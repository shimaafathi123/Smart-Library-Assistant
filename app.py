import streamlit as st
import pandas as pd

st.set_page_config(page_title="المساعد الذكي", page_icon="🎓", layout="centered")

st.markdown("""
    <style>
    /* إلغاء المسافات البيضاء في أعلى الصفحة */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 0rem !important;
    }
    
    /* إخفاء أيقونات الشات (User and Assistant Icons) */
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] {
        display: none !important;
    }
    
    /* تعديل إزاحة الرسالة بعد إخفاء الأيقونة لتأخذ المساحة كاملة */
    [data-testid="stChatMessageContent"] {
        margin-left: 0 !important;
        padding-left: 0 !important;
    }

    /* تنسيق الهيدر (اللوجو والعنوان) */
    .header-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .welcome-text {
        font-weight: 800;
        color: #111827;
        font-size: 2.2rem;
        margin-top: 10px;
        font-family: 'Segoe UI', sans-serif;
    }

    /* ستايل شات جي بي تي للرسائل */
    .stChatMessage {
        padding: 1.5rem !important;
        border-bottom: 1px solid #ececf1 !important;
        background-color: transparent !important;
    }
    
    .stChatMessage[data-testimonial="assistant"] {
        background-color: #f7f7f8 !important;
    }

    .stMarkdown p {
        font-size: 1.1rem !important;
        line-height: 1.7 !important;
        color: #374151 !important;
    }

    /* إخفاء عناصر Streamlit غير الضرورية */
    #MainMenu, footer, header {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.markdown('<div class="header-wrapper">', unsafe_allow_html=True)
try:
    st.image("logo.png", width=100)
except:
    pass
st.markdown('<p class="welcome-text">أهلاً بك في مكتبة الكلية</p>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        df_books = pd.read_excel("Library_DB.xlsx", sheet_name="Books")
        df_faq = pd.read_excel("Library_DB.xlsx", sheet_name="FAQ")
        return df_books.fillna(""), df_faq.fillna("")
    except:
        return pd.DataFrame(), pd.DataFrame()

df_books, df_faq = load_data()

# --- 5. منطق الرد ---
def local_ai_logic(user_input):
    clean_input = user_input.strip().lower()
    
    if any(word in clean_input for word in ["استعارة", "استلاف", "استلف"]):
        return "ℹ️ **خدمة الاستعارة:**\n\nخدمة الاستعارة داخل المكتبة متاحة فقط لأعضاء هيئة التدريس. ويتم استعراض المواد المتاحة من خلال التوجه إلى المكتبة، كما يتم تسجيل الاستعارة من داخل المكتبة فقط."

    if any(word in clean_input for word in ["كل الكتب", "عرض الكل", "المكتبة فيها إيه"]):
        if not df_books.empty:
            res = f"📚 **قائمة الكتب المتاحة ({len(df_books)} كتاب):**\n\n"
            for i, row in df_books.iterrows():
                res += f"{i+1}. **{row['العنوان']}** — {row['المؤلف']}\n"
            return res
        return "⚠️ لا توجد كتب مسجلة حالياً."

    if clean_input.startswith("كتاب"):
        name = clean_input.replace("كتاب", "", 1).strip()
        match = df_books[df_books['العنوان'].astype(str).str.lower() == name]
        if not match.empty:
            b = match.iloc[0]
            return f"✅ **الكتاب متوفر!**\n\n**📘 العنوان:** {b['العنوان']}\n**👤 المؤلف:** {b['المؤلف']}\n**🏢 الناشر:** {b['الناشر']}\n**📅 التاريخ:** {b['تاريخ النشر']}"
        return f"❌ للأسف كتاب '{name}' غير موجود."

    if clean_input.startswith("المؤلف"):
        auth = clean_input.replace("المؤلف", "", 1).strip()
        matches = df_books[df_books['المؤلف'].astype(str).str.lower() == auth]
        if not matches.empty:
            res = f"👤 **كتب للمؤلف '{matches.iloc[0]['المؤلف']}':**\n\n"
            for i, row in matches.iterrows():
                res += f"- **{row['العنوان']}**\n"
            return res
        return f"❌ لم نجد كتباً للمؤلف '{auth}'."

    for _, row in df_faq.iterrows():
        keys = [k.strip().lower() for k in str(row['Keywords']).split(',')]
        if any(k in clean_input for k in keys if k):
            return row['Answer']

    return "أهلاً بك! يمكنك البحث بـ: **كتاب [الاسم]** أو **المؤلف [الاسم]** أو اكتب **كل الكتب**."

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "مرحباً بك! 👋 كيف يمكنني مساعدتك في مكتبة الكلية اليوم؟"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("اسألني عن كتاب أو مؤلف..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = local_ai_logic(prompt)
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})