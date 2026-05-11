import streamlit as st
import pandas as pd

# --- إعدادات الصفحة ---
st.set_page_config(page_title="مساعد مكتبة الحاسبات", page_icon="🤖")
st.title("🤖 المساعد الذكي الموحد للمكتبة")

# --- 1. تحميل البيانات من الشيت الموحد ---
@st.cache_data
def load_unified_data():
    file_path = "Library_DB.xlsx"
    try:
        # قراءة ورقة الأسئلة
        df_faq = pd.read_excel(file_path, sheet_name="FAQ")
        # قراءة ورقة الكتب
        df_books = pd.read_excel(file_path, sheet_name="Books")
        
        # تنظيف البيانات
        df_faq.columns = [str(c).strip() for c in df_faq.columns]
        df_books.columns = [str(c).strip() for c in df_books.columns]
        
        return df_faq.fillna(""), df_books.fillna("غير متوفر")
    except Exception as e:
        st.error(f"تأكد من وجود ملف {file_path} وأن أسماء الصفحات FAQ و Books صحيحة.")
        return pd.DataFrame(), pd.DataFrame()

df_faq, df_books = load_unified_data()

# --- 2. واجهة المحادثة ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 3. منطق الرد الذكي ---
if prompt := st.chat_input("تفضل بسؤالك (ترحيب، استعارة، أو بحث عن كتاب)..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = ""
        low_prompt = prompt.lower().strip()
        query_words = low_prompt.split()

        # أ. البحث في الأسئلة الشائعة والترحيب (FAQ)
        faq_match = df_faq[df_faq['Keywords'].apply(lambda k: any(w in str(k).lower() for w in query_words))]
        
        if not faq_match.empty:
            response = faq_match.iloc[0]['Answer']
        
        # ب. إذا لم يجد في الـ FAQ، يبحث في الكتب (Books)
        else:
            if not df_books.empty:
                book_results = df_books[df_books.apply(lambda row: any(w in str(row).lower() for w in query_words), axis=1)]
                
                if not book_results.empty:
                    response = f"✅ وجدنا {len(book_results)} كتاب مطابق لبحثك:\n\n"
                    for _, row in book_results.head(3).iterrows():
                        response += f"📘 **{row.get('عنوان الكتاب', 'بدون عنوان')}**\n"
                        response += f"✍️ المؤلف: {row.get('مؤلف الكتاب', 'غير معروف')} | 📅 {row.get('تاريخ النشر', '-')}\n"
                        response += "--- \n"
                else:
                    response = "عذراً يا دكتور، لم أجد إجابة أو كتاباً بهذا الاسم. هل تقصد الاستفسار عن المواعيد أو نظام الاستعارة؟"
            else:
                response = "⚠️ قاعدة بيانات الكتب غير محملة."

        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})