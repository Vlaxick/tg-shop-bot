
with open("/Users/macbook/tg-bot/handlers/order_handlers.py", "r") as f:
    content = f.read()

old_proof = """async def process_payment_proof(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    order_id = data.get('order_id')"""

new_proof = """async def process_payment_proof(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    order_id = data.get('order_id')
    balance_to_deduct = data.get('balance_to_deduct')
    original_price = data.get('original_price')"""

if "balance_to_deduct = data.get('balance_to_deduct')" not in content:
    content = content.replace(old_proof, new_proof)

old_body = """    await message.answer("✅ <b>Дякуємо!</b>\\nВаша оплата перевіряється адміністратором. Ви отримаєте сповіщення про зміну статусу.", parse_mode="HTML")
    await state.clear()
    
    admin_text = (
        f"🚨 <b>Нове замовлення #{order_id}</b>\\n\\n"
        f"👤 Клієнт: @{order[2]} (ID: {order[1]})\\n"
        f"📞 Отримувач: {order[3]}\\n"
        f"🛒 Товар: {order[4]}\\n"
        f"💰 Сума: {order[5]} ₴"
    )"""

new_body = """    user_id = message.from_user.id
    if balance_to_deduct:
        success = await db.deduct_balance(user_id, balance_to_deduct)
        if not success:
            await message.answer("❌ Помилка списання балансу! Будь ласка, зверніться до підтримки.")
            return

    await message.answer("✅ <b>Дякуємо!</b>\\nВаша оплата перевіряється адміністратором. Ви отримаєте сповіщення про зміну статусу.", parse_mode="HTML")
    await state.clear()
    
    if balance_to_deduct and original_price:
        price_info = (
            f"💰 Загальна ціна: <b>{original_price} ₴</b>\\n"
            f"💳 З них сплачено з балансу: <b>{balance_to_deduct} ₴</b>\\n"
            f"💵 Сплачено на карту: <b>{order[5]} ₴</b>"
        )
    else:
        price_info = f"💰 Сума (карта): <b>{order[5]} ₴</b>"
        
    admin_text = (
        f"🚨 <b>Нове замовлення #{order_id}</b>\\n\\n"
        f"👤 Клієнт: @{order[2]} (ID: {order[1]})\\n"
        f"📞 Отримувач: {order[3]}\\n"
        f"🛒 Товар: {order[4]}\\n"
        f"{price_info}"
    )"""

content = content.replace(old_body, new_body)

with open("/Users/macbook/tg-bot/handlers/order_handlers.py", "w") as f:
    f.write(content)
