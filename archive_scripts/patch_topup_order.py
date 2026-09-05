with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "r") as f:
    content = f.read()

old_start = """async def _start_topup_payment(message: Message, user, amount: float, state: FSMContext, callback: CallbackQuery = None):
    # Create custom product for topup
    product_id = await db.get_or_create_custom_product("Поповнення балансу", amount)
    
    # We pretend this is a normal order
    await state.update_data(product_id=product_id, price=amount, original_price=amount, balance_to_deduct=0)"""

new_start = """async def _start_topup_payment(message: Message, user, amount: float, state: FSMContext, callback: CallbackQuery = None):
    # Create custom product for topup
    product_id = await db.get_or_create_custom_product("Поповнення балансу", amount)
    
    import hashlib
    order_id = await db.create_order(user.id, user.username or str(user.id), "Поповнення", product_id)
    order_hash = hashlib.md5(f"{order_id}_{user.id}".encode()).hexdigest()[:8]
    
    # We pretend this is a normal order
    await state.update_data(
        product_id=product_id, 
        price=amount, 
        original_price=amount, 
        balance_to_deduct=0,
        order_id=order_id,
        order_hash=order_hash,
        product_name="Поповнення балансу",
        contact_info="Поповнення"
    )"""

content = content.replace(old_start, new_start)

with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "w") as f:
    f.write(content)
