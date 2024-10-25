Quizz_ybot
==========

A Telgram bot written in Python using python-telegram-bot package.


## How to use the bot

To display bot instructions in the chat, send `/help` command.

**Turn one-message text into a quiz:**

- Surround the question with a question mark and a dot; `?question text.` 
- Surround the answers with an exlamation mark and a dot; `!answer text.`
- Surround the correct answer index (starting from 1) with colons; `:1:`
- Surround the explanation with double colons (optional); `::explanation text::`

---
### Future thoughts

**Turn a sequence of messages into a quiz:**

Follow the bot's instructions to make a quiz, where you send the question solely in a message, followed by a list of single line answers (each answer on a new line), followed by the number of the correct answer, then optionally followed by an explanation message.

**Make the bot more user friendly:**

The bot is dedicated to make quiz making on telegram easier, by pressing less buttons which makes the process more *automated*, some teachers share quizzez with their students on telegram, so the bot should make the process faster to them.