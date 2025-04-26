from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, MetaData, Table
from databases import Database
import os
from dotenv import load_dotenv

load_dotenv()

metadata = MetaData()

stock_prices = Table(
    "stock_prices",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("timestamp", DateTime),
    Column("ticker", String),
    Column("price", Float),
)

def get_database():
    DATABASE_URL = os.getenv("DB_EXTERNAL_URL")
    if DATABASE_URL is None:
        raise ValueError("DB_EXTERNAL_URL not set")
    return Database(DATABASE_URL)

def get_engine():
    DATABASE_URL = os.getenv("DB_EXTERNAL_URL")
    if DATABASE_URL is None:
        raise ValueError("DB_EXTERNAL_URL not set")
    return create_engine(str(DATABASE_URL).replace("+asyncpg", ""))