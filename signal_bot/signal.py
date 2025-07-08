import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockSignalGenerator:
    def __init__(self, symbols=['SUZLON.NS', '^NSEI']):
        """ Initialize with stock symbols """
        self.symbols = symbols
        self.signals = {}

    def calculate_rsi(self, prices, period=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def calculate_ema(self, prices, period=20):
        return prices.ewm(span=period).mean()

    def generate_signal(self, symbol):
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            stock = yf.Ticker(symbol)
            data = stock.history(start=start_date, end=end_date)
            if data.empty:
                logger.error(f"No data found for {symbol}")
                return None

            data['RSI'] = self.calculate_rsi(data['Close'])
            data['EMA_20'] = self.calculate_ema(data['Close'], 20)
            data['EMA_50'] = self.calculate_ema(data['Close'], 50)

            latest_data = data.iloc[-1]
            current_price = latest_data['Close']
            rsi = latest_data['RSI']
            ema_20 = latest_data['EMA_20']
            ema_50 = latest_data['EMA_50']

            if rsi < 30 and current_price > ema_20:
                signal = "BUY"
                reason = f"RSI oversold ({rsi:.2f}) + Price above EMA20"
            elif rsi > 70 and current_price < ema_20:
                signal = "SELL"
                reason = f"RSI overbought ({rsi:.2f}) + Price below EMA20"
            elif current_price > ema_50 and ema_20 > ema_50:
                signal = "HOLD (Bullish)"
                reason = "Price above EMA50 and uptrend"
            else:
                signal = "HOLD"
                reason = "No clear signal"

            signal_data = {
                'symbol': symbol,
                'price': current_price,
                'rsi': rsi,
                'ema_20': ema_20,
                'ema_50': ema_50,
                'signal': signal,
                'reason': reason,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            logger.info(f"Generated signal for {symbol}: {signal}")
            return signal_data
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {str(e)}")
            return None

    def generate_all_signals(self):
        logger.info("Generating signals for all symbols...")
        for symbol in self.symbols:
            signal_data = self.generate_signal(symbol)
            if signal_data:
                self.signals[symbol] = signal_data
        return self.signals

    def format_signals_message(self):
        if not self.signals:
            return "No signals generated today."

        message = "🤖 *AI Stock Signals - Daily Update*\n\n"
        message += f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}\n"
        message += "=" * 35 + "\n\n"
        for symbol, data in self.signals.items():
            display_symbol = symbol.replace('.NS', '')
            message += f"📊 *{display_symbol}*\n"
            message += f"💰 Price: ₹{data['price']:.2f}\n"
            message += f"📈 RSI: {data['rsi']:.2f}\n"
            message += f"🎯 Signal: *{data['signal']}*\n"
            message += f"📝 Reason: {data['reason']}\n"
            message += "-" * 25 + "\n\n"
        message += "⚠️ *Disclaimer:* Signals are for educational purposes only. Please do your own research before trading.\n"
        message += "🔄 Next update: Tomorrow at 9:30 AM"
        return message

def main():
    generator = StockSignalGenerator(['SUZLON.NS', '^NSEI', 'RELIANCE.NS'])
    signals = generator.generate_all_signals()
    message = generator.format_signals_message()
    print(message)
    return signals, message

if __name__ == "__main__":
    main()
