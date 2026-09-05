import sqlite3
conn = sqlite3.connect('/Users/macbook/tg-bot/shop.db')
c = conn.cursor()
desc = """Додам у сім'ю, підписка Gemini AI Pro (і всі її переваги).

🌟 <b>Що дає підписка:</b>
• Доступ до <b>Gemini Advanced</b> (найрозумніша модель Google 1.5 Pro).
• <b>2 ТБ</b> місця у вашому Google Drive та Google Фото.
• Інтеграція штучного інтелекту в <b>Gmail, Docs, Sheets, Slides та Meet</b>.
• Завантаження та аналіз величезних документів (до 1500 сторінок) і коду.
• Пріоритетний доступ до всіх нових ШІ-функцій від Google.
• Абсолютно приватна робота з вашим власним акаунтом.

❌ Звичайна ціна: 12599 ₴
✅ <b>Ціна зі знижкою: 299 ₴</b>"""
c.execute("UPDATE products SET description = ? WHERE category_id = 3", (desc,))
conn.commit()
conn.close()
