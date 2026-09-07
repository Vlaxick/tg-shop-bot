import asyncio
import aiosqlite
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "shop.db")

async def restore():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('DELETE FROM categories')
        await db.execute('DELETE FROM products')
        
        cats = [
            (1, '⭐️ Telegram Stars'),
            (2, '💎 Telegram Premium'),
            (3, '🎬 YouTube Premium'),
            (4, '🎁 Telegram Подарунки (NFT)'),
            (5, '🤖 Google Gemini')
        ]
        await db.executemany('INSERT INTO categories (id, name) VALUES (?, ?)', cats)
        
        prods = [
            (1, '50 Stars', 'Пакет 50 зірок', 40.0),
            (1, '100 Stars', 'Пакет 100 зірок', 80.0),
            (1, '250 Stars', 'Пакет 250 зірок', 195.0),
            (1, '500 Stars', 'Пакет 500 зірок', 390.0),
            (2, 'Telegram Premium 1 міс', 'Підписка на 1 місяць', 120.0),
            (2, 'Telegram Premium 3 міс', 'Підписка на 3 місяці', 350.0),
            (3, 'YouTube Premium 1 міс', 'Підписка на 1 місяць', 75.0),
            (4, 'NFT Подарунок', 'Рандомний NFT подарунок', 200.0),
            (5, 'Gemini Advanced 1 міс', 'Доступ до найрозумнішої моделі', 250.0)
        ]
        await db.executemany('INSERT INTO products (category_id, name, description, price) VALUES (?, ?, ?, ?)', prods)
        await db.commit()
        print("Database restored successfully!")

asyncio.run(restore())
