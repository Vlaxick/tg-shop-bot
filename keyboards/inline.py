from aiogram.types import CopyTextButton, InlineKeyboardButton, InlineKeyboardMarkup
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

def get_support_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💡 Часті запитання (FAQ)", callback_data="faq_menu"))
    builder.row(InlineKeyboardButton(text="👨‍💻 Зв'язатись з оператором", callback_data="contact_operator"))
    builder.row(InlineKeyboardButton(text="🏠 Головне меню", callback_data="main_menu"))
    return builder.as_markup()

def get_faq_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🚚 Доставка", callback_data="faq_delivery"))
    builder.row(InlineKeyboardButton(text="💳 Оплата", callback_data="faq_payment"))
    builder.row(InlineKeyboardButton(text="🔄 Повернення", callback_data="faq_refund"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад до підтримки", callback_data="support"))
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

def get_fragment_keyboard(page: int = 1) -> InlineKeyboardMarkup:
    standard_gifts = [
        ("💝 Серце - 12 ₴", "buy_gift_heart"),
        ("🧸 Ведмедик - 12 ₴", "buy_gift_bear"),
        ("🎁 Подарунок - 20 ₴", "buy_gift_box"),
        ("🌹 Троянда - 20 ₴", "buy_gift_rose"),
        ("🎂 Торт - 40 ₴", "buy_gift_cake"),
        ("💐 Букет - 40 ₴", "buy_gift_bouquet"),
        ("🍾 Шампанське - 40 ₴", "buy_gift_champagne"),
        ("🚀 Ракета - 40 ₴", "buy_gift_rocket"),
        ("🏆 Кубок - 80 ₴", "buy_gift_trophy"),
        ("💍 Каблучка - 80 ₴", "buy_gift_ring"),
        ("💎 Діамант - 80 ₴", "buy_gift_diamond")
    ]
    builder = InlineKeyboardBuilder()
    
    items_per_page = 4
    total_pages = (len(standard_gifts) + items_per_page - 1) // items_per_page
    
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    current_items = standard_gifts[start_idx:end_idx]
    
    row = []
    for text, callback_data in current_items:
        row.append(InlineKeyboardButton(text=text, callback_data=callback_data))
        if len(row) == 2:
            builder.row(*row)
            row = []
    if row:
        builder.row(*row)
        
    nav_row = []
    if page > 1:
        nav_row.append(InlineKeyboardButton(text="⬅️", callback_data=f"fragpage_{page-1}"))
    else:
        nav_row.append(InlineKeyboardButton(text="➖", callback_data="ignore"))
        
    nav_row.append(InlineKeyboardButton(text=f"{page}/{total_pages}", callback_data="ignore"))
    
    if page < total_pages:
        nav_row.append(InlineKeyboardButton(text="➡️", callback_data=f"fragpage_{page+1}"))
    else:
        nav_row.append(InlineKeyboardButton(text="➖", callback_data="ignore"))
        
    builder.row(*nav_row)
    
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
    
    builder.row(InlineKeyboardButton(text=f"🖤 Monobank (Apple / Google Pay) — {price_str} ₴", callback_data="pay_mono"))
    builder.row(InlineKeyboardButton(text=f"💳 Переказ на карту — {price_str} ₴", callback_data="pay_card"))
    builder.row(InlineKeyboardButton(text="💎 Крипта (CryptoBot)", callback_data="pay_crypto"))
    
    if not back_cb:
        back_cb = "cabinet" if category_id == 0 else f"cat_{category_id}"
    
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data=back_cb, style="danger"))
    return builder.as_markup()

def get_mono_payment_keyboard(order_id: str, payment_url: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💸 Оплатити (Apple/Google Pay)", url=payment_url))
    builder.row(InlineKeyboardButton(text="✅ Я оплатив", callback_data=f"paid_{order_id}", style="success"))
    builder.row(InlineKeyboardButton(text="❌ Скасувати", callback_data="main_menu", style="danger"))
    return builder.as_markup()

def get_card_payment_keyboard(order_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💳 Скопіювати номер картки", copy_text=CopyTextButton(text="4441 1110 1411 3819")))
    builder.row(InlineKeyboardButton(text="✅ Я оплатив", callback_data=f"paid_{order_id}", style="success"))
    builder.row(InlineKeyboardButton(text="❌ Скасувати", callback_data="main_menu", style="danger"))
    return builder.as_markup()

def get_open_tickets_keyboard(tickets: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if not tickets:
        return None
    for ticket in tickets:
        t_id, order_id, user_id, product_name = ticket
        short_name = product_name[:20] + "..." if len(product_name) > 20 else product_name
        builder.row(InlineKeyboardButton(text=f"🎫 #{t_id} | З. #{order_id} | {short_name}", callback_data=f"admin_reply_{user_id}_{order_id}"))
    return builder.as_markup()

def get_open_orders_admin_keyboard(orders: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if not orders:
        return None
    for order in orders:
        o_id, username, product_name, price, created_at = order
        short_name = product_name[:20] + "..." if len(product_name) > 20 else product_name
        builder.row(InlineKeyboardButton(text=f"🛍 #{o_id} | @{username} | {short_name}", callback_data=f"admin_view_order_{o_id}"))
    return builder.as_markup()

def get_admin_action_keyboard(order_id: int, user_id: int, status: str = "pending") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if status == "pending":
        builder.row(
            InlineKeyboardButton(text="⏳ Взяти в роботу", callback_data=f"admin_take_{order_id}_{user_id}"),
            InlineKeyboardButton(text="❌ Відхилити", callback_data=f"admin_reject_{order_id}_{user_id}")
        )
    elif status == "in_progress":
        builder.row(
            InlineKeyboardButton(text="✅ Підтвердити успішно", callback_data=f"admin_approve_{order_id}_{user_id}"),
            InlineKeyboardButton(text="❌ Відхилити", callback_data=f"admin_reject_{order_id}_{user_id}")
        )
    return builder.as_markup()

def get_back_to_main_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu", style="danger"))
    return builder.as_markup()

def get_order_in_progress_keyboard(order_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💬 Написати повідомлення", callback_data=f"support_order_{order_id}"))
    builder.row(InlineKeyboardButton(text="🏠 Головне меню", callback_data="main_menu"))
    return builder.as_markup()

def get_order_approved_keyboard(order_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📝 Залишити відгук", callback_data=f"leave_review_{order_id}"))
    builder.row(InlineKeyboardButton(text="🏠 Головне меню", callback_data="main_menu"))
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

def get_admin_product_manager_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="➕ Додати категорію", callback_data="admin_add_category"))
    builder.row(InlineKeyboardButton(text="➕ Додати товар", callback_data="admin_add_product"))
    builder.row(InlineKeyboardButton(text="🗑 Видалити товар", callback_data="admin_delete_product"))
    return builder.as_markup()

def get_admin_categories_selection_keyboard(categories: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.row(InlineKeyboardButton(text=cat[1], callback_data=f"admin_sel_cat_{cat[0]}"))
    builder.row(InlineKeyboardButton(text="❌ Скасувати", callback_data="admin_cancel_product"))
    return builder.as_markup()

def get_admin_products_deletion_keyboard(products: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for prod in products:
        short_name = prod[1][:30] + "..." if len(prod[1]) > 30 else prod[1]
        builder.row(InlineKeyboardButton(text=f"🗑 {short_name}", callback_data=f"admin_del_prod_{prod[0]}"))
    builder.row(InlineKeyboardButton(text="❌ Скасувати", callback_data="admin_cancel_product"))
    return builder.as_markup()
