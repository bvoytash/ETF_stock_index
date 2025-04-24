from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
import asyncio
import yfinance as yf
import sqlite3
from datetime import datetime
from db_setup import create_db
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timezone

create_db()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


tickers = ['AAPL', 'MSFT', 'META', 'AMZN', 'GOOGL', 'QCOM', 'AVGO', 'TSLA', 'NVDA', 'AMD', 'ORCL', 'ASML']

TIME_TO_SLEEP = 300  # 5 minutes

def insert_stock_price(timestamp, ticker, price):
    if not isinstance(price, (int, float)):
        print(f"Skipping insert for {ticker}, price is not a float: {price}")
        return

    try:
        conn = sqlite3.connect('stocks.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO stock_prices (timestamp, ticker, price)
            VALUES (?, ?, ?)
        ''', (timestamp, ticker, price))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error inserting stock price into database: {e}")
    finally:
        conn.close()

@app.get("/")
async def get():
    return FileResponse("static/index.html")

@app.websocket("/ws/index")
async def index_ws(websocket: WebSocket):
    await websocket.accept()
    while True:
        prices = get_prices()
        index = calculate_index(prices)

        timestamp = datetime.now(timezone.utc).isoformat()
        for ticker, price in prices.items():
            insert_stock_price(timestamp, ticker, price)
      
        await websocket.send_json({"value": float(index)})
        await asyncio.sleep(TIME_TO_SLEEP)

def get_prices():
    try:
        data = yf.download(tickers, period='1d', interval='5m', progress=False)
        if data.empty:
            print("No data received.")
            return {}

        latest_prices = data['Close'].iloc[-1]
        return {ticker: float(latest_prices[ticker]) for ticker in tickers if ticker in latest_prices}
    except Exception as e:
        print(f"Error fetching stock data: {e}")
        return {}

def calculate_index(prices: dict):
    if prices:
        return sum(prices.values()) / len(prices)
    return 0