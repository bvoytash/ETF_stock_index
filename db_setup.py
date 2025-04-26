from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, MetaData, Table
from databases import Database
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DB_EXTERNAL_URL")

database = Database(DATABASE_URL)
metadata = MetaData()

stock_prices = Table(
    "stock_prices",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("timestamp", DateTime),
    Column("ticker", String),
    Column("price", Float),
)

engine = create_engine(str(DATABASE_URL).replace("+asyncpg", ""))
metadata.create_all(engine)