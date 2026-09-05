import sqlite3

conn = sqlite3.connect('/Users/macbook/tg-bot/shop.db')
c = conn.cursor()
desc = """Додам у сім'ю, підписка Gemini AI Pro (і всі її переваги).

❌ Звичайна ціна: 12599 ₴
✅ Ціна зі знижкою: 299 ₴"""
c.execute("UPDATE products SET description = ? WHERE category_id = 3", (desc,))
conn.commit()
conn.close()
