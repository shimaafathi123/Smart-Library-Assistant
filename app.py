import streamlit as st
import pandas as pd
from google import genai  # المكتبة الجديدة

# --- 1. إعدادات الصفحة ---
st.set_page_config(page_title="المساعد الذكي", page_icon="🎓", layout="centered")

# --- 2. إعداد الـ API (النسخة الجديدة) ---
# ملحوظة: تأكدي من تثبيت المكتبة عبر: pip install google-genai
API_KEY = "AIzaSyAYpYWiGMc_0bxo1ePR8NSGkHWAxRLQ6ik"
client = genai.Client(api_key=API_KEY)

# --- 3. CSS لشكل ChatGPT وإخفاء الأيقونات ---
st.markdown("""
    <style>
    .block-container { padding-top: 2rem !important; }
    [data-testid="stChatMessageAvatarUser"], [data-testid="stChatMessageAvatarAssistant"] { display: none !important; }
    [data-testid="stChatMessageContent"] { margin-left: 0 !important; padding-left: 0 !important; }
    .header-wrapper { display: flex; flex-direction: column; align-items: center; text-align: center; margin-bottom: 2rem; }
    .welcome-text { font-weight: 800; color: #111827; font-size: 2.2rem; margin-top: 10px; font-family: 'Segoe UI', sans-serif; }
    .stChatMessage { padding: 1.5rem !important; border-bottom: 1px solid #ececf1 !important; background-color: transparent !important; }
    .stChatMessage[data-testimonial="assistant"] { background-color: #f7f7f8 !important; }
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- 4. الهيدر (اللوجو والعنوان) ---
st.markdown('<div class="header-wrapper">', unsafe_allow_html=True)
try: st.image("logo.png", width=100)
except: pass
st.markdown('<p class="welcome-text">أهلاً بك في مكتبة الكلية</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- 5. تحميل البيانات من الإكسيل ---
@st.cache_data
def load_data_as_context():
    try:
        df_books = pd.read_excel("Library_DB.xlsx", sheet_name="Books")
        df_faq = pd.read_excel("Library_DB.xlsx", sheet_name="FAQ")
        books_info = df_books.to_string(index=False)
        faq_info = df_faq.to_string(index=False)
        return books_info, faq_info
    except:
        return "", ""

books_context, faq_context = load_data_as_context()

# --- 6. واجهة الشات ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "مرحباً بك! 👋 أنا مساعدك الذكي المدعوم بالذكاء الاصطناعي. اسألني عن أي كتاب أو استفسار يخص المكتبة."}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 7. منطق الذكاء الاصطناعي (API Logic المحدث) ---
if prompt := st.chat_input("كيف يمكنني مساعدتك اليوم؟"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        system_prompt = f"""
        أنت مساعد ذكي لمكتبة الكلية. وظيفتك الإجابة على أسئلة المستخدم بناءً على البيانات التالية فقط:
        
        بيانات الكتب المتاحة:
        {books_context}
        
        الأسئلة الشائعة والقوانين:
        {faq_context}
        
        قواعد هامة:
        1. إذا سأل عن الاستعارة، أخبره أنها لأعضاء هيئة التدريس فقط وحضورياً.
        2. إذا سأل عن كتاب، ابحث في البيانات وأعطه تفاصيله (العنوان، المؤلف، الناشر، إلخ).
        3. أجب دائماً باللغة العربية بأسلوب مهذب.
        4. إذا لم تجد المعلومة، اقترح مراجعة موظف المكتبة.
        """
        
        try:
            # استخدام الطريقة الجديدة لاستدعاء الموديل
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=f"{system_prompt}\n\nسؤال المستخدم: {prompt}"
            )
            
            ai_response = response.text
            st.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
        except Exception as e:
            st.error(f"حدث خطأ في الاتصال: {e}")