import re
import os
from dotenv import load_dotenv
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext, CallbackQueryHandler, ConversationHandler

load_dotenv()

TOKEN:  Final = os.getenv('TOKEN')
BOT_USERNAME: Final = '@quizz_ybot'

#commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    fname = update.message.from_user.first_name
    await update.message.reply_text("Welcome, ${fname}! I am your quiz making wizard, under your service!, use /help command to learn how to trigger my magic trick! ")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("To turn your text into a quiz, please surround the question by a question mark `?` and a dot `.` , and then follow it with each answer surrounded by an exlamation mark `!` and a dot `.` , and follow it with the correct answer ID surrounded by colons `:`, then an optional explanation surrounded by double colons `::`, example: ```\n?what is the color of sky. \n!blue. \n!green. \n!red. \n:1: \n::just look at it!::```", parse_mode='MarkdownV2')

async def quiz_command(update: Update, context: CallbackContext):
    await create_quiz(update.message.text, update, context)


#responses
async def create_quiz(text: str, update: Update, context: CallbackContext):
    question_match = re.search(r"\?([^\.]+)\.", text)
    print(f'NOOOOOOOOOOO')
    if question_match:
        question = question_match.group(1)  # Extract text between double quotes
        answers = re.findall(r"\!([^\.]+)\.", text)  # Extract text between hashtags
        answersList = []
        correct_answer_id = 1  # Default value is "1" if not specified
        explanation = ''  # Default explanation if not specified

        # Check if answers are provided and there are at least 2 answers
        if answers:
            if len(answers) < 2:
                await update.message.reply_text("Please provide at least two answers.")
                return
        else:
            await update.message.reply_text("Please provide answers surrounded by an exlamation mark and a dot, example:`!answer.`  see /help", parse_mode='MarkdownV2')
            return

        # Pattern for identifying correct answer id and explanation
        correct_answer_match = re.search(r':(\d+):', text)
        if correct_answer_match:
            correct_answer_id = int(correct_answer_match.group(1))
            if correct_answer_id > len(answers) or correct_answer_id < 1:
                await update.message.reply_text("The correct answer ID is out of the range of provided answers.")
                return
        else:
            await update.message.reply_text("Please provide the correct answer ID surrounded by colons `:`.  see /help", parse_mode='MarkdownV2')

        explanation_match = re.search(r'::([^:]+)::', text)
        if explanation_match:
            explanation = explanation_match.group(1)

        quiz = f'Question: {question}\n'
        for idx, ans in enumerate(answers, start=1):
            quiz += f'{idx}) {ans}\n'
            answersList.append(ans)

        await context.bot.send_poll(
            update.effective_chat.id,
            question,
            answersList,
            is_anonymous=False,
            type='quiz',
            explanation=explanation,
            correct_option_id=correct_answer_id-1
        )
    else:
        await update.message.reply_text("Please provide a question surrounded by a question mark '?' in the beginning and a dot '.' in the end. see /help")

# turn sequence of messages into a quiz
quizzes = {}

async def lquiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    quizzes[user_id] = {"stage": "question", "question": "", "answers": [], "correct_answer": None, "explanation": ""}
    await update.message.reply_text("Creating a new quiz! Please send the question.")

async def receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    quiz = quizzes.get(user_id)

    if not quiz:
        await update.message.reply_text("Please start a new quiz by sending /lquiz.")
        return

    stage = quiz["stage"]

    if stage == "question":
        quiz["question"] = update.message.text
        quiz["stage"] = "answers"
        await update.message.reply_text("Now send me the list of answers, one per line. Type 'done' when you're finished.")

    elif stage == "answers":
        if update.message.text.lower() == "done":
            if len(quiz["answers"]) < 2:
                await update.message.reply_text("Please provide at least two answers.")
            else:
                quiz["stage"] = "correct_answer"
                await update.message.reply_text("Please send the number of the correct answer.")
        else:
            quiz["answers"].append(update.message.text)
            await update.message.reply_text("Answer added! Send another answer or type 'done'.")

    elif stage == "correct_answer":
        try:
            correct_answer = int(update.message.text)
            if 1 <= correct_answer <= len(quiz["answers"]):
                quiz["correct_answer"] = correct_answer
                quiz["stage"] = "explanation"
                await update.message.reply_text("Optionally, send an explanation for the correct answer. Type 'done' if you don't want to add one.")
            else:
                await update.message.reply_text(f"Please send a number between 1 and {len(quiz['answers'])}.")
        except ValueError:
            await update.message.reply_text("Please send a valid number.")

    elif stage == "explanation":
        if update.message.text.lower() == "done":
            quiz["explanation"] = ""
        else:
            quiz["explanation"] = update.message.text

        await send_quiz_poll(update, quiz)
        del quizzes[user_id]

async def send_quiz_poll(update: Update, quiz):
    try:
        await update.effective_chat.send_poll(
            question=quiz["question"],
            options=quiz["answers"],
            is_anonymous=False,
            type='quiz',
            explanation=quiz["explanation"],
            correct_option_id=quiz["correct_answer"] - 1
        )
    except Exception as e:
        await update.message.reply_text(f"An error occurred while creating the quiz: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type

    if message_type == 'group':
        if '/quiz' in update.message.text:
            await quiz_command(update, context)
    #else:
        #await update.message.reply_text('Command not found, try /quiz')
    else:
        if '/quiz' in update.message.text:
            await quiz_command(update, context)
        else:
            await lquiz_command(update, context)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    
    print('starting......')
    app = Application.builder().token(TOKEN).build()

#COMMANDS
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('quiz', quiz_command))
    app.add_handler(CommandHandler('lquiz', lquiz_command))

#MESSAGES
    #app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_message))

#ERRORS
    app.add_error_handler(error)

#POLLS THE BOT
    print('polling......')
    app.run_polling(poll_interval = 3)