import streamlit as st
from google import genai
import pandas as pd

# --- إعدادات الصفحة ---
st.set_page_config(page_title="المساعد الذكي - حاسبات ", page_icon="🎓")
st.title("📚 مساعد مكتبة كلية الحاسبات والذكاء الاصطناعي")
st.markdown("##### جامعة  - نظام المساعدة الذكي لأعضاء هيئة التدريس")

# --- 1. إدخال الـ API Key ---
with st.sidebar:
    st.image("https://bu.edu.eg/images/logo_fci.png", width=100) # اختياري: إضافة لوجو الكلية لو متاح
    user_api_key = st.text_input("إعدادات الاتصال (API Key):", 
                                value="AIzaSyA7aIoqgpJo4eh2LNlSZKLCwfgUVHR1CVA", 
                                type="password")
    st.divider()
    st.info("نظام مدعوم بـ Gemini 2.5 🚀")

# --- 2. تحميل البيانات ---
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("Library_DB.xlsx")
        return df.to_dict(orient='records')
    except Exception as e:
        st.error(f"ملف Library_DB.xlsx غير موجود: {e}")
        return []

books_data = load_data()

# --- 3. واجهة الشات ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. منطق المحادثة ---
if prompt := st.chat_input("كيف يمكنني مساعدتك يا دكتور؟"):
    if not user_api_key:
        st.error("رجاءً أدخل الـ API Key أولاً.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                client = genai.Client(api_key=user_api_key)
                
                # تحويل البيانات لنص منظم ليفهمه الـ AI بشكل أفضل
                context_info = str(books_data)
                
                # إرشادات النظام المطورة
                system_instruction = (
                    "أنت ذكاء  متطور مخصص للعمل كمساعد ذكي لمكتبة كلية = والذكاء الاصطناعي . "
                    "مهمتك هي مساعدة الدكاترة والباحثين في العثور على الكتب والمعلومات.\n\n"
                    "قواعد العمل:\n"
                    "1. استخدم البيانات المرفقة فقط للإجابة: " + context_info + "\n"
                    "2. تحدث بلهجة مهنية ولبقة تليق بالحرم الجامعي.\n"
                    "3. إذا طلب المستخدم كتاباً غير موجود، اقترح عليه أقرب تخصص متاح في البيانات.\n"
                    "4. إذا كانت البيانات تحتوي على مواعيد إرجاع أو أماكن أرفف، اذكرها بوضوح.\n"
                    "5. عرف نفسك دائماً (عند الحاجة) بأنك 'المساعد الذكي لمكتبة  '."
                )

                response = client.models.generate_content(
                    model="gemini-2.5-flash", 
                    contents=f"{system_instruction}\n\nسؤال المستخدم: {prompt}"
                )
                
                if response.text:
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
            except Exception as e:
                st.error(f"عذراً، حدث خطأ تقني: {e}")