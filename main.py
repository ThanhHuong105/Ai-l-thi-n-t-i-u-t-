import logging
import csv
from telegram import Update, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
import random
import asyncio

# Token bot Telegram
TOKEN = "7014456931:AAE5R6M9wgfMMyXPYCdogRTISwbaUjSXQRo"

# Cấu hình logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Đọc dữ liệu từ file CSV
def load_questions_from_csv():
    questions = []
    with open("questions.csv", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            questions.append(row)
    return questions

# Hàm xử lý khi người dùng mở bot
def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    update.message.reply_text(
        text="\U0001F525 Bạn đã sẵn sàng tham gia tìm kiếm 'Ai là thiên tài đầu tư?' Bấm /start để bắt đầu.",
        parse_mode=ParseMode.HTML
    )

# Hàm xử lý khi người dùng nhập /start
def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_message = (
        "\U0001F389 <b>Chào mừng bạn đến với Gameshow 'Ai Là Nhà Đầu Tư Tài Ba'!</b>\n\n"
        "\U0001F4CB <b>Luật chơi:</b>\n"
        "- Có 20 câu hỏi với tổng số điểm tối đa là 20.\n"
        "- Mỗi câu trả lời đúng được 1 điểm.\n"
        "- Nếu không trả lời trong 60 giây, bạn sẽ bị tính 0 điểm cho câu đó.\n\n"
        "\u2728 <b>Mục tiêu của bạn:</b>\n"
        "- Trên 15 điểm: Nhà đầu tư thiên tài.\n"
        "- Từ 10 đến 15 điểm: Nhà đầu tư tiềm năng.\n"
        "- Dưới 10 điểm: Cần học hỏi thêm!\n\n"
        "\U0001F449 Nhấn /quiz để bắt đầu!"
    )
    update.message.reply_text(text=welcome_message, parse_mode=ParseMode.HTML)

# Hàm xử lý khi người dùng nhập /quiz (phần câu hỏi)
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    questions = load_questions_from_csv()

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
            text=f"\U0001F4AC Câu {i}: {question}",
            reply_markup=reply_markup
        )

        # Chờ phản hồi hoặc hết 60 giây
        try:
            query: Update = await context.bot.wait_for(
                "callback_query",
                timeout=60,
                check=lambda q: q.message.message_id == message.message_id
            )
            user_answer = query.data

            # Kiểm tra câu trả lời đúng hay sai
            if user_answer == correct_answer:
                total_score += 1
                await query.answer("\U0001F44D Chính xác!", show_alert=True)
            else:
                await query.answer("\U0001F625 Sai rồi!", show_alert=True)

        except asyncio.TimeoutError:
            await update.message.reply_text("\u23F3 Hết thời gian cho câu này!")

        # Thông báo điểm số lũy kế
        await update.message.reply_text(f"\U0001F4AF Điểm hiện tại: {total_score}/{i}")

    # Kết thúc game
    result_message = (
        f"\U0001F3C6 Kết thúc game! Tổng điểm của bạn: {total_score}/20\n\n"
        "\u2728 <b>Kết quả:</b>\n"
        f"{'\U0001F947 Nhà đầu tư thiên tài!' if total_score > 15 else ''}"
        f"{'\U0001F948 Nhà đầu tư tiềm năng!' if 10 <= total_score <= 15 else ''}"
        f"{'\U0001F949 Cần học hỏi thêm!' if total_score < 10 else ''}"
    )
    await update.message.reply_text(text=result_message, parse_mode=ParseMode.HTML)

# Hàm chính để khởi chạy bot
async def main():
    # Tạo ứng dụng bot
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
