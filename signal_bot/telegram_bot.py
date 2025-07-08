import requests
import logging
from datetime import datetime
import os
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{bot_token}"

    def send_message(self, message: str, parse_mode: str = "Markdown") -> bool:
        try:
            url = f"{self.api_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode,
                'disable_web_page_preview': True
            }
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                logger.info("Message sent successfully to Telegram")
                return True
            else:
                logger.error(f"Failed to send message: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error sending message to Telegram: {str(e)}")
            return False

    def send_signal_message(self, signals_data: dict, formatted_message: str) -> bool:
        try:
            header = f"🚀 *AI Trading Signals Alert*\n"
            header += f"⏰ {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
            full_message = header + formatted_message
            success = self.send_message(full_message)
            if success:
                logger.info(f"Signal message sent successfully for {len(signals_data)} symbols")
                return True
        except Exception as e:
            logger.error(f"Error sending signal message: {str(e)}")
        return False

    def send_error_notification(self, error_msg: str) -> bool:
        try:
            message = f"🚨 *AI Signal Bot Error*\n\n"
            message += f"❌ Error: {error_msg}\n"
            message += f"⏰ Time: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n"
            message += "Please check the bot logs for more details."
            return self.send_message(message)
        except Exception as e:
            logger.error(f"Error sending error notification: {str(e)}")
            return False

    def test_connection(self) -> bool:
        try:
            url = f"{self.api_url}/getMe"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info['ok']:
                    logger.info(f"Bot connection successful: {bot_info['result']['first_name']}")
                    return True
            logger.error(f"Bot connection failed: {response.status_code}")
            return False
        except Exception as e:
            logger.error(f"Error testing bot connection: {str(e)}")
            return False

def create_bot_from_env() -> Optional[TelegramBot]:
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    if not bot_token or not chat_id:
        logger.error("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID environment variables")
        return None
    return TelegramBot(bot_token, chat_id)

def main():
    BOT_TOKEN = "your_bot_token_here"
    CHAT_ID = "your_chat_id_here"
    bot = TelegramBot(BOT_TOKEN, CHAT_ID)
    if bot.test_connection():
        test_message = "🤖 *Test Message*\n\nTelegram bot is working correctly!"
        success = bot.send_message(test_message)
        if success:
            print("✅ Test message sent successfully!")
        else:
            print("❌ Failed to send test message")
    else:
        print("❌ Bot connection failed")

if __name__ == "__main__":
    main()
