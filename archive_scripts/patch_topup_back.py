
with open("/Users/macbook/tg-bot/keyboards/inline.py", "r") as f:
    content = f.read()

old_payment_kb = """def get_payment_method_keyboard(price: float, category_id: int, balance: float = 0.0, is_partial: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if balance >= price and not is_partial:
        builder.row(InlineKeyboardButton(text=f"💰 Оплатити з балансу ({balance} ₴)", callback_data="pay_balance"))
    elif balance > 0 and not is_partial:
        builder.row(InlineKeyboardButton(text=f"💰 Списати баланс ({balance} ₴)", callback_data="pay_balance_partial"))
    
    builder.row(InlineKeyboardButton(text=f"🖤 Monobank (Apple Pay) — {price} ₴", callback_data="pay_card"))
    builder.row(InlineKeyboardButton(text="💎 Крипта (CryptoBot)", callback_data="pay_crypto"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"cat_{category_id}", style="danger"))
    return builder.as_markup()"""

new_payment_kb = """def get_payment_method_keyboard(price: float, category_id: int, balance: float = 0.0, is_partial: bool = False, back_cb: str = None) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    price_str = f"{price:.2f}".rstrip('0').rstrip('.')
    balance_str = f"{balance:.2f}".rstrip('0').rstrip('.')
    
    if balance >= price and not is_partial:
        builder.row(InlineKeyboardButton(text=f"💰 Оплатити з балансу ({balance_str} ₴)", callback_data="pay_balance"))
    elif balance > 0 and not is_partial:
        builder.row(InlineKeyboardButton(text=f"💰 Списати баланс ({balance_str} ₴)", callback_data="pay_balance_partial"))
    
    builder.row(InlineKeyboardButton(text=f"🖤 Monobank (Apple Pay) — {price_str} ₴", callback_data="pay_card"))
    builder.row(InlineKeyboardButton(text="💎 Крипта (CryptoBot)", callback_data="pay_crypto"))
    
    if not back_cb:
        back_cb = "cabinet" if category_id == 0 else f"cat_{category_id}"
    
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data=back_cb, style="danger"))
    return builder.as_markup()"""

content = content.replace(old_payment_kb, new_payment_kb)

with open("/Users/macbook/tg-bot/keyboards/inline.py", "w") as f:
    f.write(content)

