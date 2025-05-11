import os
import pandas as pd
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
import nest_asyncio

# إعداد بيئة async للعمل في السيرفرات
nest_asyncio.apply()

# تحميل متغيرات البيئة من ملف .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_API_TOKEN")

# تحميل ملف Excel
EXCEL_FILE = "GridView.xlsx"
if not os.path.exists(EXCEL_FILE):
    raise FileNotFoundError(f"❌ لم يتم العثور على الملف: {EXCEL_FILE}")

# قراءة البيانات من الملف
df = pd.read_excel(EXCEL_FILE).fillna("").astype(str)

# تنسيق الردود
def format_row(row):
    return "\n".join([f"{col}: {row[col]}" for col in df.columns])

# التعامل مع الرسائل الواردة
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

# تشغيل البوت
async def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
