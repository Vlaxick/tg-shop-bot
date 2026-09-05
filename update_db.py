import sqlite3

conn = sqlite3.connect('/Users/macbook/tg-bot/shop.db')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE users ADD COLUMN referral_earnings REAL DEFAULT 0")
    conn.commit()
    print("Added referral_earnings column.")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("Column already exists.")
    else:
        print("Error:", e)

conn.close()
