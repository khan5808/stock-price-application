import sqlite3

def init_db():
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticker TEXT,
            predicted_price REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

def save_prediction(ticker, price):
    conn = sqlite3.connect('stocks.db')
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO predictions (ticker, predicted_price) VALUES (?, ?)",
        (ticker, price)
    )

    conn.commit()
    conn.close()


