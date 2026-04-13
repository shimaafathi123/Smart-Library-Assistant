import streamlit as st
from google import genai
import pandas as pd

# --- إعدادات الصفحة ---
st.set_page_config(page_title="المساعد الذكي", page_icon="🎓")
st.title("📚 مساعد المكتبة الذكي")

# --- 1. إعداد الـ Client مرة واحدة فقط لزيادة السرعة ---
@st.cache_resource
def get_client(api_key):
    return genai.Client(api_key=api_key)

with st.sidebar:
    user_api_key = st.text_input("API Key:", value="AIzaSyCwrLJeKnX6oUmGsF8uHTIZJw-kYNLCK0k", type="password")
    st.info("نظام فائق السرعة ⚡")

# --- 2. تحميل البيانات (بصيغة نصية أخف) ---
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("Library_DB.xlsx")
        # تحويل البيانات لنص بسيط بيخلي الـ AI يعالجها أسرع من الـ Dictionary
        return df.to_string(index=False)
    except:
        return ""

books_context = load_data()

# --- 3. عرض تاريخ المحادثة ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. منطق المحادثة السريع (Streaming) ---
if prompt := st.chat_input("كيف يمكنني مساعدتك؟"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            client = get_client(user_api_key)
            
            # تعليمات مختصرة جداً لتقليل وقت التفكير
            sys_msg = f"أنت مساعد مكتبة. أجب باختصار من هذه البيانات فقط: {books_context}"

            # تفعيل خاصية الـ Stream
            response_stream = client.models.generate_content_stream(
                model="gemini-2.5-flash",
                contents=f"{sys_msg}\n\nسؤال المستخدم: {prompt}"
            )

            # عرض الكلام كلمة بكلمة (تأثير الكتابة اللحظية)
            full_response = ""
            placeholder = st.empty()
            
            for chunk in response_stream:
                full_response += chunk.text
                placeholder.markdown(full_response + "▌")
            
            placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

        except Exception as e:
            st.error(f"حدث خطأ: {e}")