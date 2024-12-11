import logging
import requests
import csv
import random
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler

# Token bot Telegram
TOKEN = "7014456931:AAE5R6M9wgfMMyXPYCdogRTISwbaUjSXQRo"

# URL Google Sheets CSV
SHEET_ID = "1QMKiohAaO5QtHoQwBX5efTXCI_Q791A4GnoCe9nMV2w"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&sheet=TTCK"

# Cấu hình logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Hàm tải câu hỏi từ Google Sheets
def fetch_questions_from_csv():
    try:
        response = requests.get(SHEET_URL)
        response.raise_for_status()
        questions = []
        decoded_content = response.content.decode("utf-8")
        csv_reader = csv.DictReader(decoded_content.splitlines())
        for row in csv_reader:
            questions.append(row)
        return questions
    except Exception as e:
        logger.error(f"Lỗi khi tải câu hỏi: {e}")
        return []

async def send_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    questions = context.user_data["questions"]
    current_question_index = context.user_data["current_question"] - 1
    question_data = questions[current_question_index]

    question = question_data["Question"]
    options = [
        InlineKeyboardButton(question_data["Option 1"], callback_data="1"),
        InlineKeyboardButton(question_data["Option 2"], callback_data="2"),
        InlineKeyboardButton(question_data["Option 3"], callback_data="3"),
    ]

    context.user_data["correct_answer"] = question_data["Answer"]

    reply_markup = InlineKeyboardMarkup.from_column(options)
    await update.message.reply_text(
        text=f"💬 Câu {context.user_data['current_question']}: {question}",
        reply_markup=reply_markup,
    )

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    user_answer = query.data
    correct_answer = context.user_data.get("correct_answer")

    if user_answer == correct_answer:
        context.user_data["total_score"] += 1
        await query.edit_message_text("👍 Chính xác!")
    else:
        await query.edit_message_text("😥 Sai rồi!")

    context.user_data["current_question"] += 1
    if context.user_data["current_question"] > 20:
        total_score = context.user_data["total_score"]
        result_message = (
            f"🏆 Kết thúc game! Tổng điểm của bạn: {total_score}/20\n\n"
            "✨ <b>Kết quả:</b>\n"
            f"{'🥇 Nhà đầu tư thiên tài!' if total_score > 15 else ''}"
            f"{'🥈 Nhà đầu tư tiềm năng!' if 10 <= total_score <= 15 else ''}"
            f"{'🥉 Cần học hỏi thêm!' if total_score < 10 else ''}"
        )
        await query.message.reply_text(text=result_message, parse_mode=ParseMode.HTML)
    else:
        await send_question(update, context)

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    questions = fetch_questions_from_csv()

    if not questions:
        await update.message.reply_text("❌ Lỗi: Không thể tải câu hỏi. Vui lòng thử lại sau.")
        return

    context.user_data["questions"] = questions
    context.user_data["current_question"] = 1
    context.user_data["total_score"] = 0

    await send_question(update, context)

def run_bot():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CallbackQueryHandler(handle_answer))
    application.run_polling()

if __name__ == "__main__":
    run_bot()
