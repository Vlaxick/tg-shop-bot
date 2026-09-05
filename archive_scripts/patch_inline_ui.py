import re
with open("/Users/macbook/tg-bot/keyboards/inline.py", "r") as f:
    content = f.read()

# 1. Main menu
old_main = """    builder.row(
        InlineKeyboardButton(text="🎁 Реферали та Баланс", callback_data="referrals")
    )
    builder.row(
        InlineKeyboardButton(text="ℹ️ Підтримка / Правила", callback_data="support", style="primary")
    )"""

new_main = """    builder.row(
        InlineKeyboardButton(text="🎁 Реферали", callback_data="referrals"),
        InlineKeyboardButton(text="ℹ️ Підтримка", callback_data="support", style="primary")
    )"""

content = content.replace(old_main, new_main)

# 2. Casino menu (add top up)
old_casino = """    builder.row(InlineKeyboardButton(text="Поставити 100 ₴", callback_data="bet_100"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu", style="danger"))"""

new_casino = """    builder.row(InlineKeyboardButton(text="Поставити 100 ₴", callback_data="bet_100"))
    builder.row(InlineKeyboardButton(text="💳 Поповнити баланс", callback_data="topup_balance", style="success"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu", style="danger"))"""

content = content.replace(old_casino, new_casino)

with open("/Users/macbook/tg-bot/keyboards/inline.py", "w") as f:
    f.write(content)
