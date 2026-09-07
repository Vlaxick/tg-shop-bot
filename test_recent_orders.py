import asyncio
from database.db import DB_PATH
import aiosqlite

async def test():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT o.id, o.user_id, o.username, o.contact_info, p.name, p.price, o.status, p.category_id, o.created_at FROM orders o JOIN products p ON o.product_id = p.id ORDER BY o.id DESC LIMIT 5') as cursor:
            orders = await cursor.fetchall()
            for order in orders:
                print("Order:", order)

asyncio.run(test())
