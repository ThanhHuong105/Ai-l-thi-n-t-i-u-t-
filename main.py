import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes

# Token bot Telegram
TOKEN = "7014456931:AAE5R6M9wgfMMyXPYCdogRTISwbaUjSXQRo"

# Cấu hình logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Hàm xử lý khi người dùng mở bot hoặc nhập /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        text="\U0001F525 Bạn đã sẵn sàng tham gia tìm kiếm 'Ai là thiên tài đầu tư?' Bấm /start để bắt đầu.",
        parse_mode=ParseMode.HTML,
    )

# Hàm xử lý khi người dùng nhập /quiz để xem luật chơi
async def show_rules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    rules_message = (
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
    await update.message.reply_text(text=rules_message, parse_mode=ParseMode.HTML)

# Hàm chính để khởi chạy bot
async def main():
    # Tạo ứng dụng bot
    application = Application.builder().token(TOKEN).build()

    # Thêm các handler cho các lệnh
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quiz", show_rules))

    # Chạy bot
    logger.info("Bot đang chạy...")
    await application.run_polling()

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
