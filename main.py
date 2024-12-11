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

# Global variables to manage quiz state
quiz_data = {}
user_scores = {}

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

# Hàm xử lý khi người dùng mở bot
def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    update.message.reply_text(
        text="🔥 Bạn đã sẵn sàng tham gia tìm kiếm 'Ai là thiên tài đầu tư?' Bấm /start để bắt đầu.",
        parse_mode=ParseMode.HTML,
    )

# Hàm xử lý khi người dùng nhập /start
def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    # Initialize user state
    user_scores[chat_id] = {"score": 0, "current_question": 0}
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
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    user_state = user_scores.get(chat_id, {"score": 0, "current_question": 0})
    
    # Load quiz questions
    if "questions" not in quiz_data:
        quiz_data["questions"] = fetch_questions_from_csv()

    questions = quiz_data["questions"]
    if not questions:
        await update.message.reply_text("❌ Lỗi: Không thể tải câu hỏi. Vui lòng thử lại sau.")
        return

    if user_state["current_question"] >= 20:
        await update.message.reply_text(
            "🏁 Bạn đã hoàn thành tất cả các câu hỏi! Nhấn /start để chơi lại."
        )
        return

    # Get next question
    question_data = random.choice(questions)
    question_text = question_data["Question"]
    options = [
        InlineKeyboardButton(question_data["Option 1"], callback_data="1"),
        InlineKeyboardButton(question_data["Option 2"], callback_data="2"),
        InlineKeyboardButton(question_data["Option 3"], callback_data="3"),
    ]
    correct_answer = str(question_data["Answer"])

    # Save correct answer to state
    user_state["current_question"] += 1
    user_scores[chat_id] = user_state
    context.user_data["correct_answer"] = correct_answer

    # Send question
    reply_markup = InlineKeyboardMarkup([options])
    await update.message.reply_text(
        text=f"💬 Câu {user_state['current_question']}: {question_text}",
        reply_markup=reply_markup,
    )

# Hàm xử lý trả lời câu hỏi
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    chat_id = query.message.chat.id
    user_state = user_scores.get(chat_id)

    if not user_state:
        await query.answer("❌ Không có bài quiz đang hoạt động. Nhấn /quiz để bắt đầu!")
        return

    correct_answer = context.user_data.get("correct_answer")
    if query.data == correct_answer:
        user_state["score"] += 1
        await query.answer("👍 Chính xác!", show_alert=True)
    else:
        await query.answer("😥 Sai rồi!", show_alert=True)

    # Check if quiz is over
    if user_state["current_question"] >= 20:
        total_score = user_state["score"]
        result_message = (
            f"🏆 Kết thúc game! Tổng điểm của bạn: {total_score}/20\n\n"
            "✨ <b>Kết quả:</b>\n"
            f"{'🥇 Nhà đầu tư thiên tài!' if total_score > 15 else ''}"
            f"{'🥈 Nhà đầu tư tiềm năng!' if 10 <= total_score <= 15 else ''}"
            f"{'🥉 Cần học hỏi thêm!' if total_score < 10 else ''}"
        )
        await query.message.reply_text(text=result_message, parse_mode=ParseMode.HTML)
    else:
        # Load next question
        await quiz(update, context)

# Hàm chính để chạy bot
def run_bot():
    application = Application.builder().token(TOKEN).build()

    # Thêm các handler
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CallbackQueryHandler(handle_answer))

    # Chạy bot
    logger.info("Bot đang chạy...")
    application.run_polling()

if __name__ == "__main__":
    run_bot()
