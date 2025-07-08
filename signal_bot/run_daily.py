#!/usr/bin/env python3
import sys
import os
import logging
from datetime import datetime
import traceback

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from signal import StockSignalGenerator
from telegram_bot import TelegramBot, create_bot_from_env

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('signal_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DailySignalBot:
    def __init__(self):
        self.generator = None
        self.telegram_bot = None
        self.setup_components()

    def setup_components(self):
        try:
            symbols = [
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'INFY.NS',
            'HINDUNILVR.NS', 'ITC.NS', 'BHARTIARTL.NS', 'ASIANPAINT.NS', 'LT.NS',
            'SBIN.NS', 'AXISBANK.NS', 'KOTAKBANK.NS', 'BAJFINANCE.NS', 'SUNPHARMA.NS',
            'TITAN.NS', 'TECHM.NS', 'ULTRACEMCO.NS', 'POWERGRID.NS', 'NTPC.NS',
            'MARUTI.NS', 'NESTLEIND.NS', 'TATAMOTORS.NS', 'TATASTEEL.NS', 'WIPRO.NS',
            'M&M.NS', 'BAJAJ-AUTO.NS', 'DRREDDY.NS', 'CIPLA.NS', 'INDUSINDBK.NS'
            ]


            self.generator = StockSignalGenerator(symbols)
            logger.info(f"Signal generator initialized with {len(symbols)} symbols")

            self.telegram_bot = create_bot_from_env()
            if not self.telegram_bot:
                logger.error("Failed to initialize Telegram bot")
                return False

            if self.telegram_bot.test_connection():
                logger.info("Telegram bot connection successful")
            else:
                logger.error("Telegram bot connection failed")
                return False
            return True
        except Exception as e:
            logger.error(f"Error setting up components: {str(e)}")
            return False

    def run_daily_signals(self):
        try:
            logger.info("Starting daily signal generation...")
            signals = self.generator.generate_all_signals()
            if not signals:
                logger.warning("No signals generated")
                error_msg = "No signals were generated today. Please check the signal generator."
                self.telegram_bot.send_error_notification(error_msg)
                return False

            formatted_message = self.generator.format_signals_message()
            success = self.telegram_bot.send_signal_message(signals, formatted_message)

            if success:
                logger.info(f"Daily signals sent successfully for {len(signals)} symbols")
                return True
            else:
                logger.error("Failed to send signals to Telegram")
                return False
        except Exception as e:
            logger.error(f"Error in daily signal execution: {str(e)}")
            logger.error(traceback.format_exc())
            if self.telegram_bot:
                self.telegram_bot.send_error_notification(str(e))
            return False

    def send_startup_message(self):
        try:
            message = "🚀 *AI Signal Bot Started*\n\n"
            message += f"⏰ Started at: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
            message += "🔄 Daily signals will be generated automatically\n"
            message += "📊 Monitoring Indian stock market signals\n\n"
            message += "✅ Bot is running successfully!"
            self.telegram_bot.send_message(message)
            logger.info("Startup message sent")
        except Exception as e:
            logger.error(f"Error sending startup message: {str(e)}")

def main():
    logger.info("="*50)
    logger.info("AI Signal Bot - Daily Execution Started")
    logger.info("="*50)

    try:
        bot = DailySignalBot()
        if not bot.generator or not bot.telegram_bot:
            logger.error("Failed to initialize bot components")
            sys.exit(1)

        bot.send_startup_message()
        success = bot.run_daily_signals()

        if success:
            logger.info("Daily signal execution completed successfully")
            sys.exit(0)
        else:
            logger.error("Daily signal execution failed")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Bot execution interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
