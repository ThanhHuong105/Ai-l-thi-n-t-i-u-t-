from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, CallbackContext

# Token bot Telegram
TOKEN = "7014456931:AAE5R6M9wgfMMyXPYCdogRTISwbaUjSXQRo"

# Hàm xử lý khi người dùng mở bot hoặc nhập /start
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(
        text="\U0001F525 Bạn đã sẵn sàng tham gia tìm kiếm 'Ai là thiên tài đầu tư?' Bấm /start để bắt đầu.",
        parse_mode=ParseMode.HTML
    )

# Hàm xử lý khi người dùng nhập /start để xem luật chơi
def show_rules(update: Update, context: CallbackContext) -> None:
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
    update.message.reply_text(text=rules_message, parse_mode=ParseMode.HTML)

# Hàm chính để khởi chạy bot
def main():
    # Khởi tạo updater và dispatcher
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    # Thêm các handler cho các lệnh
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("quiz", show_rules))

    # Bắt đầu bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
