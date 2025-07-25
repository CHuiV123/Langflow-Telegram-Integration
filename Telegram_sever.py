from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import requests
import os

# Langflow configuration
BASE_API_URL = "http://127.0.0.1:7860"
FLOW_ID = "fb1c9a4e-a54a-4659-8282-8b61900fb07d"
ENDPOINT = ""  # Optional: use if you've defined a named endpoint

# Read Langflow API key from environment
LANGFLOW_API_KEY = os.environ.get("LANGFLOW_API_KEY")
if not LANGFLOW_API_KEY:
    raise ValueError("LANGFLOW_API_KEY environment variable not found.")

# Telegram bot token from environment
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not found.")

# Function to send user message to Langflow
def run_flow(message: str) -> dict:
    api_url = f"{BASE_API_URL}/api/v1/run/{ENDPOINT or FLOW_ID}"

    payload = {
        "input_value": message,
        "output_type": "chat",
        "input_type": "chat",
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": LANGFLOW_API_KEY,
    }

    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Request error: {e}"}

# Function to extract the message from Langflow response
def extract_message(response: dict) -> str:
    if "error" in response:
        return response["error"]
    
    try:
        return response['outputs'][0]['outputs'][0]['results']['message']['text']
    except (KeyError, IndexError):
        return "No valid message found in response."

# Telegram message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    flow_response = run_flow(user_text)
    reply_text = extract_message(flow_response)

    await update.message.reply_text(reply_text)

# Start the Telegram bot
def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot is running... Press Ctrl+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()
