import streamlit as st
from google import genai
import pandas as pd

# --- إعدادات الصفحة ---
st.set_page_config(page_title="المساعد الذكي", page_icon="🎓")
st.title("📚 مساعد المكتبة الذكي")

# --- 1. إدخال الـ API Key ---
with st.sidebar:
    user_api_key = st.text_input("إعدادات الاتصال (API Key):", 
                                value="AIzaSyCwrLJeKnX6oUmGsF8uHTIZJw-kYNLCK0k", 
                                type="password")
    st.info("نظام ذكي - نسخة 2026 🚀")

# --- 2. تحميل البيانات ---
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("Library_DB.xlsx")
        return df.to_dict(orient='records')
    except Exception as e:
        st.error(f"ملف البيانات غير موجود: {e}")
        return []

books_data = load_data()

# --- 3. واجهة الشات ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. منطق المحادثة مع معالجة الازدحام ---
if prompt := st.chat_input("كيف يمكنني مساعدتك؟"):
    if not user_api_key:
        st.error("رجاءً أدخل الـ API Key أولاً.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                client = genai.Client(api_key=user_api_key)
                context_info = str(books_data)
                
                system_instruction = (
                    "أنت ذكاء اصطناعي مساعد لمكتبة أكاديمية.\n"
                    f"استخدم البيانات التالية فقط للإجابة: {context_info}\n"
                    "أجب باختصار ومهنية وباللغة العربية."
                )

                # محاولة طلب الرد
                try:
                    # جرب الموديل الأساسي (2.5)
                    response = client.models.generate_content(
                        model="gemini-2.5-flash", 
                        contents=f"{system_instruction}\n\nسؤال المستخدم: {prompt}"
                    )
                except Exception as e_inner:
                    # لو السيرفر مشغول (503)، حول فوراً للموديل الأكثر استقراراً (1.5)
                    st.warning("السيرفر الرئيسي مزدحم، يتم التحويل للمحرك البديل...")
                    response = client.models.generate_content(
                        model="gemini-2.5-flash", 
                        contents=f"{system_instruction}\n\nسؤال المستخدم: {prompt}"
                    )
                
                if response.text:
                    st.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
            except Exception as e:
                st.error(f"عذراً، المحرك حالياً غير متاح. يرجى المحاولة بعد قليل. ({e})")