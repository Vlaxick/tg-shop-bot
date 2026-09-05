import sqlite3
conn = sqlite3.connect('/Users/macbook/tg-bot/shop.db')
c = conn.cursor()
desc = """Додам у сім'ю, підписка Gemini AI Pro (і всі її переваги).

🌟 <b>Що дає підписка:</b>
• Доступ до <b>Gemini Advanced</b> (найрозумніша модель 1.5 Pro).
• <b>5 ТБ</b> місця у вашому Google Drive та Google Фото.
• <b>YouTube Premium Lite</b> (відео без набридливої реклами).
• Підвищені ліміти запитів до Gemini.
• Можливість <b>генерації відео</b> та зображень.
• Інтеграція штучного інтелекту в Gmail, Docs, Sheets.
• Аналіз величезних документів (до 1500 сторінок) і коду.

❌ Звичайна ціна: 12599 ₴
✅ <b>Ціна зі знижкою: 299 ₴</b>"""
c.execute("UPDATE products SET description = ? WHERE category_id = 3", (desc,))
conn.commit()
conn.close()
