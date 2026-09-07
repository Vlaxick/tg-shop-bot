import asyncio
from database.db import get_order, DB_PATH
import aiosqlite

async def test():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT o.id, o.user_id, o.username, o.contact_info, p.name, p.price, o.status, p.category_id, o.created_at FROM orders o JOIN products p ON o.product_id = p.id ORDER BY o.id DESC LIMIT 1') as cursor:
            order = await cursor.fetchone()
            print("Order:", order)
            if not order: return
            
            order_id = order[0]
            
            o5_str = f"{order[5]:.2f}".rstrip('0').rstrip('.')
            price_info = f"💰 Сума (карта): <b>{o5_str} ₴</b>"
            
            admin_text = (
                f"🚨 <b>Нове замовлення #{order_id}</b>\n\n"
                f"👤 Клієнт: @{order[2]} (ID: {order[1]})\n"
                f"📞 Отримувач: {order[3]}\n"
                f"🛒 Товар: {order[4]}\n"
                f"{price_info}"
            )
            print("Admin text:", admin_text)

asyncio.run(test())
