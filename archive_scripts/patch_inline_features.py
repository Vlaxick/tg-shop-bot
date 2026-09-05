with open("/Users/macbook/tg-bot/keyboards/inline.py", "r") as f:
    content = f.read()

# Add FAQ keyboard
faq_kb = """
def get_faq_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="❓ Як довго видається товар?", callback_data="faq_delivery"))
    builder.row(InlineKeyboardButton(text="❓ Чи безпечно купувати Telegram Stars?", callback_data="faq_safety"))
    builder.row(InlineKeyboardButton(text="❓ Як використати баланс?", callback_data="faq_balance"))
    builder.row(InlineKeyboardButton(text="✍️ Написати адміну", url="https://t.me/your_admin_username"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu", style="danger"))
    return builder.as_markup()
"""

if "def get_faq_keyboard()" not in content:
    content = content + faq_kb

with open("/Users/macbook/tg-bot/keyboards/inline.py", "w") as f:
    f.write(content)
