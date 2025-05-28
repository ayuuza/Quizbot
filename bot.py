import json
import random
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

with open("questions.json", "r") as f:
    QUESTIONS = json.load(f)

USER_DATA = {}

QUESTION, QUIZ = range(2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    random.shuffle(QUESTIONS)
    USER_DATA[user_id] = {
        "questions": QUESTIONS[:100],
        "index": 0,
        "correct": 0,
        "incorrect": 0
    }
    await update.message.reply_text("Welcome to the CBSE Class 10 Quiz Bot!\nLet's start.")
    return await ask_question(update, context)

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = USER_DATA[user_id]
    if data["index"] >= len(data["questions"]):
        return await show_result(update, context)
    
    q = data["questions"][data["index"]]
    options = q["options"]
    keyboard = [[opt] for opt in options]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    
    await update.message.reply_text(f"Q{data['index']+1}. {q['question']}", reply_markup=reply_markup)
    return QUIZ

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = USER_DATA[user_id]
    q = data["questions"][data["index"]]
    user_answer = update.message.text
    correct_option = q["options"][q["answer"]]

    if user_answer == correct_option:
        await update.message.reply_text("Nice, you can do it!")
        data["correct"] += 1
    else:
        await update.message.reply_text("Your choice is incorrect.")
        data["incorrect"] += 1

    data["index"] += 1
    return await ask_question(update, context)

async def show_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = USER_DATA[user_id]
    correct = data["correct"]
    incorrect = data["incorrect"]
    total = correct + incorrect

    result = f"Quiz Completed!\nCorrect: {correct}\nIncorrect: {incorrect}\nScore: {correct}/{total}"

    punishment = ""
    if correct < 20:
        punishment = (
            "\n\n😬 You scored less than 20.\n"
            "Punishment:\n- 50 pushups (Girls: Solve 100 math sums)\n"
            "- 200 squats (Girls: Upload 5 no-filter, no-makeup photos)"
        )
    elif correct < 40:
        punishment = (
            "\n\n😅 You scored less than 40.\n"
            "Punishment:\n- 20 pushups (Girls: Upload 1 photo without filter/makeup)\n"
            "- 50 squats (Girls: Solve 30 math sums)"
        )

    await update.message.reply_text(result + punishment)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Quiz cancelled.")
    return ConversationHandler.END

def main():
    import os
    from telegram.ext import ApplicationBuilder

    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            QUIZ: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
