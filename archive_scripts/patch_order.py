
with open("/Users/macbook/tg-bot/handlers/order_handlers.py", "r") as f:
    content = f.read()

replacement1 = """    user_data = await db.get_user(user.id)
    balance = user_data[3] if user_data else 0.0
    
    markup = get_payment_method_keyboard(price, category_id, balance)"""

content = content.replace("    markup = get_payment_method_keyboard(price, category_id)", replacement1)

# Add pay_balance logic
replacement2 = """@router.callback_query(F.data == "pay_balance", OrderState.waiting_for_payment_method)
async def process_pay_balance(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    order_id = data['order_id']
    price = data['price']
    
    success = await db.deduct_balance(callback.from_user.id, price)
    if not success:
        await callback.answer("❌ Недостатньо коштів на балансі!", show_alert=True)
        return
        
    await db.update_order_status(order_id, "paid")
    await callback.message.edit_text("✅ <b>Оплата успішна!</b>\n\nКошти списано з балансу. Очікуйте на видачу товару.", parse_mode="HTML")
    await state.clear()
    
    # Notify Admin
    order = await db.get_order(order_id)
    admin_text = (
        f"💰 <b>Нова оплата з балансу!</b>\n"
        f"🆔 Замовлення: #{order_id}\n"
        f"👤 Користувач: @{order[2]}\n"
        f"🛍 Товар: {order[4]}\n"
        f"💵 Сума: {price} ₴"
    )
    from keyboards.inline import get_admin_order_keyboard
    from config import ADMIN_IDS
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_text, reply_markup=get_admin_order_keyboard(order_id, callback.from_user.id), parse_mode="HTML")
        except Exception:
            pass

@router.callback_query(F.data == "pay_card", OrderState.waiting_for_payment_method)"""

content = content.replace("@router.callback_query(F.data == \"pay_card\", OrderState.waiting_for_payment_method)", replacement2)

with open("/Users/macbook/tg-bot/handlers/order_handlers.py", "w") as f:
    f.write(content)
