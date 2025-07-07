from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from ENV import telegram_bot_token
import requests

# Langflow config
BASE_API_URL = f"http://127.0.0.1:7860"
FLOW_ID = "input your flow ID"
ENDPOINT = "" # You can set a specific endpoint name in the flow settings

# Telegram bot token
TELEGRAM_BOT_TOKEN = telegram_bot_token

# Function to send user message to Langflow
def run_flow(message: str) -> dict:
    """
    Run a flow with a given message and optional tweaks.

    :param message: The message to send to the flow
    :param endpoint: The ID or the endpoint name of the flow
    :param tweaks: Optional tweaks to customize the flow
    :return: The JSON response from the flow
    """
    api_url = f"{BASE_API_URL}/api/v1/run/{ENDPOINT or FLOW_ID}"

    payload = {
        "input_value": message,
        "output_type": "chat",
        "input_type": "chat",
    }

    response = requests.post(api_url, json=payload)
    return response.json()

# Function to extract the desired message 
def extract_message(response: dict) -> str: 
    try: 
        # Navigate to the message inside the response structure 
        return response['outputs'][0]['outputs'][0]['results']['message']['text']
    except(KeyError, IndexError):
        return "No valid message found in response."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    flow_response = run_flow(user_text)
    reply_text = extract_message(flow_response)

    if 'Agent stopped due to iteration limit or time limit.' in reply_text.strip():
        reply_text = 'Maaf, saya tidak dapat menjawab soalan ini.'

    await update.message.reply_text(reply_text)

    
# Start the bot
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is running... Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()
