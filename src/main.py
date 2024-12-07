import os
from dotenv import load_dotenv
from flask import Flask, request
from bot import create_bot


# Load environment variables
load_dotenv()
TOKEN = os.getenv('TOKEN')
TELEGRAM_URL = "https://api.telegram.org/bot{token}".format(token=TOKEN)
WEBHOOK = os.getenv('WEBHOOK_URL')
WEBHOOK_URL = "https://{webhook}".format(webhook=WEBHOOK)

# Initialize Flask app
app = Flask(__name__)

# Initialize Telegram bot
telegram_app = create_bot(TOKEN)

@app.route(f'/{TOKEN}', methods=['POST'])
def webhook_handler():
    """Handle webhook updates."""
    data = request.json
    telegram_app.update_queue.put(data)
    return 'OK'

@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    """Set the Telegram webhook."""
    webhook_result = telegram_app.bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    return f"Webhook setup result: {webhook_result}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8443)))
