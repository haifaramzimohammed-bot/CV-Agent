import os
import streamlit as st
from pypdf import PdfReader
from google import genai

st.set_page_config(page_title="وكيل تحليل السير الذاتية", layout="centered")

st.markdown("""
    <style>
    body, div, p, span, h1, h2, h3 {
        direction: rtl;
        text-align: right;
        font-family: 'Cairo', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

st.title(" وكيل تحليل ومواءمة السير الذاتية")
st.write("أداة ذكية لفحص السيرة الذاتية، تحديد نسبة التوافق، والثغرات بدقة عالية.")

API_KEY = ""

uploaded_file = st.file_uploader("اختر ملف السيرة الذاتية (PDF)", type=["pdf"])

if uploaded_file is not None:
    with open("temp_cv.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    if st.button(" ابدأ التحليل"):
        with st.spinner(" جارٍ استخلاص النتائج بدقة..."):
            try:
                reader = PdfReader("temp_cv.pdf")
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"

                # برومبت مقسم بعلامات واضحة لنستطيع فصل النتائج برمجياً
                prompt = f"""
                أنت خبير توظيف ذكي ونظام ATS محترف. قم بتحليل السيرة الذاتية التالية وأعطني النتيجة مقسمة بدقة باستخدام العلامات التالية حرفياً:

                [SCORE]
                اكتب نسبة التوافق الرقمية فقط هنا (مثال: 75% أو 20%) مع تعليق قصير جداً.

                [STRENGTHS]
                اكتب أبرز نقاط القوة في نقاط واضحة.

                [WEAKNESSES]
                اكتب الثغرات ونقاط الضعف والأخطاء التنسيقية.

                [ROLES]
                اكتب المسميات الوظيفية المناسبة.

                نص السيرة الذاتية:
                {text}
                """

                client = genai.Client(api_key=API_KEY)
                response = client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=prompt
                )

                analysis_text = response.text
                st.success("تم التحليل بنجاح!")
                st.markdown("---")
                st.markdown(" تقرير التحليل الاحترافي:")

                # تقسيم النص بناءً على العلامات لعرض كل قسم في بطاقة منفصلة ومستقلة
                try:
                    parts_score = analysis_text.split("[STRENGTHS]")[0].replace("[SCORE]", "").strip()
                    remainder = analysis_text.split("[STRENGTHS]")[1]
                    parts_strengths = remainder.split("[WEAKNESSES]")[0].strip()
                    remainder2 = remainder.split("[WEAKNESSES]")[1]
                    parts_weaknesses = remainder2.split("[ROLES]")[0].strip()
                    parts_roles = remainder2.split("[ROLES]")[1].strip()
                except Exception:
                    # خطة بديلة في حال اختلف تقسيم النموذج قليلاً
                    parts_score = "التفاصيل في الأسفل"
                    parts_strengths = analysis_text
                    parts_weaknesses = ""
                    parts_roles = ""

                # 1.  نسبة التوافق
                st.markdown(
                    f"""
                    <div style="background-color: #e8f4fd; padding: 15px; border-radius: 10px; border-right: 5px solid #2196F3; margin-bottom: 15px;">
                        <h4 style="margin: 0; color: #0d47a1;"> نسبة التوافق مع نظام الفحص الآلي (ATS Score)</h4>
                        <p style="margin: 5px 0 0 0; font-size: 16px; font-weight: bold;">{parts_score}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

               # 2.  نقاط القوه
                clean_strengths = parts_strengths.replace("**", "")
                st.markdown(
                    f"""
                    <div style="background-color: #e8f8f5; padding: 15px; border-radius: 10px; border-right: 5px solid #2ecc71; margin-bottom: 15px;">
                        <h4 style="margin: 0; color: #117a65;"> أبرز نقاط القوة</h4>
                        <p style="margin: 5px 0 0 0; white-space: pre-line;">{clean_strengths}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # 3. الثغرات ونقاط الضعف
                clean_weaknesses = parts_weaknesses.replace("**", "")
                st.markdown(
                    f"""
                    <div style="background-color: #fef9e7; padding: 15px; border-radius: 10px; border-right: 5px solid #f1c40f; margin-bottom: 15px;">
                        <h4 style="margin: 0; color: #7d6608;"> الثغرات ونقاط الضعف والتنسيق</h4>
                        <p style="margin: 5px 0 0 0; white-space: pre-line;">{clean_weaknesses}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # 4.المسميات الوظيفية
                st.markdown(
                    f"""
                    <div style="background-color: #f4ecf7; padding: 15px; border-radius: 10px; border-right: 5px solid #8e44ad; margin-bottom: 15px;">
                        <h4 style="margin: 0; color: #512e5f;"> المسميات الوظيفية المناسبة</h4>
                        <p style="margin: 5px 0 0 0; white-space: pre-line;">{parts_roles}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # زر تحميل 
                st.download_button(
                    label=" تحميل التقرير الكامل (TXT)",
                    data=analysis_text,
                    file_name="ATS_Analysis_Report.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error(f"حدث خطأ: {e}")