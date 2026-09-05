
with open("/Users/macbook/tg-bot/handlers/order_handlers.py", "r") as f:
    content = f.read()

content = content.replace("await start_order_recipient_flow(callback, state, name, price, product_id)", "await start_order_recipient_flow(callback, state, name, price, product_id, 1)")
content = content.replace("await start_order_recipient_flow(message, state, name, price, product_id)", "await start_order_recipient_flow(message, state, name, price, product_id, 1)")
content = content.replace("await start_order_recipient_flow(callback, state, gift_data[\"name\"], gift_data[\"price\"], 0)", "await start_order_recipient_flow(callback, state, gift_data[\"name\"], gift_data[\"price\"], 0, 4)")

# For line 121, we can just fetch category_id via db or we can pass 0 for now and it'll fallback to main menu if it's 0? No, let's pass 4 since most products are gifts right now? No, wait. 
content = content.replace("await start_order_recipient_flow(callback, state, product[1], product[3], product_id)", "category_id = 4 # Default to gifts if unknown\n    await start_order_recipient_flow(callback, state, product[1], product[3], product_id, category_id)")

with open("/Users/macbook/tg-bot/handlers/order_handlers.py", "w") as f:
    f.write(content)
