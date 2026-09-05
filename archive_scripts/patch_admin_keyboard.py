with open("/Users/macbook/tg-bot/handlers/admin_handlers.py", "r") as f:
    content = f.read()

old_admin_msg = """        try:
            await bot.send_message(
                chat_id=user_id,
                text=f"✅ <b>Ваш баланс успішно поповнено на {price} ₴!</b>",
                parse_mode="HTML"
            )
        except:
            pass"""

new_admin_msg = """        try:
            from keyboards.inline import get_back_to_main_keyboard
            p_str = f"{price:.2f}".rstrip('0').rstrip('.')
            await bot.send_message(
                chat_id=user_id,
                text=f"✅ <b>Ваш баланс успішно поповнено на {p_str} ₴!</b>",
                reply_markup=get_back_to_main_keyboard(),
                parse_mode="HTML"
            )
        except:
            pass"""

content = content.replace(old_admin_msg, new_admin_msg)

with open("/Users/macbook/tg-bot/handlers/admin_handlers.py", "w") as f:
    f.write(content)
