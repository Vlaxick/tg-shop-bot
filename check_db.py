import asyncio
from database.db import DB_PATH
import aiosqlite

async def test():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT id, name, price, description FROM products WHERE name = "Поповнення балансу"') as cursor:
            products = await cursor.fetchall()
            for p in products:
                print("Product:", p)

asyncio.run(test())
