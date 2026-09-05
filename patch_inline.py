import re

with open("/Users/macbook/tg-bot/keyboards/inline.py", "r") as f:
    content = f.read()

new_main_menu = """def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🛍 Магазин", callback_data="shop", style="success"),
        InlineKeyboardButton(text="📦 Мої замовлення", callback_data="my_orders", style="primary")
    )
    builder.row(
        InlineKeyboardButton(text="⭐️ Відгуки", url="https://t.me/your_channel_or_post"),
        InlineKeyboardButton(text="👤 Мій профіль", callback_data="cabinet")
    )
    builder.row(
        InlineKeyboardButton(text="ℹ️ Підтримка / Правила", callback_data="support", style="primary")
    )
    return builder.as_markup()"""

start = content.find("def get_main_menu_keyboard()")
end = content.find("def get_categories_keyboard")
content = content[:start] + new_main_menu + "\n\n" + content[end:]

with open("/Users/macbook/tg-bot/keyboards/inline.py", "w") as f:
    f.write(content)
