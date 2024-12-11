import logging
import requests
import csv
import random
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import asyncio

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

# Trạng thái toàn cục cho người dùng
user_states = {}

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

# Hàm xử lý khi người dùng nhập /start
def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    # Đặt trạng thái ban đầu cho người dùng
    user_states[chat_id] = {"score": 0, "question_index": 0, "questions": fetch_questions_from_csv()}
    welcome_message = (
        "🎉 <b>Chào mừng bạn đến với Gameshow 'Ai Là Nhà Đầu Tư Tài Ba'!</b>\n\n"
        "📋 <b>Luật chơi:</b>\n"
        "- Có 20 câu hỏi với tổng số điểm tối đa là 20.\n"
        "- Mỗi câu trả lời đúng được 1 điểm.\n"
        "- Nếu không trả lời trong 60 giây, bạn sẽ bị tính 0 điểm cho câu đó.\n\n"
        "✨ <b>Mục tiêu của bạn:</b>\n"
        "- Trên 15 điểm: Nhà đầu tư thiên tài.\n"
        "- Từ 10 đến 15 điểm: Nhà đầu tư tiềm năng.\n"
        "- Dưới 10 điểm: Cần học hỏi thêm!\n\n"
        "👉 Nhấn /quiz để bắt đầu!"
    )
    update.message.reply_text(text=welcome_message, parse_mode=ParseMode.HTML)

# Hàm xử lý khi người dùng nhập /quiz
def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    user_state = user_states.get(chat_id)

    if not user_state or not user_state["questions"]:
        update.message.reply_text("❌ Không có câu hỏi. Vui lòng thử lại sau.")
        return

    # Lấy câu hỏi tiếp theo
    question_index = user_state["question_index"]
    if question_index >= 20:
        # Kết thúc quiz
        total_score = user_state["score"]
        result_message = (
            f"🏆 Kết thúc game! Tổng điểm của bạn: {total_score}/20\n\n"
            "✨ <b>Kết quả:</b>\n"
            f"{'🥇 Nhà đầu tư thiên tài!' if total_score > 15 else ''}"
            f"{'🥈 Nhà đầu tư tiềm năng!' if 10 <= total_score <= 15 else ''}"
            f"{'🥉 Cần học hỏi thêm!' if total_score < 10 else ''}"
        )
        update.message.reply_text(text=result_message, parse_mode=ParseMode.HTML)
        return

    question_data = user_state["questions"][question_index]
    question = question_data["Question"]
    options = [
        InlineKeyboardButton(question_data["Option 1"], callback_data="1"),
        InlineKeyboardButton(question_data["Option 2"], callback_data="2"),
        InlineKeyboardButton(question_data["Option 3"], callback_data="3"),
    ]
    correct_answer = question_data["Answer"]

    # Lưu câu trả lời đúng
    context.user_data["correct_answer"] = correct_answer
    user_state["question_index"] += 1

    reply_markup = InlineKeyboardMarkup([options])
    update.message.reply_text(
        text=f"💬 Câu {question_index + 1}: {question}",
        reply_markup=reply_markup,
    )

# Hàm xử lý trả lời câu hỏi
def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    chat_id = query.message.chat_id
    user_state = user_states.get(chat_id)

    if not user_state:
        query.answer("❌ Không có bài quiz đang hoạt động.")
        return

    correct_answer = context.user_data.get("correct_answer")
    if query.data == correct_answer:
        user_state["score"] += 1
        query.answer("👍 Chính xác!")
    else:
        query.answer(f"😥 Sai rồi! Đáp án đúng: {correct_answer}")

    # Hiển thị câu hỏi tiếp theo
    quiz(query.message, context)

# Hàm chính để chạy bot
def run_bot():
    application = Application.builder().token(TOKEN).build()

    # Thêm các handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CallbackQueryHandler(handle_answer))

    logger.info("Bot đang chạy...")
    application.run_polling()

if __name__ == "__main__":
    run_bot()
