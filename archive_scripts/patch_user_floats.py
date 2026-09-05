with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "r") as f:
    content = f.read()

# Fix process_casino_menu
old_casino = """    text = (
        "🎰 <b>Вітаємо в Казино!</b>\\n\\n"
        "Правила прості: ви робите ставку і крутите слоти.\\n"
        "Виграшні комбінації (3 в ряд):\\n"
        "🍒🍒🍒 або 🍋🍋🍋 = <b>x5</b> від ставки\\n"
        "💎💎💎 = <b>Джекпот (x10)</b>\\n\\n"
        f"Ваш баланс: <b>{balance} ₴</b>\\n"
        "Оберіть суму ставки:"
    )"""

new_casino = """    b_str = f"{balance:.2f}".rstrip('0').rstrip('.')
    if not b_str: b_str = "0"
    text = (
        "🎰 <b>Вітаємо в Казино!</b>\\n\\n"
        "Правила прості: ви робите ставку і крутите слоти.\\n"
        "Виграшні комбінації (3 в ряд):\\n"
        "🍒🍒🍒 або 🍋🍋🍋 = <b>x5</b> від ставки\\n"
        "💎💎💎 = <b>Джекпот (x10)</b>\\n\\n"
        f"Ваш баланс: <b>{b_str} ₴</b>\\n"
        "Оберіть суму ставки:"
    )"""

content = content.replace(old_casino, new_casino)

# Fix process_create_gift
old_gift = """    text = (
        f"💳 <b>Створення подарункового сертифікату</b>\\n\\n"
        f"Ваш баланс: {balance} ₴\\n"
        "Введіть суму, яку хочете перетворити на промокод (вона спишеться з балансу):\\n\\n"
        "(Або напишіть /cancel для скасування)"
    )"""

new_gift = """    b_str = f"{balance:.2f}".rstrip('0').rstrip('.')
    if not b_str: b_str = "0"
    text = (
        f"💳 <b>Створення подарункового сертифікату</b>\\n\\n"
        f"Ваш баланс: {b_str} ₴\\n"
        "Введіть суму, яку хочете перетворити на промокод (вона спишеться з балансу):\\n\\n"
        "(Або напишіть /cancel для скасування)"
    )"""

content = content.replace(old_gift, new_gift)

with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "w") as f:
    f.write(content)
