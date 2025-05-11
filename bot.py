import streamlit as st
import pandas as pd
import os
import asyncio
import threading
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
import nest_asyncio

nest_asyncio.apply()  # ✅ الحل السحري لتجنب الخطأ

# تحميل متغيرات البيئة
load_dotenv()
TOKEN = os.getenv("TELEGRAM_API_TOKEN")

# تحميل ملف Excel
EXCEL_FILE = "GridView.xlsx"
if not os.path.exists(EXCEL_FILE):
    st.error(f"❌ لم يتم العثور على الملف: {EXCEL_FILE}")
    st.stop()

df = pd.read_excel(EXCEL_FILE).fillna("").astype(str)

def format_row(row):
    return "\n".join([f"{col}: {row[col]}" for col in df.columns])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    matches = df[df['الاسم'].str.contains(user_input, case=False, na=False)]

    if not matches.empty:
        responses = [format_row(row) for _, row in matches.iterrows()]
        full_response = "\n\n---\n\n".join(responses)
        if len(full_response) > 4000:
            full_response = full_response[:4000] + "\n\n(تم تقليص النتائج بسبب الحجم)"
    else:
        full_response = "عذرًا، لم يتم العثور على هذا الاسم في قاعدة البيانات."

    await update.message.reply_text(full_response)

# ✅ تشغيل البوت داخل حلقة الحدث الحالية (بدون أخطاء)
async def start_bot_async():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await app.run_polling()

def start_bot():
    loop = asyncio.get_event_loop()
    if not loop.is_running():
        loop.run_until_complete(start_bot_async())
    else:
        asyncio.ensure_future(start_bot_async())

# واجهة Streamlit
st.set_page_config(page_title="مشغل بوت تيليغرام", layout="centered")
st.title("🤖 مشغل بوت تيليغرام")
st.markdown("اضغط على الزر لتشغيل البوت:")

if st.button("🚀 تشغيل البوت"):
    try:
        start_bot()
        st.success("✅ تم تشغيل البوت في الخلفية. يمكنك الآن إرسال رسالة إلى البوت.")
    except Exception as e:
        st.error(f"حدث خطأ أثناء التشغيل: {e}")
