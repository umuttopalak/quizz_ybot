from dotenv import load_dotenv
from typing import Final
from fastapi import FastAPI, Request, HTTPException

# Webhook Route
@app.post(WEBHOOK_PATH)
async def handle_webhook(request: Request):
    try:
        update = Update.de_json(await request.json(), bot_app.bot)
        await bot_app.process_update(update)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing update: {e}")


@app.on_event("startup")
async def startup():
    # Configure the bot with handlers
    bot_app.add_handler(CommandHandler("start", start_command))
    bot_app.add_handler(CommandHandler("help", help_command))
    bot_app.add_handler(CommandHandler("quiz", quiz_command))
    bot_app.add_handler(CommandHandler("lquiz", lquiz_command))

    # Set Webhook
    await bot_app.bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")

@app.on_event("shutdown")
async def shutdown():
    await bot_app.shutdown()