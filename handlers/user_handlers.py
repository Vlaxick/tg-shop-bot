from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardButton, Message

from database import db
from keyboards.inline import (
    get_back_to_main_keyboard,
    get_categories_keyboard,
    get_main_menu_keyboard,
    get_product_action_keyboard,
    get_products_keyboard,
)
from states.order import OrderState

router = Router()

@router.callback_query(F.data == "enter_promo")
async def process_enter_promo(callback: CallbackQuery, state: FSMContext):
    await state.set_state(OrderState.waiting_for_promo)
    text = "🎟 <b>Введіть ваш промокод:</b>\n\n(Або натисніть /cancel для скасування)"
    await edit_or_send_photo(callback, text)
    await callback.answer()

@router.message(OrderState.waiting_for_promo)
async def process_promo_input(message: Message, state: FSMContext):
    code = message.text.strip()
    amount = await db.activate_promocode(message.from_user.id, code)
    
    await state.clear()
    
    if amount > 0:
        await message.answer(f"✅ <b>Промокод активовано!</b>\nВам нараховано <b>{amount} ₴</b> на баланс.", parse_mode="HTML")
    else:
        await message.answer("❌ Промокод недійсний або його ліміт вичерпано.")

@router.callback_query(F.data == "daily_bonus")
async def process_daily_bonus(callback: CallbackQuery):
    user_id = callback.from_user.id
    status = await db.get_next_bonus_time(user_id)
    
    if status == "ready":
        amount = await db.claim_daily_bonus(user_id)
        if amount > 0:
            await callback.answer(f"🎉 Ви отримали щоденний бонус: {amount} ₴!", show_alert=True)
            # reload cabinet
            await process_cabinet(callback)
        else:
            await callback.answer("❌ Помилка нарахування.", show_alert=True)
    else:
        await callback.answer(f"⏳ Наступний бонус буде доступний через {status}.", show_alert=True)

async def edit_or_send_photo(callback: CallbackQuery, text: str, markup=None):
    from aiogram.types import FSInputFile
    try:
        if callback.message.photo:
            await callback.message.edit_caption(caption=text, reply_markup=markup, parse_mode="HTML")
        else:
            await callback.message.delete()
            await callback.message.answer_photo(photo=FSInputFile("banner.jpg"), caption=text, reply_markup=markup, parse_mode="HTML")
    except Exception:
        # Fallback if something goes wrong
        try:
            await callback.message.delete()
        except:
            pass
        await callback.message.answer_photo(photo=FSInputFile("banner.jpg"), caption=text, reply_markup=markup, parse_mode="HTML")


@router.message(Command("cancel"), StateFilter("*"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Дію скасовано. Напишіть /start для повернення в головне меню.")

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    args = message.text.split(maxsplit=1)[1] if len(message.text.split()) > 1 else None
    referrer_id = None
    if args and args.startswith("ref_"):
        try:
            referrer_id = int(args.split('_')[1])
            if referrer_id == message.from_user.id:
                referrer_id = None # Can't refer yourself
        except ValueError:
            pass
            
    await db.add_user(
        user_id=message.from_user.id,
        username=message.from_user.username or message.from_user.first_name,
        referrer_id=referrer_id
    )
    
    text = (
        f"😋 Привіт, <b>{message.from_user.first_name}</b>!\n\n"
        "Тут ви можете швидко придбати цифрові товари та підписки на свій акаунт.\n\n"
        "⭐️ За допомогою нашого сервісу вже виконано безліч успішних замовлень!"
    )
    
    photo = FSInputFile("banner.jpg")
    await message.answer_photo(photo=photo, caption=text, reply_markup=get_main_menu_keyboard(), parse_mode="HTML")
    
    from config import ADMIN_IDS
    if message.from_user.id in ADMIN_IDS:
        from keyboards.reply import get_admin_main_keyboard
        await message.answer("🛠 <b>Ви авторизовані як Адміністратор.</b>\nВикористовуйте нижнє меню для керування.", reply_markup=get_admin_main_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "main_menu")
async def process_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    
    text = (
        f"😋 Привіт, <b>{callback.from_user.first_name}</b>!\n\n"
        "Тут ви можете швидко придбати цифрові товари та підписки на свій акаунт.\n\n"
        "⭐️ За допомогою нашого сервісу вже виконано безліч успішних замовлень!"
    )
    
    await edit_or_send_photo(callback, text, get_main_menu_keyboard())
    await callback.answer()

@router.callback_query(F.data == "shop")
async def process_shop(callback: CallbackQuery):
    categories = await db.get_categories()
    text = "🛍 Оберіть категорію:"
    await edit_or_send_photo(callback, text, get_categories_keyboard(categories))
    await callback.answer()

@router.callback_query(F.data.startswith("cat_"))
async def process_category(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    
    category_id = int(callback.data.split("_")[1])
    
    if category_id == 1:
        from keyboards.inline import get_stars_keyboard
        text = "⭐️ <b>Telegram Stars</b>\n\nОберіть бажаний пакет або введіть власну кількість (мінімум 50 зірок)."
        await edit_or_send_photo(callback, text, get_stars_keyboard(category_id))
        await callback.answer()
        return
        
    elif category_id == 4:
        from keyboards.inline import get_fragment_keyboard
        from states.order import OrderState
        await state.set_state(OrderState.waiting_for_fragment_link)
        text = (
            "🎁 <b>Telegram Подарунки / NFT</b>\n"

            "Оберіть один із стандартних подарунків нижче, або надішліть посилання (скріншот) на будь-який унікальний подарунок чи юзернейм з Fragment.\n\n"
            "👇 <b>Оберіть подарунок кнопкою або кидайте лінк:</b>\n\n"
            "<i>(Після отримання запиту з вами зв'яжеться адміністратор для оформлення)</i>"
        )
        await edit_or_send_photo(callback, text, get_fragment_keyboard())
        await callback.answer()
        return

    products = await db.get_products_by_category(category_id)
    if not products:
        text = "😔 В цій категорії поки немає товарів."
        await edit_or_send_photo(callback, text, get_categories_keyboard(await db.get_categories()))
    else:
        text = "📦 Оберіть товар:"
        await edit_or_send_photo(callback, text, get_products_keyboard(products, category_id))
    await callback.answer()

@router.callback_query(F.data.startswith("prod_"))
async def process_product(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    product = await db.get_product(product_id)
    if product:
        prod_id, category_id, name, description, price = product
        
        text = (
            f"🛒 <b>Товар:</b> {name}\n\n"
            f"📝 <b>Опис:</b> {description}\n\n"
            f"💰 <b>Ціна:</b> {price} ₴"
        )
        
        await edit_or_send_photo(
            callback,
            text, 
            markup=get_product_action_keyboard(product_id, category_id)
        )
    else:
        await callback.answer("Товар не знайдено", show_alert=True)
    await callback.answer()

@router.callback_query(F.data == "my_orders")
async def process_my_orders_first_page(callback: CallbackQuery):
    await process_my_orders_page(callback, 1)

@router.callback_query(F.data.startswith("my_orders_page_"))
async def process_my_orders_page_handler(callback: CallbackQuery):
    page = int(callback.data.split("_")[3])
    await process_my_orders_page(callback, page)

async def process_my_orders_page(callback: CallbackQuery, page: int):
    orders = await db.get_user_orders(callback.from_user.id)
    if not orders:
        text = "У вас ще немає замовлень. 😔"
        markup = get_back_to_main_keyboard()
        await edit_or_send_photo(callback, text, markup)
        return

    per_page = 4
    total_pages = (len(orders) + per_page - 1) // per_page
    page = max(page, 1)
    page = min(page, total_pages)
    
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    current_orders = orders[start_idx:end_idx]
    
    text = f"📦 <b>Ваші замовлення (Сторінка {page}/{total_pages}):</b>\n\n"
    text += "Оберіть замовлення для деталей та зв'язку з підтримкою:"
    
    from keyboards.inline import get_user_orders_paginated_keyboard
    markup = get_user_orders_paginated_keyboard(orders, page, per_page)
    
    await edit_or_send_photo(callback, text, markup)
    try:
        await callback.answer()
    except Exception:
        pass

@router.callback_query(F.data.startswith("view_order_"))
async def process_view_order(callback: CallbackQuery):
    order_id = int(callback.data.split("_")[2])
    order = await db.get_order(order_id)
    if not order:
        await callback.answer("Замовлення не знайдено.", show_alert=True)
        return
        
    status_str = "⏳ В обробці" if order[6] == "pending" else "✅ Підтверджено" if order[6] == "approved" else "❌ Відхилено"
    text = (
        f"📦 <b>Замовлення #{order[0]}</b>\n\n"
        f"🛍 Товар: {order[4]}\n"
        f"💵 Ціна: {order[5]} ₴\n"
        f"📅 Дата: {order[8]}\n"
        f"📊 Статус: {status_str}\n\n"
        f"<i>Якщо у вас виникли питання щодо цього замовлення, ви можете звернутись у підтримку.</i>"
    )
    from keyboards.inline import get_order_details_keyboard
    await edit_or_send_photo(callback, text, get_order_details_keyboard(order[0]))
    await callback.answer()
@router.callback_query(F.data.startswith("leave_review_"))
async def process_leave_review(callback: CallbackQuery, state: FSMContext):
    order_id = int(callback.data.split("_")[2])
    from states.order import ReviewState
    await state.set_state(ReviewState.waiting_for_review)
    await state.update_data(review_order_id=order_id)
    
    text = (
        f"📝 <b>Залишити відгук (Замовлення #{order_id})</b>\n\n"
        f"Напишіть ваші враження від покупки одним повідомленням. Ваша думка дуже важлива для нас!"
    )
    from keyboards.inline import get_back_to_main_keyboard
    await edit_or_send_photo(callback, text, get_back_to_main_keyboard())
    await callback.answer()

from states.order import ReviewState


@router.message(ReviewState.waiting_for_review)
async def process_review_message(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    order_id = data.get('review_order_id')
    await state.clear()
    
    # Notify admins
    from config import ADMIN_IDS
    user_info = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
    admin_text = f"📝 <b>Новий відгук! (Замовлення #{order_id})</b>\nВід: {user_info}\n\n<i>{message.text}</i>"
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_text, parse_mode="HTML")
        except:
            pass
            
    # Thank user
    text = "💖 <b>Дякуємо за ваш відгук!</b>\nМи цінуємо, що ви обрали наш сервіс."
    from aiogram.types import FSInputFile

    from keyboards.inline import get_main_menu_keyboard
    photo = FSInputFile("banner.jpg")
    await message.answer_photo(photo=photo, caption=text, reply_markup=get_main_menu_keyboard(), parse_mode="HTML")
@router.callback_query(F.data.startswith("support_order_"))
async def process_support_order(callback: CallbackQuery, state: FSMContext, bot: Bot):
    order_id = int(callback.data.split("_")[2])
    from states.support import SupportState
    
    ticket_id = await db.get_or_create_ticket(callback.from_user.id, order_id)
    
    await state.set_state(SupportState.user_in_ticket)
    await state.update_data(support_order_id=order_id, ticket_id=ticket_id)
    
    from keyboards.inline import get_ticket_user_keyboard
    text = (
        f"💬 <b>Чат з підтримкою (Тікет #{ticket_id}, Замовлення #{order_id})</b>\n\n"
        f"Ви підключені до живого чату з адміністратором. Всі ваші повідомлення будуть пересилатися йому.\n"
        f"Опишіть проблему максимально детально. Ви можете надсилати текст або фото."
    )
    await edit_or_send_photo(callback, text, get_ticket_user_keyboard())
    await callback.answer()

from states.support import SupportState


@router.callback_query(F.data == "close_ticket_user", SupportState.user_in_ticket)
async def close_ticket_user(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    order_id = data.get('support_order_id')
    ticket_id = data.get('ticket_id')
    
    if ticket_id:
        await db.close_ticket(ticket_id)
        
    await state.clear()
    
    from config import ADMIN_IDS
    admin_text = f"⚠️ Користувач @{callback.from_user.username} закрив тікет #{ticket_id}."
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_text)
        except:
            pass
            
    text = "✅ Чат завершено."
    await edit_or_send_photo(callback, text, get_back_to_main_keyboard())
    await callback.answer()

from states.support import SupportState


@router.message(SupportState.user_in_ticket)
async def process_user_ticket_message(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    order_id = data.get('support_order_id')
    ticket_id = data.get('ticket_id')
    
    from config import ADMIN_IDS
    from keyboards.inline import get_ticket_admin_keyboard
    
    user_info = f"@{message.from_user.username}" if message.from_user.username else f"ID: {message.from_user.id}"
    admin_text = f"📩 <b>Тікет #{ticket_id} (Замовлення #{order_id})</b> | Від: {user_info}\n\nНове повідомлення від клієнта:\n"
    
    for admin_id in ADMIN_IDS:
        try:
            markup = get_ticket_admin_keyboard(message.from_user.id, order_id)
            if message.text:
                await bot.send_message(admin_id, admin_text + f"<i>{message.text}</i>", parse_mode="HTML", reply_markup=markup)
            elif message.photo:
                caption = admin_text + (f"<i>{message.caption}</i>" if message.caption else "")
                await bot.send_photo(admin_id, photo=message.photo[-1].file_id, caption=caption, parse_mode="HTML", reply_markup=markup)
        except Exception:
            pass
            
    # We don't clear state! Ticket stays open!
    # No need to confirm every message, user can just keep typing

@router.callback_query(F.data == "language")
async def process_language(callback: CallbackQuery):
    await callback.answer("У майбутньому тут можна буде змінити мову!", show_alert=True)

@router.callback_query(F.data == "support")
async def process_support(callback: CallbackQuery):
    from keyboards.inline import get_support_menu_keyboard
    text = "ℹ️ <b>Центр підтримки</b>\n\nОберіть потрібний розділ:"
    await edit_or_send_photo(callback, text, get_support_menu_keyboard())
    await callback.answer()

@router.callback_query(F.data == "faq_menu")
async def process_faq_menu(callback: CallbackQuery):
    from keyboards.inline import get_faq_keyboard
    text = "💡 <b>Часті запитання (FAQ)</b>\n\nОберіть тему, яка вас цікавить:"
    await edit_or_send_photo(callback, text, get_faq_keyboard())
    await callback.answer()

@router.callback_query(F.data.startswith("faq_"))
async def process_faq_item(callback: CallbackQuery):
    from keyboards.inline import get_faq_keyboard
    topic = callback.data.split("_")[1]
    
    if topic == "delivery":
        text = "🚚 <b>Доставка:</b>\n\nВсі цифрові товари (ключі, акаунти) видаються протягом 24 годин після оплати (зазвичай миттєво після перевірки). Фізична доставка відсутня."
    elif topic == "payment":
        text = "💳 <b>Оплата:</b>\n\nМи приймаємо оплату через Monobank (переказ або Apple/Google Pay), а також криптовалютою через CryptoBot (USDT, TON тощо)."
    elif topic == "refund":
        text = "🔄 <b>Повернення:</b>\n\nПовернення коштів можливе лише у випадку, якщо товар не був доставлений, або виявився неробочим і ми не змогли надати заміну."
    else:
        text = "💡 Інформація оновлюється."
        
    await edit_or_send_photo(callback, text, get_faq_keyboard())
    await callback.answer()

@router.callback_query(F.data == "contact_operator")
async def process_contact_operator(callback: CallbackQuery):
    text = (
        "👨‍💻 <b>Зв'язок з оператором</b>\n\n"
        "Якщо у вас виникли проблеми з конкретним замовленням, будь ласка, зайдіть у «📦 Мої замовлення», оберіть замовлення і натисніть «💬 Зв'язатись з підтримкою».\n\n"
        "Якщо у вас загальне запитання — напишіть адміністратору: @ваші_контакти"
    )
    from keyboards.inline import get_back_to_main_keyboard
    await edit_or_send_photo(callback, text, get_back_to_main_keyboard())
    await callback.answer()

# --- SMART SEARCH ---
@router.callback_query(F.data == "search_product")
async def process_search_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(OrderState.waiting_for_search_query)
    from keyboards.inline import get_back_to_main_keyboard
    await edit_or_send_photo(callback, "🔍 <b>Розумний Пошук</b>\n\nНадішліть мені слово для пошуку товару (наприклад, iPhone або Premium):", get_back_to_main_keyboard())
    await callback.answer()

@router.message(OrderState.waiting_for_search_query)
async def process_search_query(message: Message, state: FSMContext):
    query = message.text.strip()
    if len(query) < 2:
        await message.answer("❌ Запит занадто короткий. Введіть хоча б 2 символи.")
        return
        
    from database import db
    results = await db.search_products(query)
    
    if not results:
        from keyboards.inline import get_back_to_main_keyboard
        await message.answer("🔍 За вашим запитом нічого не знайдено. Спробуйте інше слово.", reply_markup=get_back_to_main_keyboard())
        return
        
    # We will build an inline keyboard with the results
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    builder = InlineKeyboardBuilder()
    
    for prod in results:
        # prod: (id, name, price)
        short_name = prod[1][:25] + "..." if len(prod[1]) > 25 else prod[1]
        btn_text = f"📦 {short_name} - {prod[2]}₴"
        builder.row(InlineKeyboardButton(text=btn_text, callback_data=f"product_{prod[0]}"))
        
    builder.row(InlineKeyboardButton(text="🏠 Головне меню", callback_data="main_menu"))
    
    await state.clear()
    await message.answer(f"🔍 <b>Результати пошуку для:</b> {query}\nОберіть товар зі списку:", reply_markup=builder.as_markup(), parse_mode="HTML")

@router.message(F.web_app_data)
async def process_web_app_data(message: Message, state: FSMContext):
    import json
    try:
        data = json.loads(message.web_app_data.data)
        if data.get('action') == 'buy_fragment':
            item = data.get('item')
            price = item.get('price')
            name = item.get('name')
            
            from states.order import OrderState
            await state.set_state(OrderState.waiting_for_recipient)
            await state.update_data(
                product_id=item.get('id'),
                product_name=name,
                price=price
            )
            
            from keyboards.inline import get_recipient_keyboard
            await message.answer(
                f"🎁 Ви обрали <b>{name}</b> за {price} ₴.\n\nДля кого купляємо?",
                reply_markup=get_recipient_keyboard(),
                parse_mode="HTML"
            )
    except Exception as e:
        print(f"Web App Data Error: {e}")
        await message.answer("Сталася помилка при обробці даних з каталогу.")

@router.message(OrderState.waiting_for_fragment_link)
async def process_fragment_link(message: Message, state: FSMContext):
    from config import ADMIN_ID
    from keyboards.inline import get_back_to_main_keyboard
    await state.clear()
    
    # Send to admin
    await message.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"🆕 <b>Новий запит на Fragment/NFT</b>\nВід: @{message.from_user.username or message.from_user.id}\n\nНижче буде переслане повідомлення користувача (скріншот або посилання):",
        parse_mode="HTML"
    )
    await message.forward(chat_id=ADMIN_ID)
    
    await message.answer(
        "✅ Ваша заявка прийнята!\n\nОчікуйте, найближчим часом з вами зв'яжеться адміністратор для уточнення деталей та оплати.",
        reply_markup=get_back_to_main_keyboard()
    )

from aiogram.utils.keyboard import InlineKeyboardBuilder


@router.callback_query(F.data == "cabinet")
async def process_cabinet(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    balance = user[3] if user else 0.0
    referral_earnings = user[4] if user and len(user) > 4 else 0.0
    
    total_purchases, total_spent = await db.get_user_stats(user_id)
    
    b_str = f"{balance:.2f}".rstrip('0').rstrip('.')
    re_str = f"{referral_earnings:.2f}".rstrip('0').rstrip('.')
    ts_str = f"{total_spent:.2f}".rstrip('0').rstrip('.')
    if b_str == "": b_str = "0"
    if re_str == "": re_str = "0"
    if ts_str == "": ts_str = "0"
    
    text = (
        "🎩 <b>Ваш профіль</b>\n\n"
        f"👤 <b>Ваш ID:</b> <code>{user_id}</code>\n"
        f"👥 <b>Реферальний баланс:</b> {re_str} ₴\n\n"
        f"🛍 <b>Всього покупок:</b> {total_purchases}\n"
        f"💸 <b>Загальний депозит:</b> {ts_str} ₴\n\n"
        f"💰 <b>Баланс:</b> {b_str} ₴"
    )
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="👥 Реферальна система", callback_data="referrals"))
    builder.row(
        InlineKeyboardButton(text="🎁 Щоденний бонус", callback_data="daily_bonus"),
        InlineKeyboardButton(text="🎟 Ввести промокод", callback_data="enter_promo")
    )
    builder.row(
        InlineKeyboardButton(text="💳 Подарувати баланс", callback_data="create_gift"),
        InlineKeyboardButton(text="💵 Поповнити", callback_data="topup_balance")
    )
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu", style="danger"))
    
    await edit_or_send_photo(callback, text, builder.as_markup())
    await callback.answer()

@router.callback_query(F.data == "referrals")
async def process_referrals(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    balance = user[3] if user else 0.0
    bot_info = await callback.bot.get_me()
    bot_username = bot_info.username
    ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    
    text = (
        "🎁 <b>Реферальна програма та Баланс</b>\n"

        f"💰 <b>Ваш баланс:</b> {balance} ₴\n\n"
        "🤝 <b>Запрошуйте друзів та заробляйте:</b>\n"
        "• <b>50%</b> від суми першої покупки вашого друга!\n"
        "• <b>5%</b> від усіх наступних покупок друга!\n\n"
        f"🔗 <b>Ваше реферальне посилання:</b>\n<code>{ref_link}</code>\n\n"
        "<i>Просто надішліть це посилання друзям. Коли вони здійснять покупку, гроші автоматично зарахуються на ваш баланс!</i>"
    )
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu", style="danger"))
    
    await edit_or_send_photo(callback, text, builder.as_markup())
    await callback.answer()


@router.callback_query(F.data == "casino")
async def process_casino_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    balance = user[3] if user else 0.0
    
    b_str = f"{balance:.2f}".rstrip('0').rstrip('.')
    if not b_str: b_str = "0"
    text = (
        "🎰 <b>Вітаємо в Казино!</b>\n\n"
        "Правила прості: ви робите ставку і крутите слоти.\n"
        "Виграшні комбінації:\n"
        "💎💎💎 = <b>x5</b> (Джекпот)\n"
        "🍒🍒🍒 = <b>x2</b> (Великий куш)\n"
        "🍎🍎🍎, 🍇🍇🍇, 🔔🔔🔔 = <b>x1.5</b> (Міні-виграш)\n\n"
        f"Ваш баланс: <b>{b_str} ₴</b>\n"
        "Оберіть суму ставки:"
    )
    from keyboards.inline import get_casino_keyboard
    await edit_or_send_photo(callback, text, get_casino_keyboard())
    await callback.answer()

import asyncio


@router.callback_query(F.data.startswith("bet_"))
async def process_casino_bet(callback: CallbackQuery, bot: Bot):
    bet = float(callback.data.split("_")[1])
    user_id = callback.from_user.id
    
    # deduct balance first
    success = await db.deduct_balance(user_id, bet)
    if not success:
        await callback.answer("❌ Недостатньо коштів на балансі!", show_alert=True)
        return
        
    slots = ["🍎", "🍋", "🍒", "💎", "🔔", "🍇"]
    import random
    
    # Animation
    for i in range(3):
        f1, f2, f3 = random.choice(slots), random.choice(slots), random.choice(slots)
        try:
            await callback.message.edit_caption(
                caption=f"🎰 <b>Ставка: {bet} ₴</b>\n\n     [ {f1} | {f2} | {f3} ]\n\n🔄 <i>Крутимо слоти... ({3-i})</i>", 
                parse_mode="HTML"
            )
        except:
            pass
        await asyncio.sleep(0.5)
        
    # Final outcome
    rand = random.random()
    if rand < 0.02: # 2% chance
        final_slots = ["💎", "💎", "💎"]
        multiplier = 5
        text_res = f"🎉 <b>ДЖЕКПОТ!</b> Ви виграли <b>{bet*multiplier} ₴</b> (x5)!"
    elif rand < 0.10: # 8% chance
        final_slots = ["🍒", "🍒", "🍒"]
        multiplier = 2
        text_res = f"🎊 <b>ВИГРАШ!</b> Ви виграли <b>{bet*multiplier} ₴</b> (x2)!"
    elif rand < 0.35: # 25% chance
        f = random.choice(["🍎", "🍇", "🔔"])
        final_slots = [f, f, f]
        multiplier = 1.5
        text_res = f"👍 <b>Непогано!</b> Ви виграли <b>{bet*multiplier} ₴</b> (x1.5)!"
    else: # 65% chance
        final_slots = [random.choice(slots), random.choice(slots), random.choice(slots)]
        while final_slots[0] == final_slots[1] == final_slots[2]:
            final_slots[2] = random.choice(slots)
        multiplier = 0
        text_res = f"😔 На жаль, ви програли <b>{bet} ₴</b>. Спробуйте ще раз!"
        
    win_amount = bet * multiplier
    if win_amount > 0:
        await db.add_balance(user_id, win_amount)
        
    user = await db.get_user(user_id)
    balance = user[3] if user else 0.0
    
    final_caption = (
        f"🎰 <b>Результат гри</b>\n\n"
        f"     [ {final_slots[0]} | {final_slots[1]} | {final_slots[2]} ]\n\n"
        f"{text_res}\n\n"
        f"💳 Ваш баланс: <b>{balance:.2f} ₴</b>"
    )
    
    from keyboards.inline import get_casino_keyboard
    try:
        await callback.message.edit_caption(caption=final_caption, reply_markup=get_casino_keyboard(), parse_mode="HTML")
    except:
        pass
    await callback.answer()


@router.callback_query(F.data == "create_gift")
async def process_create_gift(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    balance = user[3] if user else 0.0
    
    if balance <= 0:
        await callback.answer("❌ У вас порожній баланс!", show_alert=True)
        return
        
    await state.set_state(OrderState.waiting_for_gift_amount)
    b_str = f"{balance:.2f}".rstrip('0').rstrip('.')
    if not b_str: b_str = "0"
    text = (
        f"💳 <b>Створення подарункового сертифікату</b>\n\n"
        f"Ваш баланс: {b_str} ₴\n"
        "Введіть суму, яку хочете перетворити на промокод (вона спишеться з балансу):\n\n"
        "(Або напишіть /cancel для скасування)"
    )
    await edit_or_send_photo(callback, text)
    await callback.answer()

import random
import string


def generate_gift_code():
    return "GIFT-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

@router.message(OrderState.waiting_for_gift_amount)
async def process_gift_amount(message: Message, state: FSMContext):
    user_id = message.from_user.id
    try:
        amount = float(message.text.strip())
        if amount <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Будь ласка, введіть коректну суму (число більше 0).")
        return
        
    success = await db.deduct_balance(user_id, amount)
    if not success:
        await message.answer("❌ На балансі недостатньо коштів для такої суми!")
        await state.clear()
        return
        
    code = generate_gift_code()
    await db.create_promocode(code, amount, 1)
    
    await state.clear()
    await message.answer(
        f"🎉 <b>Сертифікат успішно створено!</b>\n\n"
        f"Ваш код: <code>{code}</code>\n"
        f"Номінал: <b>{amount} ₴</b>\n\n"
        "Надішліть цей код другу, і він зможе активувати його в розділі 'Ввести промокод'!",
        parse_mode="HTML"
    )


@router.callback_query(F.data == "topup_balance")
async def process_topup_balance(callback: CallbackQuery, state: FSMContext):
    await state.set_state(OrderState.waiting_for_topup_amount)
    
    from aiogram.types import InlineKeyboardButton
    from aiogram.utils.keyboard import InlineKeyboardBuilder
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="50 ₴", callback_data="topup_amt_50"),
        InlineKeyboardButton(text="100 ₴", callback_data="topup_amt_100")
    )
    builder.row(
        InlineKeyboardButton(text="200 ₴", callback_data="topup_amt_200"),
        InlineKeyboardButton(text="500 ₴", callback_data="topup_amt_500")
    )
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="cabinet", style="danger"))
    
    text = (
        "💳 <b>Поповнення балансу</b>\n\n"
        "Оберіть суму для поповнення або введіть її вручну повідомленням:\n\n"
        "<i>(Мінімальна сума: 10 ₴)</i>"
    )
    await edit_or_send_photo(callback, text, builder.as_markup())
    await state.update_data(prompt_msg_id=callback.message.message_id)
    await callback.answer()

@router.callback_query(F.data.startswith("topup_amt_"), OrderState.waiting_for_topup_amount)
async def process_topup_preset(callback: CallbackQuery, state: FSMContext, bot: Bot):
    amount = float(callback.data.split("_")[2])
    await _start_topup_payment(callback.message, callback.from_user, amount, state, callback)

@router.message(OrderState.waiting_for_topup_amount)
async def process_topup_manual(message: Message, state: FSMContext):
    try:
        amount = float(message.text.strip())
        if amount < 10:
            await message.answer("❌ Мінімальна сума поповнення — 10 ₴.")
            return
        await _start_topup_payment(message, message.from_user, amount, state)
    except ValueError:
        await message.answer("❌ Будь ласка, введіть коректну суму числом (наприклад: 100).")

async def _start_topup_payment(message: Message, user, amount: float, state: FSMContext, callback: CallbackQuery = None):
    # Create custom product for topup
    product_id = await db.get_or_create_custom_product("Поповнення балансу", amount)
    
    import hashlib
    order_id = await db.create_order(user.id, user.username or str(user.id), "Поповнення", product_id)
    order_hash = hashlib.md5(f"{order_id}_{user.id}".encode()).hexdigest()[:8]
    
    # We pretend this is a normal order
    await state.update_data(
        product_id=product_id, 
        price=amount, 
        original_price=amount, 
        balance_to_deduct=0,
        order_id=order_id,
        order_hash=order_hash,
        product_name="Поповнення балансу",
        contact_info="Поповнення"
    )
    
    from keyboards.inline import get_payment_method_keyboard
    
    amount_str = f"{amount:.2f}".rstrip('0').rstrip('.')
    text = (
        f"💳 <b>Оберіть спосіб оплати для поповнення балансу на {amount_str} ₴:</b>"
    )
    markup = get_payment_method_keyboard(amount, category_id=0, balance=0, is_partial=False, back_cb="cabinet")
    
    if callback:
        await edit_or_send_photo(callback, text, markup)
        await state.set_state(OrderState.waiting_for_payment_method)
        await callback.answer()
    else:
        from aiogram.types import FSInputFile
        # manual entry: delete user msg and previous prompt
        data = await state.get_data()
        prompt_id = data.get("prompt_msg_id")
        try:
            await message.delete()
            if prompt_id:
                await message.bot.delete_message(chat_id=message.chat.id, message_id=prompt_id)
        except:
            pass
            
        await state.set_state(OrderState.waiting_for_payment_method)
        await message.answer_photo(photo=FSInputFile("banner.jpg"), caption=text, reply_markup=markup, parse_mode="HTML")
