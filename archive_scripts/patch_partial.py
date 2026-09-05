
with open("/Users/macbook/tg-bot/handlers/order_handlers.py", "r") as f:
    content = f.read()

# Add pay_balance_partial
new_partial = """@router.callback_query(F.data == "pay_balance_partial", OrderState.waiting_for_payment_method)
async def process_pay_balance_partial(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    order_id = data['order_id']
    price = data['price']
    category_id = data.get('category_id', 1)
    
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    balance = user[3] if user else 0.0
    
    if balance <= 0:
        await callback.answer("❌ У вас немає коштів на балансі!", show_alert=True)
        return
        
    # Deduct balance and update price
    success = await db.deduct_balance(user_id, balance)
    if not success:
        await callback.answer("❌ Помилка списання балансу!", show_alert=True)
        return
        
    new_price = round(price - balance, 2)
    await state.update_data(price=new_price, balance_used=balance)
    
    from keyboards.inline import get_payment_method_keyboard
    markup = get_payment_method_keyboard(new_price, category_id, balance=0, is_partial=True)
    
    await callback.message.edit_text(
        f"✅ <b>Баланс списано!</b> ({balance} ₴)\\n\\n"
        f"Залишилось доплатити: <b>{new_price} ₴</b>\\n"
        "Оберіть спосіб доплати:",
        reply_markup=markup,
        parse_mode="HTML"
    )
    await callback.answer()

"""

# Insert before pay_card
start = content.find('@router.callback_query(F.data == "pay_card"')
content = content[:start] + new_partial + content[start:]

with open("/Users/macbook/tg-bot/handlers/order_handlers.py", "w") as f:
    f.write(content)
