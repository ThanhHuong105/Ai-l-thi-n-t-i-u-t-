import logging
import requests
import csv
import random
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes
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
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_message = (
        "🎉 <b>Chào mừng bạn đến với Gameshow 'Ai Là Nhà Đầu Tư Tài Ba'!</b>\n\n"
        "📋 <b>Luật chơi:</b>\n"
        "- Có 20 câu hỏi.\n"
        "- Mỗi câu trả lời đúng được 1 điểm.\n"
        "- Nếu không trả lời trong 60 giây, bạn sẽ bị tính 0 điểm.\n\n"
        "👉 Nhấn /quiz để bắt đầu!"
    )
    await update.message.reply_text(welcome_message, parse_mode="HTML")

from telegram.ext import CallbackQueryHandler

# Hàm xử lý khi người dùng trả lời câu hỏi
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # Trả lời tạm thời để loại bỏ thông báo "Loading..."

    # Lấy dữ liệu từ callback_data
    user_answer = query.data
    correct_answer = context.chat_data.get("correct_answer", "")

    # Kiểm tra câu trả lời đúng hay sai
    if user_answer == correct_answer:
        context.chat_data["total_score"] = context.chat_data.get("total_score", 0) + 1
        await query.edit_message_text("👍 Chính xác!")
    else:
        await query.edit_message_text("😥 Sai rồi!")

# Cập nhật hàm quiz để lưu câu trả lời đúng vào chat_data
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    questions = fetch_questions_from_csv()

    if not questions:
        await update.message.reply_text("❌ Lỗi: Không thể tải câu hỏi. Vui lòng thử lại sau.")
        return

    total_score = 0
    for i in range(1, 21):  # Lặp qua 20 câu hỏi
        question_data = random.choice(questions)
        question = question_data["Question"]
        options = [
            InlineKeyboardButton(question_data["Option 1"], callback_data="1"),
            InlineKeyboardButton(question_data["Option 2"], callback_data="2"),
            InlineKeyboardButton(question_data["Option 3"], callback_data="3"),
        ]
        correct_answer = str(question_data["Answer"])

        # Lưu câu trả lời đúng vào chat_data
        context.chat_data["correct_answer"] = correct_answer

        # Gửi câu hỏi
        reply_markup = InlineKeyboardMarkup.from_column(options)
        await update.message.reply_text(
            text=f"💬 Câu {i}: {question}", reply_markup=reply_markup
        )

    # Kết thúc game
    total_score = context.chat_data.get("total_score", 0)
    result_message = (
        f"🏆 Kết thúc game! Tổng điểm của bạn: {total_score}/20\n\n"
        "✨ <b>Kết quả:</b>\n"
        f"{'🥇 Nhà đầu tư thiên tài!' if total_score > 15 else ''}"
        f"{'🥈 Nhà đầu tư tiềm năng!' if 10 <= total_score <= 15 else ''}"
        f"{'🥉 Cần học hỏi thêm!' if total_score < 10 else ''}"
    )
    await update.message.reply_text(text=result_message, parse_mode=ParseMode.HTML)

# Thêm CallbackQueryHandler
def run_bot():
    application = Application.builder().token(TOKEN).build()

    # Thêm các handler cho các lệnh
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CallbackQueryHandler(handle_answer))  # Bắt sự kiện trả lời

    # Chạy bot
    logger.info("Bot đang chạy...")
    application.run_polling()
