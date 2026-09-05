with open("/Users/macbook/tg-bot/keyboards/inline.py", "r") as f:
    content = f.read()

old_main = """    builder.row(
        InlineKeyboardButton(text="⭐️ Відгуки", url="https://t.me/your_channel_or_post"),
        InlineKeyboardButton(text="👤 Мій профіль", callback_data="cabinet")
    )"""

new_main = """    builder.row(
        InlineKeyboardButton(text="⭐️ Відгуки", url="https://t.me/your_channel_or_post"),
        InlineKeyboardButton(text="👤 Мій профіль", callback_data="cabinet")
    )
    builder.row(
        InlineKeyboardButton(text="🎰 Казино", callback_data="casino")
    )"""

content = content.replace(old_main, new_main)

# Add casino keyboard
casino_kb = """
def get_casino_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Поставити 10 ₴", callback_data="bet_10"),
        InlineKeyboardButton(text="Поставити 50 ₴", callback_data="bet_50")
    )
    builder.row(InlineKeyboardButton(text="Поставити 100 ₴", callback_data="bet_100"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu", style="danger"))
    return builder.as_markup()
"""

if "def get_casino_keyboard" not in content:
    content = content + "\n" + casino_kb

with open("/Users/macbook/tg-bot/keyboards/inline.py", "w") as f:
    f.write(content)
