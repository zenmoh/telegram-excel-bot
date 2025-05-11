import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# تحميل ملف Excel المحلي (تأكد أنه في نفس المجلد)
df = pd.read_excel("GridView.xlsx")
df = df.fillna("").astype(str)

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

app = ApplicationBuilder().token("7857924864:AAEP9mu5vqHjKtIePowaOUkddDAfFZn8b1s").build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.run_polling()
