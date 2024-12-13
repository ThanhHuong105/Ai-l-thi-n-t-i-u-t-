# Ask Next Question
def ask_question(update: Update, context: CallbackContext):
    user_data = context.user_data
    current = user_data["current_question"]
    questions = user_data["questions"]

    # Hủy job timeout cũ nếu tồn tại
    if "timeout_job" in user_data and user_data["timeout_job"]:
        try:
            user_data["timeout_job"].schedule_removal()
        except Exception as e:
            logger.error(f"Error removing timeout job: {e}")

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

        # Đặt timeout mới
        timeout_job = context.job_queue.run_once(timeout_handler, 60, context=update.message.chat_id)
        user_data["timeout_job"] = timeout_job
        return WAIT_ANSWER
    else:
        finish_quiz(update, context)
        return ConversationHandler.END

# Timeout Handler
def timeout_handler(context: CallbackContext):
    chat_id = context.job.context
    bot = context.bot

    user_data = context.dispatcher.user_data.get(chat_id, {})
    current = user_data.get("current_question", 0)
    questions = user_data.get("questions", [])

    if current < len(questions):
        bot.send_message(
            chat_id=chat_id,
            text=f"⏳ Hết thời gian cho câu này! Tổng điểm hiện tại của bạn là {user_data.get('score', 0)}/20."
        )
        user_data["timeout_job"] = None  # Xóa job timeout sau khi hết thời gian
        ask_question_via_context(context, chat_id)
    else:
        finish_quiz_via_context(context, chat_id)

# Ask Question via Context
def ask_question_via_context(context: CallbackContext, chat_id):
    user_data = context.dispatcher.user_data.get(chat_id, {})
    current = user_data.get("current_question", 0)
    questions = user_data.get("questions", [])

    if "timeout_job" in user_data and user_data["timeout_job"]:
        try:
            user_data["timeout_job"].schedule_removal()
        except Exception as e:
            logger.error(f"Error removing timeout job: {e}")

    if current < len(questions):
        question = questions[current]
        options = [question["Option 1"], question["Option 2"], question["Option 3"]]
        user_data["current_question"] += 1

        context.bot.send_message(
            chat_id=chat_id,
            text=f"💬 *Câu {current + 1}:* {question['Question']}\n\n"
                 f"1️⃣ {options[0]}\n"
                 f"2️⃣ {options[1]}\n"
                 f"3️⃣ {options[2]}",
            reply_markup=ReplyKeyboardMarkup([[1, 2, 3]], one_time_keyboard=True),
        )

        timeout_job = context.job_queue.run_once(timeout_handler, 60, context=chat_id)
        user_data["timeout_job"] = timeout_job
    else:
        finish_quiz_via_context(context, chat_id)
