with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "r") as f:
    content = f.read()

old_product = """@router.callback_query(F.data.startswith("product_"))
async def process_product(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    product = await db.get_product(product_id)
    if not product:
        await callback.answer("Товар не знайдено.", show_alert=True)
        return
        
    category_id, name, description, price, image_url = product
    
    text = (
        f"🛍 <b>{name}</b>\\n\\n"
        f"📝 {description}\\n\\n"
        f"💰 <b>Ціна:</b> {price} ₴"
    )
    
    from keyboards.inline import get_product_action_keyboard
    await edit_or_send_photo(callback, text, get_product_action_keyboard(product_id, category_id))
    await callback.answer()"""

new_product = """@router.callback_query(F.data.startswith("product_"))
async def process_product(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    product = await db.get_product(product_id)
    if not product:
        await callback.answer("Товар не знайдено.", show_alert=True)
        return
        
    category_id, name, description, price, image_url = product
    
    user_id = callback.from_user.id
    stats = await db.get_user_stats(user_id)
    spent = stats[1] if stats else 0.0
    from database.db import get_vip_rank
    rank_name, discount = get_vip_rank(spent)
    
    if discount > 0:
        new_price = round(price * (1 - discount), 2)
        price_text = f"💰 <b>Ціна:</b> <s>{price} ₴</s> <b>{new_price} ₴</b> <i>({rank_name} знижка)</i>"
    else:
        price_text = f"💰 <b>Ціна:</b> {price} ₴"
    
    text = (
        f"🛍 <b>{name}</b>\\n\\n"
        f"📝 {description}\\n\\n"
        f"{price_text}"
    )
    
    from keyboards.inline import get_product_action_keyboard
    await edit_or_send_photo(callback, text, get_product_action_keyboard(product_id, category_id))
    await callback.answer()"""

content = content.replace(old_product, new_product)

with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "w") as f:
    f.write(content)
