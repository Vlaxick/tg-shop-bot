from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, FSInputFile
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from states.order import OrderState
from keyboards.inline import (
    get_main_menu_keyboard,
    get_categories_keyboard,
    get_products_keyboard,
    get_product_action_keyboard,
    get_back_to_main_keyboard
)
from database import db

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
    except Exception as e:
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
        "😋 Привіт, <b>{username}</b>!\n\n"
        "Тут ви можете швидко придбати цифрові товари та підписки на свій акаунт.\n\n"
        "⭐️ За допомогою нашого сервісу вже виконано безліч успішних замовлень!"
    ).format(username=message.from_user.first_name)
    
    photo = FSInputFile("banner.jpg")
    await message.answer_photo(photo=photo, caption=text, reply_markup=get_main_menu_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "main_menu")
async def process_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    
    text = (
        "😋 Привіт, <b>{username}</b>!\n\n"
        "Тут ви можете швидко придбати цифрові товари та підписки на свій акаунт.\n\n"
        "⭐️ За допомогою нашого сервісу вже виконано безліч успішних замовлень!"
    ).format(username=callback.from_user.first_name)
    
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
            "━━━━━━━━━━━━━━━━━━\n\n"
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
        prod_id, name, description, price = product
        
        # Get category_id to provide a working Back button
        # Actually we didn't fetch category_id in get_product, let's fix db.py or handle it
        # For simplicity we'll just parse the category ID from the db if we need to, 
        # or we can modify db.get_product to return category_id. 
        # Let's assume we can fetch it, or we just rely on get_product returning category_id.
        # Actually I didn't include category_id in get_product SELECT. I will update db.py in a bit.
        
        text = (
            f"🛒 <b>Товар:</b> {name}\n\n"
            f"📝 <b>Опис:</b> {description}\n\n"
            f"💰 <b>Ціна:</b> {price} ₴"
        )
        
        # Let's do a trick: we don't have category_id here easily without another query, 
        # but for the "Back" button we can just go to the shop if we don't have it, 
        # or we fetch it. I'll fetch it from the DB.
        
        import aiosqlite
        async with aiosqlite.connect(db.DB_PATH) as _db:
            async with _db.execute('SELECT category_id FROM products WHERE id = ?', (product_id,)) as cursor:
                res = await cursor.fetchone()
                category_id = res[0] if res else 0

        await edit_or_send_photo(
            callback,
            text, 
            markup=get_product_action_keyboard(product_id, category_id)
        )
    else:
        await callback.answer("Товар не знайдено", show_alert=True)
    await callback.answer()

@router.callback_query(F.data == "my_orders")
async def process_my_orders(callback: CallbackQuery):
    orders = await db.get_user_orders(callback.from_user.id)
    if not orders:
        text = "У вас ще немає замовлень. 😔"
    else:
        text = "📦 <b>Ваші замовлення:</b>\n\n"
        for name, status, created_at in orders[:10]: # show last 10
            status_emoji = "⏳" if status == "pending" else "✅" if status == "approved" else "❌"
            text += f"▪️ {name}\n📅 {created_at}\nСтатус: {status_emoji} {status}\n\n"
    
    await edit_or_send_photo(callback, text, get_back_to_main_keyboard())
    await callback.answer()

@router.callback_query(F.data == "language")
async def process_language(callback: CallbackQuery):
    await callback.answer("У майбутньому тут можна буде змінити мову!", show_alert=True)

@router.callback_query(F.data == "support")
async def process_support(callback: CallbackQuery):
    text = (
        "ℹ️ <b>Підтримка та Правила</b>\n\n"
        "1. Всі цифрові товари видаються протягом 24 годин після оплати.\n"
        "2. Повернення коштів можливе лише у випадку, якщо товар не був доставлений.\n\n"
        "Якщо у вас є питання, звертайтесь до адміністратора."
    )
    await edit_or_send_photo(callback, text, get_back_to_main_keyboard())
    await callback.answer()

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
        "━━━━━━━━━━━━━━━━━━\n\n"
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
        "Виграшні комбінації (3 в ряд):\n"
        "🍒🍒🍒 або 🍋🍋🍋 = <b>x5</b> від ставки\n"
        "💎💎💎 = <b>Джекпот (x10)</b>\n\n"
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
        
    await callback.message.delete()
    msg = await callback.message.answer_dice(emoji="🎰")
    
    # Value 1, 22, 43 is x5. Value 64 is x10.
    # We must wait a few seconds for the animation
    await asyncio.sleep(2.0)
    
    win_amount = 0
    if msg.dice.value == 64: # 777
        win_amount = bet * 10
        await bot.send_message(user_id, f"🎉 <b>ДЖЕКПОТ!</b> Ви виграли <b>{win_amount} ₴</b>!", parse_mode="HTML")
    elif msg.dice.value in (1, 22, 43):
        win_amount = bet * 5
        await bot.send_message(user_id, f"🎊 <b>ВИГРАШ!</b> Ви виграли <b>{win_amount} ₴</b>!", parse_mode="HTML")
    else:
        await bot.send_message(user_id, f"😔 На жаль, ви програли. Спробуйте ще раз!")
        
    if win_amount > 0:
        await db.add_balance(user_id, win_amount)
        
    # Send menu back
    await process_casino_menu(callback)


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

import string
import random

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
    
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
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
