import asyncio
from aiogram import Bot
from config import BOT_TOKEN, ADMIN_IDS
from keyboards.inline import get_admin_action_keyboard

async def test():
    bot = Bot(token=BOT_TOKEN)
    order_id = 28
    user_id = 5927166969
    username = "vlaioxss"
    contact_info = "Поповнення"
    product_name = "Поповнення балансу"
    price = 50.0
    
    o5_str = f"{price:.2f}".rstrip('0').rstrip('.')
    price_info = f"💰 Сума (карта): <b>{o5_str} ₴</b>"
    
    admin_text = (
        f"🚨 <b>Нове замовлення #{order_id}</b>\n\n"
        f"👤 Клієнт: @{username} (ID: {user_id})\n"
        f"📞 Отримувач: {contact_info}\n"
        f"🛒 Товар: {product_name}\n"
        f"{price_info}"
    )
    
    photo_id = "AgACAgIAAxkBAAIJ1WbS-jV65iXl_u_6_y3G3QAB9O1l-gACGtoAMwABR0l09QABR0l09QABR0l09Q" # Fake photo ID from random
    # Actually, I can just send a message instead of a photo to test the markup parsing.
    
    try:
        await bot.send_message(
            chat_id=ADMIN_IDS[0],
            text=admin_text,
            reply_markup=get_admin_action_keyboard(order_id, user_id),
            parse_mode="HTML"
        )
        print("Success")
    except Exception as e:
        print("Exception:", e)
    
    await bot.session.close()

asyncio.run(test())
