import re

with open("/Users/macbook/tg-bot/handlers/admin_handlers.py", "r") as f:
    content = f.read()

# In process_admin_approve, intercept "Поповнення балансу"
old_approve = """    # Process Referral Cashback
    order = await db.get_order(order_id)
    if order:
        price = order[5]"""

new_approve = """    # Check if this is a top-up
    order = await db.get_order(order_id)
    if not order:
        return
        
    product_name = order[4]
    price = order[5]
    
    if product_name == "Поповнення балансу":
        await db.add_balance(user_id, price)
        await callback.message.edit_caption(
            caption=callback.message.caption + "\\n\\n✅ <b>Статус:</b> Підтверджено (Баланс поповнено)",
            parse_mode="HTML"
        )
        await callback.answer("Баланс поповнено!")
        try:
            await bot.send_message(
                chat_id=user_id,
                text=f"✅ <b>Ваш баланс успішно поповнено на {price} ₴!</b>",
                parse_mode="HTML"
            )
        except:
            pass
        return

    # Process Referral Cashback"""

content = content.replace(old_approve, new_approve)

with open("/Users/macbook/tg-bot/handlers/admin_handlers.py", "w") as f:
    f.write(content)
