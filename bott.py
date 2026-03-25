import asyncio
import requests
import pandas as pd
from telegram import Bot

# 
import os

TOKEN = os.environ["TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

bot = Bot(token=TOKEN)

# Fetch recent BTC/USDT closing prices
def get_prices():
    url = "https://api.binance.com/api/v3/klines?symbol=BTCUSDT&interval=1m&limit=50"
    data = requests.get(url).json()
    closes = [float(candle[4]) for candle in data]  # Close prices
    return closes

# Calculate RSI
def calculate_rsi(prices, period=14):
    series = pd.Series(prices)
    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi.iloc[-1]

# Async function to send signal
async def send_signal():
    prices = get_prices()
    rsi = calculate_rsi(prices)
    current_price = prices[-1]

    if rsi < 30:
        signal = "BUY 🚀"
        sl = current_price * 0.99  
        tp = current_price * 1.02  

    elif rsi > 70:
        signal = "SELL 🔻"
        sl = current_price * 1.01   
        tp = current_price * 0.98  

    else:
        return # Do nothing if RSI neutral

   
    message = f"""
 BTC/USDT SIGNAL

Type: {signal}
Price: {round(current_price, 2)}
RSI: {round(rsi, 2)}
Timeframe: 1m

🎯 TP: {round(tp, 2)}
🛑 SL: {round(sl, 2)}
"""

    await bot.send_message(chat_id=CHAT_ID, text=message)

# Run the async function
import time
import asyncio

async def main_loop():
    while True:
        await send_signal()
        await asyncio.sleep(60)  # Wait 60 seconds before next signal

asyncio.run(main_loop())
