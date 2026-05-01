import streamlit as st
import pandas as pd

# --- إعدادات الصفحة ---
st.set_page_config(page_title="المساعد الذكي المحلي", page_icon="🎓")
st.title("📚 مساعد مكتبة الحاسبات الذكي")

# --- 1. تحميل البيانات ---
@st.cache_data
def load_data():
    try:
        df_books = pd.read_excel("Library_DB.xlsx", sheet_name="Books")
        df_faq = pd.read_excel("Library_DB.xlsx", sheet_name="FAQ")
        return df_books.fillna(""), df_faq.fillna("")
    except Exception as e:
        st.error(f"تأكد من وجود ملف Library_DB.xlsx وبداخله صفحات Books و FAQ. الخطأ: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_books, df_faq = load_data()

# --- 2. محرك المنطق المخصص ---
def local_ai_logic(user_input):
    clean_input = user_input.strip().lower()
    
    # أ. الرد الخاص بالاستعارة
    borrow_keywords = ["استعارة", "استعار", "استلف", "استلاف", "استعير", "كارنيه"]
    if any(word in clean_input for word in borrow_keywords):
        return "ℹ️ **خدمة الاستعارة:**\n\nخدمة الاستعارة داخل المكتبة متاحة فقط لأعضاء هيئة التدريس. ويتم استعراض المواد المتاحة من خلال التوجه إلى المكتبة، كما يتم تسجيل الاستعارة من داخل المكتبة فقط."

    # ب. عرض كل الكتب الموجودة
    all_books_keywords = ["كل الكتب", "عرض الكل", "جميع الكتب", "المكتبة فيها إيه", "المحتويات"]
    if any(word in clean_input for word in all_books_keywords):
        if not df_books.empty:
            response = f"📚 **إليك قائمة بجميع الكتب المتاحة ({len(df_books)} كتاب):**\n\n"
            for i, row in df_books.iterrows():
                response += f"{i+1}. **{row['العنوان']}** - للمؤلف: {row['المؤلف']}\n"
            return response
        else:
            return "⚠️ المكتبة لا تحتوي على كتب مسجلة حالياً."

    # ج. البحث عن كتاب محدد (يجب أن يبدأ بكلمة "كتاب")
    elif clean_input.startswith("كتاب"):
        target_book = clean_input.replace("كتاب", "", 1).strip()
        if not df_books.empty and target_book:
            match = df_books[df_books['العنوان'].astype(str).str.lower() == target_book]
            if not match.empty:
                book_info = match.iloc[0]
                return f"✅ **نعم، الكتاب متوفر!** إليك تفاصيله:\n\n" \
                       f"📘 **العنوان:** {book_info['العنوان']}\n" \
                       f"👤 **المؤلف:** {book_info['المؤلف']}\n" \
                       f"🏢 **الناشر:** {book_info['الناشر']} | 🔢 **الطبعة:** {book_info['الطبعة']}\n" \
                       f"📅 **تاريخ النشر:** {book_info['تاريخ النشر']} | 📑 **الفئة:** {book_info['الفئة']}"
            else:
                return f"❌ للأسف، كتاب '{target_book}' غير موجود حالياً."
        else:
            return "يرجى كتابة اسم الكتاب بعد كلمة 'كتاب'."

    # د. البحث عن مؤلف (يجب أن يبدأ بكلمة "المؤلف")
    elif clean_input.startswith("المؤلف"):
        target_author = clean_input.replace("المؤلف", "", 1).strip()
        if not df_books.empty and target_author:
            author_matches = df_books[df_books['المؤلف'].astype(str).str.lower() == target_author]
            if not author_matches.empty:
                response = f"👤 **إليك جميع الكتب المتاحة للمؤلف '{author_matches.iloc[0]['المؤلف']}':**\n\n"
                for i, row in author_matches.iterrows():
                    response += f"{i+1}. **{row['العنوان']}** (طبعة: {row['الطبعة']})\n"
                return response
            else:
                return f"❌ عذراً، لم نجد أي كتب مسجلة للمؤلف '{target_author}'."
        else:
            return "يرجى كتابة اسم المؤلف بعد كلمة 'المؤلف'."

    # هـ. الردود العامة من الـ FAQ
    if not df_faq.empty:
        for _, row in df_faq.iterrows():
            keywords = [k.strip().lower() for k in str(row['Keywords']).split(',')]
            if any(key in clean_input for key in keywords if key != ""):
                return row['Answer']

    return "أهلاً بك! للبحث استخدم الصيغ التالية:\n" \
           "- **كل الكتب**: لعرض قائمة المكتبة كاملة.\n" \
           "- **كتاب [اسم الكتاب]**: للبحث عن تفاصيل كتاب.\n" \
           "- **المؤلف [اسم المؤلف]**: لعرض كتب مؤلف معين.\n" \
           "- أو اسأل عن نظام الاستعارة."

# --- 3. واجهة المحادثة ورسالة الترحيب ---
if "messages" not in st.session_state:
    # إضافة رسالة ترحيب مثبتة تظهر أول مرة فقط
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "أهلاً بك في نظام المساعد الذكي لمكتبة كلية الحاسبات! 👋\n\n"
                       "يمكنني مساعدتك في:\n"
                       "1️⃣ البحث عن **كتاب** معين وتفاصيله.\n"
                       "2️⃣ عرض كل كتب **مؤلف** محدد.\n"
                       "3️⃣ عرض **جميع الكتب** المتاحة بالمكتبة.\n"
                       "4️⃣ الإجابة على استفسارات **الاستعارة** والمواعيد.\n\n"
                       "كيف يمكنني مساعدتك اليوم؟"
        }
    ]

# عرض الرسائل المخزنة في الـ session
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. استقبال مدخلات اليوزر ---
if prompt := st.chat_input("مثال: كتاب Python Programming أو كل الكتب"):
    # عرض رسالة المستخدم
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # توليد وعرض رد البوت
    with st.chat_message("assistant"):
        response = local_ai_logic(prompt)
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})