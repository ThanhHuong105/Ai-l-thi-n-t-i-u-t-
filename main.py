import logging
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes

# Token bot Telegram
TOKEN = "7014456931:AAE5R6M9wgfMMyXPYCdogRTISwbaUjSXQRo"

# Cấu hình logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Hàm xử lý khi người dùng mở bot hoặc nhập /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        text="\U0001F525 Bạn đã sẵn sàng tham gia tìm kiếm 'Ai là thiên tài đầu tư?' Bấm /start để bắt đầu.",
        parse_mode=ParseMode.HTML
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
def main():
    # Tạo ứng dụng bot
    application = Application.builder().token(TOKEN).build()

    # Thêm các handler cho các lệnh
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quiz", show_rules))

    # Chạy bot
    logger.info("Bot đang chạy...")
    application.run_polling()

if __name__ == "__main__":
    main()
import logging
import asyncio
import requests
import csv
from random import choice
from telegram import Update, ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Token bot Telegram
TOKEN = "7014456931:AAE5R6M9wgfMMyXPYCdogRTISwbaUjSXQRo"

# ID Google Sheets và URL để tải bảng TTCK
SHEET_ID = "1QMKiohAaO5QtHoQwBX5efTXCl_Q791A4GnoCe9nMV2w"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=TTCK"

# Cấu hình logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Hàm tải câu hỏi từ Google Sheets
def fetch_questions_from_csv():
    response = requests.get(SHEET_URL)
    response.raise_for_status()  # Kiểm tra nếu lỗi xảy ra

    questions = []
    decoded_content = response.content.decode('utf-8')
    csv_reader = csv.DictReader(decoded_content.splitlines())

    for row in csv_reader:
        questions.append(row)

    return questions

# Hàm lấy câu hỏi ngẫu nhiên
def get_random_question():
    questions = fetch_questions_from_csv()
    return choice(questions)  # Chọn ngẫu nhiên một câu hỏi

# Hàm xử lý khi người dùng mở bot hoặc nhập /start
def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    update.message.reply_text(
        text="\U0001F525 Bạn đã sẵn sàng tham gia tìm kiếm 'Ai là thiên tài đầu tư?' Bấm /quiz để bắt đầu.",
        parse_mode=ParseMode.HTML
    )

# Hàm xử lý khi người dùng nhập /quiz để xem luật chơi
def show_rules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
        "\U0001F449 Nhấn /next để trả lời câu hỏi đầu tiên!"
    )
    update.message.reply_text(text=rules_message, parse_mode=ParseMode.HTML)

# Hàm hiển thị câu hỏi và đếm ngược
async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = get_random_question()

    # Tạo nội dung câu hỏi
    question_text = (
        f"<b>Câu hỏi:</b> {question['Question']}\n\n"
        f"1️⃣ {question['Option 1']}\n"
        f"2️⃣ {question['Option 2']}\n"
        f"3️⃣ {question['Option 3']}\n\n"
        "Hãy trả lời bằng cách nhập số 1, 2 hoặc 3!"
    )
    await update.message.reply_text(text=question_text, parse_mode=ParseMode.HTML)

    # Lưu câu hỏi hiện tại
    context.user_data['current_question'] = question
    context.user_data['answer_received'] = False  # Đánh dấu chưa nhận câu trả lời

    # Đếm ngược 60 giây
    for remaining in range(60, 0, -1):
        if context.user_data.get('answer_received', False):  # Kiểm tra nếu đã trả lời
            return
        if remaining in [30, 10, 5]:
            await update.message.reply_text(f"⏳ Còn {remaining} giây!")
        await asyncio.sleep(1)

    # Hết thời gian, thông báo
    await update.message.reply_text("⏰ Hết thời gian! Bạn không trả lời câu hỏi này.")
    context.user_data['current_question'] = None  # Xóa câu hỏi hiện tại

# Hàm xử lý câu trả lời của người dùng
def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_answer = update.message.text.strip()
    question = context.user_data.get('current_question', None)

    if not question:
        update.message.reply_text("⛔ Bạn chưa bắt đầu câu hỏi nào. Nhấn /next để tiếp tục!")
        return

    # Kiểm tra câu trả lời
    correct_answer = question['Answer']
    if user_answer == correct_answer:
        update.message.reply_text("✅ Chính xác! Bạn được 1 điểm.")
    else:
        update.message.reply_text(f"❌ Sai rồi! Đáp án đúng là: {correct_answer}.")

    # Đánh dấu đã nhận câu trả lời
    context.user_data['answer_received'] = True
    context.user_data['current_question'] = None  # Xóa câu hỏi hiện tại

# Hàm chính để khởi chạy bot
async def main():
    # Tạo ứng dụng bot
    application = Application.builder().token(TOKEN).build()

    # Thêm các handler cho các lệnh
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("quiz", show_rules))
    application.add_handler(CommandHandler("next", ask_question))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))

    # Chạy bot
    logger.info("Bot đang chạy...")
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
