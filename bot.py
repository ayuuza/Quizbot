import json
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import Update, ReplyKeyboardMarkup
import logging

# Load questions from JSON
with open("questions.json") as f:
    QUESTIONS = json.load(f)

# State: user_id -> progress
USER_STATE = {}

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    USER_STATE[user_id] = {"index": 0, "correct": 0, "incorrect": 0, "answers": []}
    send_question(update, context)

def send_question(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    state = USER_STATE[user_id]
    index = state["index"]

    if index >= len(QUESTIONS):
        update.message.reply_text("You've completed all questions! Use /result to see your score.")
        return

    q = QUESTIONS[index]
    reply_markup = ReplyKeyboardMarkup([q["options"]], one_time_keyboard=True)
    update.message.reply_text(f"Q{index+1}: {q['question']}", reply_markup=reply_markup)

def handle_answer(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    state = USER_STATE.get(user_id)

    if not state:
        update.message.reply_text("Send /start to begin the quiz.")
        return

    index = state["index"]
    if index >= len(QUESTIONS):
        update.message.reply_text("You've completed the quiz. Use /result to see your score.")
        return

    q = QUESTIONS[index]
    user_answer = update.message.text.strip()
    correct_answer = q["answer"]

    if user_answer == correct_answer:
        state["correct"] += 1
        update.message.reply_text("Nice! Keep it up 💯")
    else:
        state["incorrect"] += 1
        update.message.reply_text(f"Incorrect 😕 why did you select '{user_answer}'?
Correct answer: {correct_answer}")

    state["index"] += 1
    send_question(update, context)

def result(update: Update, context: CallbackContext):
    user_id = update.message.chat_id
    state = USER_STATE.get(user_id)

    if not state:
        update.message.reply_text("No data found. Start with /start.")
        return

    correct = state["correct"]
    incorrect = state["incorrect"]
    update.message.reply_text(f"Your result:
✅ Correct: {correct}
❌ Incorrect: {incorrect}")

    punishment = ""
    if 25 <= incorrect <= 30:
        punishment = (
            "🏋️ Do 15 push-ups and 100 squats
"
            "📷 Girls: Upload 1 photo on Instagram without makeup and filter
"
            "🧠 Girls: Solve 30 maths sums in 1 day"
        )
    elif 31 <= incorrect <= 40:
        punishment = (
            "🏋️ Do 50 push-ups and 200 squats
"
            "📷 Girls: Upload 5 photos on Instagram without makeup and filter
"
            "🧠 Girls: Solve 50 maths sums in 1 day"
        )

    if punishment:
        update.message.reply_text(f"⚠️ Based on your score, here’s your challenge:
{punishment}")
    else:
        update.message.reply_text("Great effort! No challenge this time 🎉")

def review(update: Update, context: CallbackContext):
    update.message.reply_text("Please type your review. It will be sent to the developer @Brave_soull.")
    context.user_data["awaiting_review"] = True

def handle_message(update: Update, context: CallbackContext):
    if context.user_data.get("awaiting_review"):
        context.user_data["awaiting_review"] = False
        user_review = update.message.text
        username = update.message.from_user.username or "Unknown User"
        logger.info(f"Forwarding review to @Brave_soull from @{username}: {user_review}")
        update.message.reply_text("Thanks for your feedback! Your review has been sent to the developer.")
    else:
        handle_answer(update, context)

def main():
    TOKEN = "7964523879:AAGHnf27A66SYF5oNrBH-37mSijksR60g1s"  # Replace with your actual bot token
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("result", result))
    dp.add_handler(CommandHandler("review", review))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
    
