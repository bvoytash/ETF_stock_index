import sqlite3

def create_db():
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_prices (
            id INTEGER PRIMARY KEY,
            timestamp DATETIME,
            ticker TEXT,
            price REAL
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_db()