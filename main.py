from fastapi import FastAPI, WebSocket
from uvicorn import run
from fastapi.responses import FileResponse
import asyncio
import yfinance as yf
import sqlite3
from datetime import datetime
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from db_setup import get_database, stock_prices


database = get_database()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()


tickers = ['AAPL', 'MSFT', 'META', 'AMZN', 'GOOGL', 'QCOM', 'AVGO', 'TSLA', 'NVDA', 'AMD', 'ORCL', 'ASML']

TIME_TO_SLEEP = 300  # 5 minutes

async def insert_stock_price(timestamp, ticker, price):
    if not isinstance(price, (int, float)):
        print(f"Skipping insert for {ticker}, price is not a float: {price}")
        return

    try:
        query = stock_prices.insert().values(timestamp=timestamp, ticker=ticker, price=price)
        await database.execute(query)
    except Exception as e:
        print(f"Error inserting stock price into PostgreSQL: {e}")

@app.get("/")
async def get():
    return FileResponse("static/index.html")

@app.websocket("/ws/index")
async def index_ws(websocket: WebSocket):
    await websocket.accept()
    while True:
        prices = get_prices()
        index = calculate_index(prices)

        timestamp = datetime.now(timezone.utc)
        for ticker, price in prices.items():
            await insert_stock_price(timestamp, ticker, price)
      
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


if __name__ == "__main__":
    run(
        "main:app", host="0.0.0.0", port=8000, workers=4, 
        #reload=True
    )  # remove reload when finished with testing