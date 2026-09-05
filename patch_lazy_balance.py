import re

with open("/Users/macbook/tg-bot/handlers/order_handlers.py", "r") as f:
    content = f.read()

# 1. Update pay_balance_partial
old_partial = """    # Deduct balance and update price
    success = await db.deduct_balance(user_id, balance)
    if not success:
        await callback.answer("❌ Помилка списання балансу!", show_alert=True)
        return
        
    new_price = round(price - balance, 2)
    await state.update_data(price=new_price, balance_used=balance)"""

new_partial = """    # Reserve balance in state instead of deducting immediately
    new_price = round(price - balance, 2)
    await state.update_data(price=new_price, balance_to_deduct=balance, original_price=price)"""

content = content.replace(old_partial, new_partial)

# 2. Update process_payment_proof
old_proof = """async def process_payment_proof(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    order_id = data.get('order_id')"""

new_proof = """async def process_payment_proof(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    order_id = data.get('order_id')
    balance_to_deduct = data.get('balance_to_deduct')
    original_price = data.get('original_price')"""

content = content.replace(old_proof, new_proof)

# 2.b Deduct balance in process_payment_proof
# We need to deduct the balance before sending to admin.
old_proof_body = """    await message.answer("✅ <b>Дякуємо!</b>\\nВаша оплата перевіряється адміністратором. Ви отримаєте сповіщення про зміну статусу.", parse_mode="HTML")
    await state.clear()
    
    admin_text = (
        f"🚨 <b>Нове замовлення #{order_id}</b>\\n\\n"
        f"👤 Клієнт: @{order[2]} (ID: {order[1]})\\n"
        f"🛍 Товар: ID {order[4]}\\n"
        f"📝 Контакт/ID/Посилання: <code>{order[3]}</code>\\n\\n"
        f"💰 Очікувана оплата: <b>{order[5]} ₴</b>\\n"
        f"⏳ Статус: Очікує перевірки"
    )"""

new_proof_body = """    # Deduct reserved balance now
    user_id = message.from_user.id
    if balance_to_deduct:
        success = await db.deduct_balance(user_id, balance_to_deduct)
        if not success:
            await message.answer("❌ Помилка списання балансу! Будь ласка, зверніться до підтримки.")
            return

    await message.answer("✅ <b>Дякуємо!</b>\\nВаша оплата перевіряється адміністратором. Ви отримаєте сповіщення про зміну статусу.", parse_mode="HTML")
    await state.clear()
    
    price_info = f"💰 Очікувана оплата на карту: <b>{order[5]} ₴</b>"
    if balance_to_deduct and original_price:
        price_info = (
            f"💰 Загальна ціна: <b>{original_price} ₴</b>\\n"
            f"💳 З них сплачено з балансу: <b>{balance_to_deduct} ₴</b>\\n"
            f"💵 Очікувана оплата на карту: <b>{order[5]} ₴</b>"
        )
    else:
        price_info = f"💰 Очікувана оплата на карту: <b>{order[5]} ₴</b>"

    admin_text = (
        f"🚨 <b>Нове замовлення #{order_id}</b>\\n\\n"
        f"👤 Клієнт: @{order[2]} (ID: {order[1]})\\n"
        f"🛍 Товар: ID {order[4]}\\n"
        f"📝 Контакт/ID/Посилання: <code>{order[3]}</code>\\n\\n"
        f"{price_info}\\n\\n"
        f"⏳ Статус: Очікує перевірки"
    )"""
content = content.replace(old_proof_body, new_proof_body)

# Write back
with open("/Users/macbook/tg-bot/handlers/order_handlers.py", "w") as f:
    f.write(content)

