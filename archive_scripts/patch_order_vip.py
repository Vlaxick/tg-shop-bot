with open("/Users/macbook/tg-bot/handlers/order_handlers.py", "r") as f:
    content = f.read()

# in process_buy_product
old_buy = """    price = product[3]
    await state.update_data(product_id=product_id, price=price)"""

new_buy = """    price = product[3]
    
    user_id = callback.from_user.id
    stats = await db.get_user_stats(user_id)
    spent = stats[1] if stats else 0.0
    from database.db import get_vip_rank
    rank_name, discount = get_vip_rank(spent)
    
    if discount > 0:
        price = round(price * (1 - discount), 2)
        
    await state.update_data(product_id=product_id, price=price, original_price=price)"""

content = content.replace(old_buy, new_buy)

with open("/Users/macbook/tg-bot/handlers/order_handlers.py", "w") as f:
    f.write(content)
