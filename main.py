import logging
import requests
import csv
import random
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
import asyncio

# Token bot Telegram
TOKEN = "7014456931:AAE5R6M9wgfMMyXPYCdogRTISwbaUjSXQRo"

# URL Google Sheets CSV
SHEET_ID = "1QMKiohAaO5QtHoQwBX5efTXCI_Q791A4GnoCe9nMV2w"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&sheet=TTCK"

# Cấu hình logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Hàm tải câu hỏi từ Google Sheets
def fetch_questions_from_csv():
    try:
        response = requests.get(SHEET_URL)
        response.raise_for_status()  # Kiểm tra nếu lỗi xảy ra
        questions = []
        decoded_content = response.content.decode('utf-8')
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
        parse_mode=ParseMode.HTML
    )

# Hàm xử lý khi người dùng nhập /start
def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    questions = fetch_questions_from_csv()

    if not questions:
        await update.message.reply_text("❌ Lỗi: Không thể tải câu hỏi. Vui lòng thử lại sau.")
        return

    total_score = 0
    for i in range(1, 21):  # Lặp qua 20 câu hỏi
        question_data = random.choice(questions)
        question = question_data['Question']
        options = [
            InlineKeyboardButton(question_data['Option 1'], callback_data='1'),
            InlineKeyboardButton(question_data['Option 2'], callback_data='2'),
            InlineKeyboardButton(question_data['Option 3'], callback_data='3')
        ]
        correct_answer = str(question_data['Answer'])

        # Gửi câu hỏi
        reply_markup = InlineKeyboardMarkup.from_column(options)
        message = await update.message.reply_text(
            text=f"💬 Câu {i}: {question}",
            reply_markup=reply_markup
        )

        # Chờ phản hồi hoặc hết 60 giây
        try:
            query = await context.bot.wait_for(
                "callback_query",
                timeout=60,
                check=lambda q: q.message.message_id == message.message_id
            )
            user_answer = query.data

            # Kiểm tra câu trả lời đúng hay sai
            if user_answer == correct_answer:
                total_score += 1
                await query.answer("👍 Chính xác!", show_alert=True)
            else:
                await query.answer("😥 Sai rồi!", show_alert=True)

        except asyncio.TimeoutError:
            await update.message.reply_text("⏳ Hết thời gian cho câu này!")

        # Thông báo điểm số lũy kế
        await update.message.reply_text(f"💯 Điểm hiện tại: {total_score}/{i}")

    # Kết thúc game
    result_message = (
        f"🏆 Kết thúc game! Tổng điểm của bạn: {total_score}/20\n\n"
        "✨ <b>Kết quả:</b>\n"
        f"{'🥇 Nhà đầu tư thiên tài!' if total_score > 15 else ''}"
        f"{'🥈 Nhà đầu tư tiềm năng!' if 10 <= total_score <= 15 else ''}"
        f"{'🥉 Cần học hỏi thêm!' if total_score < 10 else ''}"
    )
    await update.message.reply_text(text=result_message, parse_mode=ParseMode.HTML)

# Hàm chính để khởi chạy bot
async def main():
    application = Application.builder().token(TOKEN).build()

    # Thêm các handler cho các lệnh
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quiz", quiz))
    application.add_handler(CommandHandler("welcome", welcome))

    # Chạy bot
    logger.info("Bot đang chạy...")
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())

