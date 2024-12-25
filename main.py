import logging
import pandas as pd
import random
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Updater, CommandHandler, MessageHandler, Filters, CallbackContext
)

# Bot Constants
TOKEN = "7014456931:AAE5R6M9wgfMMyXPYCdogRTISwbaUjSXQRo"
SHEET_URL = "https://docs.google.com/spreadsheets/d/1QMKiohAaO5QtHoQwBX5efTXCI_Q791A4GnoCe9nMV2w/export?format=csv&gid=0"

# Logging
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Hỗ trợ tải câu hỏi ---
def load_questions():
    try:
        data = pd.read_csv(SHEET_URL)
        questions = data.to_dict(orient="records")
        valid_questions = []
        for q in questions:
            if all(k in q for k in ["Question", "Option 1", "Option 2", "Option 3", "Answer"]) and q["Answer"] in [1, 2, 3]:
                valid_questions.append(q)
        random.shuffle(valid_questions)
        return valid_questions[:20]
    except Exception as e:
        logger.error(f"Error loading questions: {e}")
        return []

# --- Lệnh /start ---
def start(update: Update, context: CallbackContext):
    context.user_data.clear()
    context.user_data["questions"] = load_questions()
    context.user_data["current_question"] = 0
    context.user_data["score"] = 0

    if not context.user_data["questions"]:
        update.message.reply_text("⚠️ Không thể tải câu hỏi. Vui lòng thử lại sau.")
        return

    update.message.reply_text(
        "🎉 Chào mừng bạn đến với Gameshow 'Thiên Tài Đầu Tư'!\n\n"
        "📜 *Luật chơi:*\n"
        "- Có 20 câu hỏi.\n"
        "- Mỗi câu trả lời đúng được 1 điểm.\n"
        "- Nếu không trả lời trong 60 giây, bạn sẽ bị tính 0 điểm.\n\n"
        "🔥 Nhấn /quiz để bắt đầu trả lời các câu hỏi!",
        parse_mode="Markdown"
    )

# --- Lệnh /quiz ---
def quiz(update: Update, context: CallbackContext):
    if not context.user_data.get("questions"):
        update.message.reply_text("⚠️ Không thể tải câu hỏi. Vui lòng thử lại sau.")
        return

    context.user_data["current_question"] = 0
    context.user_data["score"] = 0
    ask_question(update, context)

# --- Hiển thị câu hỏi ---
def ask_question(update: Update, context: CallbackContext):
    current = context.user_data["current_question"]
    questions = context.user_data["questions"]

    if current < len(questions):
        question = questions[current]
        context.user_data["current_question"] += 1

        options = [question["Option 1"], question["Option 2"], question["Option 3"]]
        reply_markup = ReplyKeyboardMarkup([[1, 2, 3]], one_time_keyboard=True)

        update.message.reply_text(
            f"💬 *Câu {current + 1}:* {question['Question']}\n\n"
            f"1️⃣ {options[0]}\n"
            f"2️⃣ {options[1]}\n"
            f"3️⃣ {options[2]}",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    else:
        finish_quiz(update, context)

# --- Xử lý câu trả lời ---
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
        update.message.reply_text(f"✅ Chính xác! Tổng điểm hiện tại: {user_data['score']}/20.")
    else:
        update.message.reply_text(
            f"❌ Sai rồi! Đáp án đúng là {correct_answer}.\n"
            f"🏆 Tổng điểm hiện tại: {user_data['score']}/20."
        )

    ask_question(update, context)

# --- Hoàn thành quiz ---
def finish_quiz(update: Update, context: CallbackContext):
    score = context.user_data.get("score", 0)

    if score >= 15:
        result = "🥇 Bạn đúng là Thiên tài Đầu tư!"
    elif 12 <= score < 15:
        result = "🥈 Nhà đầu tư tiềm năng!"
    else:
        result = "🥉 Hãy học hỏi thêm để thành công hơn."

    update.message.reply_text(
        f"🎉 *Chúc mừng bạn đã hoàn thành Gameshow 'Thiên Tài Đầu Tư'!*\n\n"
        f"🏆 *Tổng điểm:* {score}/20.\n{result}",
        parse_mode="Markdown"
    )

# --- Chạy bot ---
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("quiz", quiz))
    dp.add_handler(MessageHandler(Filters.regex("^[1-3]$"), handle_answer))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
