import logging
import pandas as pd
import random
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Bot Constants
TOKEN = "7014456931:AAE5R6M9wgfMMyXPYCdogRTISwbaUjSXQRo"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1QMKiohAaO5QtHoQwBX5efTXCI_Q791A4GnoCe9nMV2w/export?format=csv&sheet=TTCK"

# Logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Questions
def load_questions():
    try:
        data = pd.read_csv(SHEET_URL)
        questions = data.to_dict(orient="records")
        random.shuffle(questions)
        return questions[:20]
    except Exception as e:
        logger.error(f"Error loading questions: {e}")
        return []

# Start Command
def start(update: Update, context: CallbackContext):
    context.user_data["questions"] = load_questions()
    context.user_data["current_question"] = 0
    context.user_data["score"] = 0

    if not context.user_data["questions"]:
        update.message.reply_text("⚠️ Không thể tải câu hỏi. Vui lòng thử lại sau.")
        return

    update.message.reply_text(
        "🎉 Chào mừng bạn đến với Gameshow 'Ai Là Thiên Tài Đầu Tư’'!\n\n"
        "📜 *Luật chơi:*\n"
        "- Có 20 câu hỏi.\n"
        "- Mỗi câu trả lời đúng được 1 điểm.\n"
        "- Nếu không trả lời trong 60 giây, bạn sẽ bị tính 0 điểm.\n\n"
        "🔥 Bạn đã sẵn sàng? Nhấn /quiz để bắt đầu trả lời các câu hỏi!"
    )

# Quiz Command (giống hàm start)
def quiz(update: Update, context: CallbackContext):
    context.user_data["questions"] = load_questions()
    context.user_data["current_question"] = 0
    context.user_data["score"] = 0

    if not context.user_data["questions"]:
        update.message.reply_text("⚠️ Không thể tải câu hỏi. Vui lòng thử lại sau.")
        return

    ask_question(update, context)

# Ask Next Question
def ask_question(update: Update, context: CallbackContext):
    user_data = context.user_data
    current = user_data["current_question"]
    questions = user_data["questions"]

    if current < len(questions):
        question = questions[current]
        options = [question["Option 1"], question["Option 2"], question["Option 3"]]
        user_data["current_question"] += 1

        reply_markup = ReplyKeyboardMarkup([[1, 2, 3]], one_time_keyboard=True)
        update.message.reply_text(
            f"💬 Câu {current + 1}: {question['Question']}\n\n"
            f"1️⃣ {options[0]}\n"
            f"2️⃣ {options[1]}\n"
            f"3️⃣ {options[2]}",
            reply_markup=reply_markup,
        )
    else:
        finish_quiz(update, context)

# Finish Quiz
def finish_quiz(update: Update, context: CallbackContext):
    user_data = context.user_data
    score = user_data.get("score", 0)

    if score >= 15:
        result = "🥇 Nhà đầu tư thiên tài!"
    elif 12 <= score < 15:
        result = "🥈 Nhà đầu tư tiềm năng!"
    else:
        result = "🥉 Thế giới rất rộng lớn và còn nhiều thứ phải học thêm."

    update.message.reply_text(
        f"🎉 *Chúc mừng bạn đã hoàn thành cuộc thi 'Ai Là Thiên Tài Đầu Tư’'!*\n\n"
        f"🏆 *Tổng điểm của bạn:* {score}/20.\n{result}"
    )

# Main Function
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("quiz", quiz))
    dp.add_handler(MessageHandler(Filters.regex("^[1-3]$"), handle_answer))

    updater.start_polling()
    updater.idle()

# Handle Answer
def handle_answer(update: Update, context: CallbackContext):
    user_data = context.user_data
    current = user_data["current_question"] - 1
    questions = user_data["questions"]

    try:
        user_answer = int(update.message.text)
    except ValueError:
        update.message.reply_text("⚠️ Vui lòng chọn 1, 2 hoặc 3.")
        return

    correct_answer = int(questions[current]["Answer"])

    if user_answer == correct_answer:
        user_data["score"] += 1
        update.message.reply_text(f"👍 Chính xác! Tổng điểm của bạn hiện tại là {user_data['score']}/20.")
    else:
        update.message.reply_text(
            f"😥 Sai rồi! Đáp án đúng là {correct_answer}. "
            f"Tổng điểm hiện tại của bạn là {user_data['score']}/20."
        )

    ask_question(update, context)

if __name__ == "__main__":
    main()
