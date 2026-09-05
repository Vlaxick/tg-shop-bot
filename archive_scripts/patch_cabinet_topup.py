with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "r") as f:
    content = f.read()

old_cabinet_kb = """    builder.row(
        InlineKeyboardButton(text="💳 Подарувати баланс (Створити промокод)", callback_data="create_gift")
    )"""

new_cabinet_kb = """    builder.row(
        InlineKeyboardButton(text="💳 Подарувати баланс", callback_data="create_gift"),
        InlineKeyboardButton(text="💵 Поповнити", callback_data="topup_balance")
    )"""

content = content.replace(old_cabinet_kb, new_cabinet_kb)

with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "w") as f:
    f.write(content)
