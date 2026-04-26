import streamlit as st
import pandas as pd

# --- إعدادات الصفحة ---
st.set_page_config(page_title="مساعد مكتبة الحاسبات", page_icon="📚")
st.title("📚 مساعد مكتبة كلية الحاسبات والذكاء الاصطناعي")

# --- 1. تحميل البيانات ---
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("Library_DB.xlsx")
        # تنظيف البيانات لضمان دقة البحث
        df.columns = [c.strip() for c in df.columns] 
        return df.fillna("غير متوفر")
    except Exception as e:
        st.error(f"ملف Library_DB.xlsx غير موجود: {e}")
        return pd.DataFrame()

df_books = load_data()

# --- 2. واجهة المحادثة ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 3. منطق الرد (بدون API Key) ---
if prompt := st.chat_input("كيف يمكنني مساعدتك يا دكتور؟"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = ""
        
        # أ. الإجابة على الأسئلة العامة (مواعيد، استعارة)
        low_prompt = prompt.lower()
        if "مواعيد" in low_prompt or "وقت" in low_prompt:
            response = "🕒 **مواعيد العمل:** من الأحد إلى الخميس، من الساعة 9 صباحاً وحتى 3 عصراً."
        
        elif "استعار" in low_prompt or "آلية" in low_prompt:
            response = ("📖 **نظام الاستعارة:**\n"
                        "1. متاح الاستعارة لأعضاء هيئة التدريس والطلاب.\n"
                        "2. الحد الأقصى كتابين لمدة أسبوعين.\n"
                        "3. يتم ذلك من خلال كارنيه الكلية عبر مكتب شؤون الطلاب.")
        
        # ب. البحث عن كتاب في قاعدة البيانات
        else:
            if not df_books.empty:
                # البحث في جميع الأعمدة عن كلمات البحث
                query_words = prompt.split()
                # فلترة البيانات التي تحتوي على الكلمات المطلوبة
                results = df_books[df_books.apply(lambda row: any(word.lower() in str(row).lower() for word in query_words), axis=1)]
                
                if not results.empty:
                    response = f"✅ وجدنا {len(results)} كتاب مطابقت لبحثك:\n\n"
                    for i, row in results.head(5).iterrows(): # عرض أول 5 نتائج فقط
                        response += f"📖 **الكتاب:** {row.get('العنوان', 'غير متوفر')} | **المؤلف:** {row.get('المؤلف', 'غير متوفر')} | **الرف:** {row.get('رقم الرف', 'غير متوفر')}\n\n"
                    if len(results) > 5:
                        response += "*(هناك نتائج أخرى، يرجى تحديد البحث أكثر)*"
                else:
                    response = "❌ عذراً، هذا الكتاب غير موجود حالياً في قاعدة البيانات. يمكنك تجربة البحث بكلمة مفتاحية أخرى."
            else:
                response = "⚠️ قاعدة البيانات غير محملة، يرجى التأكد من وجود ملف Library_DB.xlsx."

        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})