
with open("/Users/macbook/tg-bot/handlers/order_handlers.py", "r") as f:
    content = f.read()

# Replace any occurrence of {price}, {balance}, {new_price} with formatted version
# Actually, it's safer to just find the f-strings and format them.
# In process_buy_product:
old_contact = """    text = (
        "📞 <b>Крок 2: Введіть дані для отримання</b>\\n\\n"
        "Напишіть посилання на акаунт, ID або номер телефону, "
        "на який потрібно видати товар:\\n\\n"
        "(Або натисніть /cancel для скасування)"
    )"""

# In process_contact:
old_pay_method = """    text = (
        f"💳 <b>Оберіть спосіб оплати:</b>"
    )"""

old_pay_partial = """    text_partial = (
        f"✅ <b>Баланс списано!</b> ({balance} ₴)\\n\\n"
        f"Залишилось доплатити: <b>{new_price} ₴</b>\\n"
        "Оберіть спосіб доплати:"
    )"""

new_pay_partial = """    bal_str = f"{balance:.2f}".rstrip('0').rstrip('.')
    np_str = f"{new_price:.2f}".rstrip('0').rstrip('.')
    text_partial = (
        f"✅ <b>Баланс списано!</b> ({bal_str} ₴)\\n\\n"
        f"Залишилось доплатити: <b>{np_str} ₴</b>\\n"
        "Оберіть спосіб доплати:"
    )"""

content = content.replace(old_pay_partial, new_pay_partial)

old_price_info = """    if balance_to_deduct and original_price:
        price_info = (
            f"💰 Загальна ціна: <b>{original_price} ₴</b>\\n"
            f"💳 З них сплачено з балансу: <b>{balance_to_deduct} ₴</b>\\n"
            f"💵 Сплачено на карту: <b>{order[5]} ₴</b>"
        )
    else:
        price_info = f"💰 Сума (карта): <b>{order[5]} ₴</b>"
"""

new_price_info = """    if balance_to_deduct and original_price:
        op_str = f"{original_price:.2f}".rstrip('0').rstrip('.')
        bd_str = f"{balance_to_deduct:.2f}".rstrip('0').rstrip('.')
        o5_str = f"{order[5]:.2f}".rstrip('0').rstrip('.')
        price_info = (
            f"💰 Загальна ціна: <b>{op_str} ₴</b>\\n"
            f"💳 З них сплачено з балансу: <b>{bd_str} ₴</b>\\n"
            f"💵 Сплачено на карту: <b>{o5_str} ₴</b>"
        )
    else:
        o5_str = f"{order[5]:.2f}".rstrip('0').rstrip('.')
        price_info = f"💰 Сума (карта): <b>{o5_str} ₴</b>"
"""

content = content.replace(old_price_info, new_price_info)

with open("/Users/macbook/tg-bot/handlers/order_handlers.py", "w") as f:
    f.write(content)

