import re
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext

TOKEN:  Final = '6800558875:AAG_oSnWvphzUbxmDoABb1bZ8Gdf9GSaj1M'
BOT_USERNAME: Final = '@quizz_ybot'

#commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi!, I am your quiz making wizard, under your service!, use /help command to learn how to trigger my magic trick! ")

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
        correct_answer_id = -1  # Default value if not specified
        explanation = ''  # Default explanation if not specified

        # Check if answers are provided and there are at least 2 answers
        if answers:
            if len(answers) < 2:
                await update.message.reply_text("Please provide at least two answers.")
                return
        else:
            await update.message.reply_text("Please provide answers surrounded by an exlamation mark and a dot, example:`!correct answer\.`\.  see /help", parse_mode='MarkdownV2')
            return

        # Pattern for identifying correct answer id and explanation
        correct_answer_match = re.search(r':(\d+)', text)
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
        await update.message.reply_text("Please provide a question surrounded by double quotes. see /help")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type

    if message_type == 'group':
        if '/quiz' in update.message.text:
            await quiz_command(update, context)
    #else:
        #await update.message.reply_text('Command not found, try /quiz')
    else:
        await quiz_command(update, context)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    
    print('starting......')
    app = Application.builder().token(TOKEN).build()

#COMMANDS
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('quiz', quiz_command))

#MESSAGES
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

#ERRORS
    app.add_error_handler(error)

#POLLS THE BOT
    print('polling......')
    app.run_polling(poll_interval = 3)