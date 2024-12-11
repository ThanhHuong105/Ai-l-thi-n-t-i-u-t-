from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import requests
import random
import csv
from io import StringIO
from PIL import Image, ImageDraw, ImageFont

# Token của Telegram bot
TELEGRAM_TOKEN = '8161313133:AAFcvw3RhIzdoz7cWZqeVGEWuYyB3b1qCCI'

# Link Google Sheets (chế độ công khai)
GOOGLE_SHEET_CSV_URL = 'https://docs.google.com/spreadsheets/d/1QMKiohAaO5QtHoQwBX5efTXCI_Q791A4GnoCe9nMV2w/export?format=csv'

# Danh sách câu hỏi, câu hỏi hiện tại, và điểm số
QUESTIONS = []
CURRENT_QUESTION = {}
PLAYER_SCORE = 0
QUESTIONS_ASKED = 0  # Số câu hỏi đã trả lời
ANSWER_TIMEOUT = False  # Trạng thái hết giờ cho câu hỏi hiện tại
CURRENT_JOB = None  # Lưu công việc đếm giờ hiện tại

# Hàm tải câu hỏi từ Google Sheets ở dạng CSV
def load_questions():
    global QUESTIONS
    response = requests.get(GOOGLE_SHEET_CSV_URL)
    response.raise_for_status()
    csv_data = response.content.decode('utf-8')

    # Đọc dữ liệu CSV
    reader = csv.DictReader(StringIO(csv_data))
    QUESTIONS = []  # Reset câu hỏi
    for row in reader:
        question = {
            "question": row['Question'],
            "options": [row['Option 1'], row['Option 2'], row['Option 3']],
            "answer": row['Answer']
        }
        QUESTIONS.append(question)

# Hàm tạo ảnh kết quả với nền
async def create_summary_image(score, rank):
    background_path = "/mnt/data/Slide457.png"  # Đường dẫn tới ảnh nền
    background = Image.open(background_path)

    # Tạo vùng vẽ trên ảnh
    draw = ImageDraw.Draw(background)

    # Font chữ
    font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 55)
    font_body = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 35)

    # Tính toán vị trí chữ
    image_width, image_height = background.size
    title_text = "KẾT QUẢ QUIZ"
    score_text = f"Điểm: {score}/20"
    rank_text = f"Danh hiệu: {rank}"

    title_position = ((image_width - draw.textsize(title_text, font=font_title)[0]) // 2, 40)
    score_position = ((image_width - draw.textsize(score_text, font=font_body)[0]) // 2, image_height // 2 + 110)
    rank_position = ((image_width - draw.textsize(rank_text, font=font_body)[0]) // 2, image_height // 2 + 140)

    # Vẽ chữ lên ảnh
    draw.text(title_position, title_text, fill="white", font=font_title)
    draw.text(score_position, score_text, fill="yellow", font=font_body)
    draw.text(rank_position, rank_text, fill="green", font=font_body)

    # Lưu ảnh kết quả
    result_path = "/tmp/quiz_summary.png"
    background.save(result_path)
    return result_path

# Hàm hiển thị tổng kết
async def send_summary(update: Update):
    global PLAYER_SCORE, QUESTIONS_ASKED, CURRENT_QUESTION
    rank = (
        "Nhà đầu tư thiên tài! 🎉" if PLAYER_SCORE > 15 else
        "Nhà đầu tư tiềm năng." if 10 <= PLAYER_SCORE <= 15 else
        "Cần học hỏi thêm!"
    )

    # Tạo ảnh tổng kết
    file_path = await create_summary_image(PLAYER_SCORE, rank)

    # Nút chia sẻ
    share_keyboard = [
        [
            InlineKeyboardButton("📤 Chia sẻ lên Facebook", url="https://www.facebook.com"),
            InlineKeyboardButton("🐦 Chia sẻ lên X (Twitter)", url="https://twitter.com"),
        ],
        [
            InlineKeyboardButton("📸 Hướng dẫn chia sẻ Instagram", url="https://www.instagram.com"),
            InlineKeyboardButton("📩 Gửi sang phòng Telegram", switch_inline_query="Chia sẻ kết quả quiz!"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(share_keyboard)

    # Gửi ảnh và tổng kết
    await update.message.reply_photo(photo=open(file_path, 'rb'), caption="🏆 Tổng kết quiz của bạn!", reply_markup=reply_markup)

    # Reset trạng thái
    QUESTIONS_ASKED = 0
    PLAYER_SCORE = 0
    CURRENT_QUESTION = {}

# Hàm xử lý lời chào tự động
async def auto_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_text = (
        "🎉 Chào mừng bạn đến với Gameshow 'Ai Là Nhà Đầu Tư Tài Ba'!\n\n"
        "📋 Luật chơi:\n"
        "- Có 20 câu hỏi với tổng số điểm tối đa là 20.\n"
        "- Mỗi câu trả lời đúng được 1 điểm.\n"
        "- Nếu không trả lời trong 60 giây, bạn sẽ bị tính 0 điểm cho câu đó.\n\n"
        "✨ Mục tiêu của bạn:\n"
        "- Trên 15 điểm: Nhà đầu tư thiên tài.\n"
        "- Từ 10 đến 15 điểm: Nhà đầu tư tiềm năng.\n"
        "- Dưới 10 điểm: Cần học hỏi thêm!\n\n"
        "👉 Nhấn /quiz để bắt đầu!"
    )
    await update.message.reply_text(welcome_text)

# Hàm bắt đầu quiz
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global CURRENT_QUESTION, QUESTIONS_ASKED, PLAYER_SCORE, ANSWER_TIMEOUT, CURRENT_JOB

    if QUESTIONS_ASKED >= 20:
        await send_summary(update)
        return

    if CURRENT_JOB:  # Hủy công việc đếm giờ trước đó nếu có
        CURRENT_JOB.schedule_removal()

    CURRENT_QUESTION = random.choice(QUESTIONS)
    QUESTIONS_ASKED += 1
    ANSWER_TIMEOUT = False
    question_text = CURRENT_QUESTION["question"]
    options = "\n".join([f"{i + 1}. {opt}" for i, opt in enumerate(CURRENT_QUESTION["options"])])
    await update.message.reply_text(
        f"Câu {QUESTIONS_ASKED}: {question_text}\n\n{options}\n\n⏳ Bạn có 60 giây để trả lời!"
    )

    # Hẹn giờ 60 giây
    CURRENT_JOB = context.job_queue.run_once(timeout_question, 60, data={'chat_id': update.message.chat_id})

# Hẹn giờ 60 giây cho câu hỏi
async def timeout_question(context: ContextTypes.DEFAULT_TYPE):
    global ANSWER_TIMEOUT, CURRENT_JOB
    chat_id = context.job.data['chat_id']
    if not ANSWER_TIMEOUT:  # Chỉ báo hết giờ nếu chưa trả lời
        ANSWER_TIMEOUT = True
        CURRENT_JOB = None  # Xóa công việc hiện tại
        await context.bot.send_message(
            chat_id=chat_id,
            text="⏱ Hết giờ! Bạn bị tính 0 điểm cho câu hỏi này.\n\nNhấn /quiz để tiếp tục câu hỏi tiếp theo."
        )

# Hàm xử lý câu trả lời
async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    global CURRENT_QUESTION, PLAYER_SCORE, ANSWER_TIMEOUT, CURRENT_JOB

    if ANSWER_TIMEOUT:
        await update.message.reply_text("⏱ Hết giờ! Đáp án của bạn không được chấp nhận.\n\nNhấn /quiz để tiếp tục.")
        return

    if CURRENT_JOB:  # Hủy công việc đếm giờ nếu người chơi trả lời
        CURRENT_JOB.schedule_removal()
        CURRENT_JOB = None

    user_answer = update.message.text.strip()
    correct_answer = str(CURRENT_QUESTION["answer"])

    if user_answer == correct_answer:
        PLAYER_SCORE += 1
        await update.message.reply_text(
            f"🎉 Chính xác! Điểm hiện tại của bạn: {PLAYER_SCORE}\n\nNhấn /quiz để tiếp tục."
        )
    else:
        await update.message.reply_text(
            f"Sai rồi! Đáp án đúng là: {correct_answer}.\n\nĐiểm hiện tại của bạn: {PLAYER_SCORE}\n\nNhấn /quiz để tiếp tục."
        )
    ANSWER_TIMEOUT = True  # Dừng đếm ngược
    CURRENT_QUESTION = {}  # Xóa câu hỏi hiện tại

# Hàm chính chạy bot
def main():
    # Tải câu hỏi
    load_questions()

    # Khởi tạo bot
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Đăng ký các lệnh
    application.add_handler(CommandHandler('start', auto_welcome))
    application.add_handler(CommandHandler('quiz', quiz))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, answer))

    # Bắt đầu chạy bot
    print("Bot quiz đang chạy... Nhấn Ctrl+C để dừng.")
    application.run_polling()

if __name__ == '__main__':
    main()
