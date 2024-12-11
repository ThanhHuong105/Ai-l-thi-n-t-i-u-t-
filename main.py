from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import logging
import csv
import random
import requests

# Token bot Telegram
TOKEN = "7014456931:AAE5R6M9wgfMMyXPYCdogRTISwbaUjSXQRo"

# URL Google Sheets CSV
SHEET_ID = "1QMKiohAaO5QtHoQwBX5efTXCI_Q791A4GnoCe9nMV2w"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&sheet=TTCK"

# Cấu hình logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Biến toàn cục
questions = []
user_scores = {}
current_questions = {}

# Tải câu hỏi từ Google Sheets
def fetch_questions_from_csv():
    try:
        response = requests.get(SHEET_URL)
        response.raise_for_status()
        decoded_content = response.content.decode("utf-8")
        csv_reader = csv.DictReader(decoded_content.splitlines())
        return [row for row in csv_reader]
    except Exception as e:
        logger.error(f"Error loading questions: {e}")
        return []

# Hàm xử lý khi người dùng nhập /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_scores[user_id] = 0
    current_questions[user_id] = iter(random.sample(questions, len(questions)))

    welcome_message = (
        "🎉 <b>Chào mừng bạn đến với Gameshow 'Ai Là Nhà Đầu Tư Tài Ba'!</b>\n\n"
        "📋 <b>Luật chơi:</b>\n"
        "- Có 20 câu hỏi.\n"
        "- Mỗi câu trả lời đúng được 1 điểm.\n"
        "- Nếu không trả lời trong 60 giây, bạn sẽ bị tính 0 điểm.\n\n"
        "👉 Nhấn /quiz để bắt đầu!"
    )
    await update.message.reply_text(welcome_message, parse_mode="HTML")

# Hàm bắt đầu quiz
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        question_data = next(current_questions[user_id])
        options = [
            InlineKeyboardButton(question_data["Option 1"], callback_data="1"),
            InlineKeyboardButton(question_data["Option 2"], callback_data="2"),
            InlineKeyboardButton(question_data["Option 3"], callback_data="3"),
        ]
        reply_markup = InlineKeyboardMarkup.from_column(options)
        await update.message.reply_text(
            text=f"💬 {question_data['Question']}", reply_markup=reply_markup
        )
        context.user_data["current_question"] = question_data
    except StopIteration:
        total_score = user_scores[user_id]
        result_message = (
            f"🏆 Kết thúc game! Tổng điểm của bạn: {total_score}/20\n\n"
            "✨ <b>Kết quả:</b>\n"
            f"{'🥇 Nhà đầu tư thiên tài!' if total_score > 15 else ''}"
            f"{'🥈 Nhà đầu tư tiềm năng!' if 10 <= total_score <= 15 else ''}"
            f"{'🥉 Cần học hỏi thêm!' if total_score < 10 else ''}"
        )
        await update.message.reply_text(result_message, parse_mode="HTML")

# Hàm xử lý phản hồi từ người dùng
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    question_data = context.user_data.get("current_question")
    correct_answer = question_data["Answer"]
    user_answer = query.data

    if user_answer == correct_answer:
        user_scores[user_id] += 1
        await query.edit_message_text("👍 Chính xác!")
    else:
        await query.edit_message_text(
            f"😥 Sai rồi! Đáp án đúng là: {question_data[f'Option {correct_answer}']}"
        )

    # Gửi câu hỏi tiếp theo
    await quiz(update, context)

# Chạy bot
def main():
    global questions
    questions = fetch_questions_from_csv()

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CallbackQueryHandler(handle_answer))

    application.run_polling()

if __name__ == "__main__":
    main()
