from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CopyTextButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
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
        InlineKeyboardButton(text="🎰 Казино", callback_data="casino")
    )
    builder.row(
        InlineKeyboardButton(text="🎁 Реферали", callback_data="referrals"),
        InlineKeyboardButton(text="ℹ️ Підтримка", callback_data="support", style="primary")
    )
    return builder.as_markup()

def get_categories_keyboard(categories: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cat_id, cat_name in categories:
        builder.row(InlineKeyboardButton(text=cat_name, callback_data=f"cat_{cat_id}"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu", style="danger"))
    return builder.as_markup()

def get_products_keyboard(products: list, category_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for prod_id, prod_name, price in products:
        builder.row(InlineKeyboardButton(text=f"{prod_name} - {price} ₴", callback_data=f"prod_{prod_id}"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="shop", style="danger"))
    return builder.as_markup()

def get_stars_keyboard(category_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✍️ Ввести власну кількість (від 50)", callback_data="stars_custom", style="success"))
    builder.row(InlineKeyboardButton(text="⭐️ 50 Stars - 40 грн", callback_data="stars_buy_50"))
    builder.row(InlineKeyboardButton(text="⭐️ 100 Stars - 80 грн", callback_data="stars_buy_100"))
    builder.row(InlineKeyboardButton(text="⭐️ 250 Stars - 195 грн", callback_data="stars_buy_250"))
    builder.row(InlineKeyboardButton(text="⭐️ 500 Stars - 390 грн", callback_data="stars_buy_500"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="shop", style="danger"))
    return builder.as_markup()

def get_fragment_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="💝 Серце - 12 ₴", callback_data="buy_gift_heart"),
        InlineKeyboardButton(text="🧸 Ведмедик - 12 ₴", callback_data="buy_gift_bear")
    )
    builder.row(
        InlineKeyboardButton(text="🎁 Подарунок - 20 ₴", callback_data="buy_gift_box"),
        InlineKeyboardButton(text="🌹 Троянда - 20 ₴", callback_data="buy_gift_rose")
    )
    builder.row(
        InlineKeyboardButton(text="🎂 Торт - 40 ₴", callback_data="buy_gift_cake"),
        InlineKeyboardButton(text="💐 Букет - 40 ₴", callback_data="buy_gift_bouquet")
    )
    builder.row(
        InlineKeyboardButton(text="🍾 Шампанське - 40 ₴", callback_data="buy_gift_champagne")
    )
    builder.row(
        InlineKeyboardButton(text="🚀 Ракета - 40 ₴", callback_data="buy_gift_rocket"),
        InlineKeyboardButton(text="🏆 Кубок - 80 ₴", callback_data="buy_gift_trophy")
    )
    builder.row(
        InlineKeyboardButton(text="💍 Каблучка - 80 ₴", callback_data="buy_gift_ring"),
        InlineKeyboardButton(text="💎 Діамант - 80 ₴", callback_data="buy_gift_diamond")
    )
    
    builder.row(InlineKeyboardButton(text="🔗 Інший подарунок (Fragment)", url="https://fragment.com/gifts", style="success"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="shop", style="danger"))
    return builder.as_markup()

def get_product_action_keyboard(product_id: int, category_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💳 Купити", callback_data=f"buy_{product_id}"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"cat_{category_id}", style="danger"))
    return builder.as_markup()

def get_recipient_keyboard(category_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🎁 Для себе", callback_data="recipient_self"))
    builder.row(InlineKeyboardButton(text="👥 Для друга", callback_data="recipient_friend"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"cat_{category_id}", style="danger"))
    return builder.as_markup()

def get_payment_method_keyboard(price: float, category_id: int, balance: float = 0.0, is_partial: bool = False, back_cb: str = None) -> InlineKeyboardMarkup:
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
    return builder.as_markup()

def get_payment_details_keyboard(order_id: str, payment_url: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💸 Оплатити (Apple/Google Pay)", url=payment_url))
    builder.row(InlineKeyboardButton(text="💳 Скопіювати картку", copy_text=CopyTextButton(text="4441 1110 1411 3819")))
    builder.row(InlineKeyboardButton(text="✅ Я оплатив", callback_data=f"paid_{order_id}", style="success"))
    builder.row(InlineKeyboardButton(text="❌ Скасувати", callback_data="main_menu", style="danger"))
    return builder.as_markup()

def get_admin_action_keyboard(order_id: int, user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Підтвердити", callback_data=f"admin_approve_{order_id}_{user_id}"),
        InlineKeyboardButton(text="❌ Відхилити", callback_data=f"admin_reject_{order_id}_{user_id}")
    )
    return builder.as_markup()

def get_back_to_main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu", style="danger"))
    return builder.as_markup()

def get_order_approved_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🏠 Головне меню", callback_data="main_menu"))
    builder.row(InlineKeyboardButton(text="📦 Мої замовлення", callback_data="my_orders"))
    return builder.as_markup()

def get_faq_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="❓ Як довго видається товар?", callback_data="faq_delivery"))
    builder.row(InlineKeyboardButton(text="❓ Чи безпечно купувати Telegram Stars?", callback_data="faq_safety"))
    builder.row(InlineKeyboardButton(text="❓ Як використати баланс?", callback_data="faq_balance"))
    builder.row(InlineKeyboardButton(text="✍️ Написати адміну", url="https://t.me/your_admin_username"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu", style="danger"))
    return builder.as_markup()


def get_casino_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="Поставити 10 ₴", callback_data="bet_10"),
        InlineKeyboardButton(text="Поставити 50 ₴", callback_data="bet_50")
    )
    builder.row(InlineKeyboardButton(text="Поставити 100 ₴", callback_data="bet_100"))
    builder.row(InlineKeyboardButton(text="💳 Поповнити баланс", callback_data="topup_balance", style="success"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu", style="danger"))
    return builder.as_markup()

def get_user_orders_paginated_keyboard(orders: list, page: int = 1, per_page: int = 4) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    current_orders = orders[start_idx:end_idx]
    
    # 1. Order buttons
    for idx, order in enumerate(current_orders):
        order_id, name, status, created_at, price = order
        status_emoji = "⏳" if status == "pending" else "✅" if status == "approved" else "❌"
        short_name = name[:20] + "..." if len(name) > 20 else name
        btn_text = f"{status_emoji} #{order_id} | {short_name} | {price}₴"
        builder.row(InlineKeyboardButton(text=btn_text, callback_data=f"view_order_{order_id}"))
        
    # 2. Pagination buttons
    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Попередня", callback_data=f"my_orders_page_{page-1}"))
    if end_idx < len(orders):
        nav_buttons.append(InlineKeyboardButton(text="Наступна ➡️", callback_data=f"my_orders_page_{page+1}"))
    
    if nav_buttons:
        builder.row(*nav_buttons)
        
    # 3. Main menu
    builder.row(InlineKeyboardButton(text="🏠 Головне меню", callback_data="main_menu"))
    return builder.as_markup()

def get_order_details_keyboard(order_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💬 Зв'язатись з підтримкою", callback_data=f"support_order_{order_id}"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад до замовлень", callback_data="my_orders"))
    return builder.as_markup()

def get_ticket_user_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="❌ Завершити чат", callback_data="close_ticket_user"))
    return builder.as_markup()

def get_ticket_admin_keyboard(user_id: int, order_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💬 Відповісти", callback_data=f"admin_reply_{user_id}_{order_id}"))
    return builder.as_markup()

def get_ticket_admin_active_keyboard(order_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⬅️ Вийти з режиму відповіді", callback_data="exit_admin_reply"))
    builder.row(InlineKeyboardButton(text="❌ Закрити тікет", callback_data=f"close_ticket_admin_{order_id}"))
    return builder.as_markup()
