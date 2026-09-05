from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from states.order import OrderState
from keyboards.inline import (
    get_recipient_keyboard,
    get_payment_method_keyboard,
    get_payment_details_keyboard,
    get_admin_action_keyboard
)
from database import db
from config import ADMIN_IDS
import random
import string

router = Router()

async def edit_or_send_photo(callback: CallbackQuery, text: str, markup=None):
    from aiogram.types import FSInputFile
    try:
        if callback.message.photo:
            await callback.message.edit_caption(caption=text, reply_markup=markup, parse_mode="HTML")
        else:
            await callback.message.delete()
            await callback.message.answer_photo(photo=FSInputFile("banner.jpg"), caption=text, reply_markup=markup, parse_mode="HTML")
    except Exception as e:
        try:
            await callback.message.delete()
        except:
            pass
        await callback.message.answer_photo(photo=FSInputFile("banner.jpg"), caption=text, reply_markup=markup, parse_mode="HTML")


def calculate_stars_price(amount: int) -> int:
    raw_price = amount * 0.78
    price = int(round(raw_price))
    remainder = price % 5
    if remainder <= 2:
        price -= remainder
    else:
        price += (5 - remainder)
    return price

def generate_order_hash() -> str:
    return "QL" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

async def start_order_recipient_flow(message_or_callback, state: FSMContext, name: str, price: float, product_id: int, category_id: int):
    await state.update_data(product_id=product_id, price=price, product_name=name, category_id=category_id)
    
    if category_id in (3, 5):
        await go_to_payment_method(message_or_callback, state, "Очікується пошта")
        return
        
    await state.set_state(OrderState.waiting_for_recipient)
    
    text = (
        f"⭐ <b>Замовлення {name}</b>\n"

        f"📊 <b>Кількість/Назва:</b> {name}\n"
        f"💳 <b>До оплати:</b> {price} ₴\n\n"

        "👤 <b>Для кого купляємо?</b>"
    )
    
    markup = get_recipient_keyboard(category_id)
    
    if isinstance(message_or_callback, CallbackQuery):
        await edit_or_send_photo(message_or_callback, text, markup)
        await message_or_callback.answer()
    else:
        await message_or_callback.answer(text, reply_markup=markup, parse_mode="HTML")

@router.callback_query(F.data.startswith("stars_buy_"))
async def process_stars_buy_preset(callback: CallbackQuery, state: FSMContext):
    amount = int(callback.data.split("_")[2])
    price = calculate_stars_price(amount)
    name = f"{amount} Stars"
    product_id = await db.get_or_create_custom_product(name, price, category_id=1)
    await start_order_recipient_flow(callback, state, name, price, product_id, 1)

@router.callback_query(F.data == "stars_custom")
async def process_stars_custom(callback: CallbackQuery, state: FSMContext):
    await state.set_state(OrderState.waiting_for_stars_amount)
    from keyboards.inline import get_back_to_main_keyboard
    text = (
        "⭐ <b>Купівля Telegram Stars</b>\n"

        "🥷 <b>Ціна:</b> ~0.75 ₴ за 1 зірку\n"
        "✨ <b>Комісія:</b> 15 ₴ за транзакцію\n\n"
        "📊 <b>Мін. замовлення:</b> 50 Stars\n"
        "🎱 <b>Макс. замовлення:</b> 100,000 Stars\n\n"

        "🖍 <b>Введіть кількість Stars:</b>"
    )
    await edit_or_send_photo(callback, text, get_back_to_main_keyboard())
    await callback.answer()

@router.message(OrderState.waiting_for_stars_amount)
async def process_stars_amount(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Будь ласка, введіть число.")
        return
    amount = int(message.text)
    if amount < 50:
        await message.answer("Мінімальна кількість зірок - 50. Введіть ще раз:")
        return
        
    price = calculate_stars_price(amount)
    name = f"{amount} Stars"
    product_id = await db.get_or_create_custom_product(name, price, category_id=1)
    await start_order_recipient_flow(message, state, name, price, product_id, 1)

STOCK_GIFTS = {
    "buy_gift_heart": {"name": "💝 Серце", "price": 12},
    "buy_gift_bear": {"name": "🧸 Ведмедик", "price": 12},
    "buy_gift_box": {"name": "🎁 Подарунок", "price": 20},
    "buy_gift_rose": {"name": "🌹 Троянда", "price": 20},
    "buy_gift_cake": {"name": "🎂 Торт", "price": 40},
    "buy_gift_bouquet": {"name": "💐 Букет", "price": 40},
    "buy_gift_champagne": {"name": "🍾 Шампанське", "price": 40},
    "buy_gift_rocket": {"name": "🚀 Ракета", "price": 40},
    "buy_gift_trophy": {"name": "🏆 Кубок", "price": 80},
    "buy_gift_ring": {"name": "💍 Каблучка", "price": 80},
    "buy_gift_diamond": {"name": "💎 Діамант", "price": 80},
}

@router.callback_query(F.data.startswith("buy_gift_"))
async def process_buy_gift_button(callback: CallbackQuery, state: FSMContext):
    gift_data = STOCK_GIFTS.get(callback.data)
    if not gift_data:
        await callback.answer("Товар не знайдено", show_alert=True)
        return
    await start_order_recipient_flow(callback, state, gift_data["name"], gift_data["price"], 0, 4)

@router.callback_query(F.data.startswith("buy_") & ~F.data.startswith("buy_gift_"))
async def process_buy_button(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[1])
    product = await db.get_product(product_id)
    if not product:
        await callback.answer("Товар не знайдено", show_alert=True)
        return
    category_id = product[1]
    name = product[2]
    price = product[4]
    await start_order_recipient_flow(callback, state, name, price, product_id, category_id)

@router.callback_query(F.data == "recipient_self", OrderState.waiting_for_recipient)
async def process_recipient_self(callback: CallbackQuery, state: FSMContext):
    username = f"@{callback.from_user.username}" if callback.from_user.username else callback.from_user.first_name
    await go_to_payment_method(callback, state, username)

@router.callback_query(F.data == "recipient_friend", OrderState.waiting_for_recipient)
async def process_recipient_friend(callback: CallbackQuery, state: FSMContext):
    await state.set_state(OrderState.waiting_for_friend_contact)
    await callback.message.edit_text(
        "📝 Введіть <b>@username</b> друга або посилання на профіль для відправки товару:",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(OrderState.waiting_for_friend_contact)
async def process_friend_contact(message: Message, state: FSMContext):
    await go_to_payment_method(message, state, message.text)

async def go_to_payment_method(message_or_callback, state: FSMContext, contact_info: str):
    data = await state.get_data()
    product_id = data['product_id']
    price = data['price']
    product_name = data['product_name']
    category_id = data.get('category_id', 1)
    
    order_hash = generate_order_hash()
    
    user = message_or_callback.from_user
    order_id = await db.create_order(
        user_id=user.id,
        username=user.username or user.first_name,
        contact_info=contact_info,
        product_id=product_id
    )
    
    await state.update_data(order_id=order_id, contact_info=contact_info, order_hash=order_hash)
    await state.set_state(OrderState.waiting_for_payment_method)
    
    text = (
        "💳 <b>Спосіб оплати</b>\n"

        f"🆔 <b>Замовлення:</b> #{order_hash}\n"
        f"🛍 <b>Товар:</b> {product_name}\n"
        f"👤 <b>Отримувач:</b> {contact_info}\n\n"
        "📈 <b>Суми до оплати:</b>\n"
        f"💳 Картка: {price} ₴\n"
        "💎 Крипта: USDT / TON / BTC / ETH\n\n"

        "👇 <b>Виберіть зручний спосіб:</b>"
    )
    user_data = await db.get_user(user.id)
    balance = user_data[3] if user_data else 0.0
    
    markup = get_payment_method_keyboard(price, category_id, balance)
    
    if isinstance(message_or_callback, CallbackQuery):
        await edit_or_send_photo(message_or_callback, text, markup)
        await message_or_callback.answer()
    else:
        await message_or_callback.answer(text, reply_markup=markup, parse_mode="HTML")

@router.callback_query(F.data == "pay_crypto", OrderState.waiting_for_payment_method)
async def process_pay_crypto(callback: CallbackQuery):
    await callback.answer("Цей спосіб оплати наразі у розробці! Оберіть переказ на картку.", show_alert=True)

@router.callback_query(F.data == "pay_balance", OrderState.waiting_for_payment_method)
async def process_pay_balance(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    order_id = data['order_id']
    price = data['price']
    
    success = await db.deduct_balance(callback.from_user.id, price)
    if not success:
        await callback.answer("❌ Недостатньо коштів на балансі!", show_alert=True)
        return
        
    await db.update_order_status(order_id, "paid")
    
    if data.get('category_id') in (3, 5):
        await state.update_data(paid_via_balance=True)
        await state.set_state(OrderState.waiting_for_email)
        text = "✅ <b>Оплата успішна!</b>\n\nБудь ласка, надайте пошту на яку потрібно підключити підписку:"
        await edit_or_send_photo(callback, text, None)
        await callback.answer()
        return
        
    await edit_or_send_photo(callback, "✅ <b>Оплата успішна!</b>\n\nКошти списано з балансу. Очікуйте на видачу товару.", get_back_to_main_keyboard())
    await state.clear()
    
    # Notify Admin
    order = await db.get_order(order_id)
    admin_text = (
        f"💰 <b>Нова оплата з балансу!</b>\n"
        f"🆔 Замовлення: #{order_id}\n"
        f"👤 Користувач: @{order[2]}\n"
        f"🛍 Товар: {order[4]}\n"
        f"💵 Сума: {price} ₴"
    )
    from keyboards.inline import get_admin_action_keyboard
    from config import ADMIN_IDS
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, admin_text, reply_markup=get_admin_action_keyboard(order_id, callback.from_user.id), parse_mode="HTML")
        except Exception:
            pass

@router.callback_query(F.data == "pay_balance_partial", OrderState.waiting_for_payment_method)
async def process_pay_balance_partial(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    order_id = data['order_id']
    price = data['price']
    category_id = data.get('category_id', 1)
    
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    balance = user[3] if user else 0.0
    
    if balance <= 0:
        await callback.answer("❌ У вас немає коштів на балансі!", show_alert=True)
        return
        
    # Reserve balance in state instead of deducting immediately
    new_price = round(price - balance, 2)
    await state.update_data(price=new_price, balance_to_deduct=balance, original_price=price)
    
    from keyboards.inline import get_payment_method_keyboard
    markup = get_payment_method_keyboard(new_price, category_id, balance=0, is_partial=True)
    
    bal_str = f"{balance:.2f}".rstrip('0').rstrip('.')
    np_str = f"{new_price:.2f}".rstrip('0').rstrip('.')
    text_partial = (
        f"✅ <b>Баланс списано!</b> ({bal_str} ₴)\n\n"
        f"Залишилось доплатити: <b>{np_str} ₴</b>\n"
        "Оберіть спосіб доплати:"
    )
    await edit_or_send_photo(callback, text_partial, markup)
    await callback.answer()

@router.callback_query(F.data == "pay_mono", OrderState.waiting_for_payment_method)
async def process_pay_mono(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_id = data['order_id']
    order_hash = data['order_hash']
    product_name = data['product_name']
    contact_info = data['contact_info']
    price = data['price']
    
    await state.set_state(OrderState.waiting_for_payment_proof)
    
    import urllib.parse
    comment = f"Оплата замовлення #{order_hash}"
    encoded_comment = urllib.parse.quote(comment)
    payment_url = f"https://send.monobank.ua/jar/6KvNFpBCX?a={int(price)}&t={encoded_comment}"
    
    text = (
        "🖤 <b>Оплата через Monobank (Apple/Google Pay)</b>\n\n"
        f"🆔 <b>Замовлення:</b> #{order_hash}\n"
        f"🛍 <b>Товар:</b> {product_name}\n"
        f"👤 <b>Отримувач:</b> {contact_info}\n"
        f"💲 <b>До оплати:</b> {price} ₴\n\n"
        "Оплатіть за посиланням нижче.\n"
        "📸 <b>Після оплати натисніть «Я оплатив» та надішліть скріншот квитанції!</b>"
    )
    
    from keyboards.inline import get_mono_payment_keyboard
    markup = get_mono_payment_keyboard(str(order_id) + "_" + order_hash, payment_url)
    await edit_or_send_photo(callback, text, markup)
    await callback.answer()

@router.callback_query(F.data == "pay_card", OrderState.waiting_for_payment_method)
async def process_pay_card(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_id = data['order_id']
    order_hash = data['order_hash']
    product_name = data['product_name']
    contact_info = data['contact_info']
    price = data['price']
    
    await state.set_state(OrderState.waiting_for_payment_proof)
    
    text = (
        "💳 <b>Переказ на карту</b>\n\n"
        f"🆔 <b>Замовлення:</b> #{order_hash}\n"
        f"🛍 <b>Товар:</b> {product_name}\n"
        f"👤 <b>Отримувач:</b> {contact_info}\n"
        f"💲 <b>До оплати:</b> {price} ₴\n\n"
        "💳 <b>Номер картки для ручного переказу:</b>\n"
        "<code>4441 1110 1411 3819</code>\n\n"
        "❗ <b>Обов'язково вкажіть у коментарі до платежу:</b>\n"
        f"<code>Оплата замовлення #{order_hash}</code>\n\n"
        "📸 <b>Після оплати натисніть «Я оплатив» та надішліть скріншот квитанції!</b>"
    )
    
    from keyboards.inline import get_card_payment_keyboard
    markup = get_card_payment_keyboard(str(order_id) + "_" + order_hash)
    await edit_or_send_photo(callback, text, markup)
    await callback.answer()

@router.callback_query(F.data.startswith("paid_"), OrderState.waiting_for_payment_proof)
async def process_paid_button(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "📸 Будь ласка, надішліть скріншот (фото) чека про оплату для підтвердження.",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(F.photo, OrderState.waiting_for_payment_proof)
async def process_payment_proof(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    order_id = data.get('order_id')
    balance_to_deduct = data.get('balance_to_deduct')
    original_price = data.get('original_price')
    
    if not order_id:
        await message.answer("Помилка: замовлення не знайдено.")
        await state.clear()
        return

    order = await db.get_order(order_id)
    if not order:
        await message.answer("Помилка: замовлення не знайдено в базі.")
        await state.clear()
        return

    user_id = message.from_user.id
    if balance_to_deduct:
        success = await db.deduct_balance(user_id, balance_to_deduct)
        if not success:
            await message.answer("❌ Помилка списання балансу! Будь ласка, зверніться до підтримки.")
            return

    category_id = data.get('category_id')
    if category_id in (3, 5):
        await state.update_data(payment_photo_id=message.photo[-1].file_id)
        await state.set_state(OrderState.waiting_for_email)
        await message.answer("Будь ласка, надайте пошту на яку потрібно підключити підписку:")
        return

    await message.answer("✅ <b>Дякуємо!</b>\nВаша оплата перевіряється адміністратором. Ви отримаєте сповіщення про зміну статусу.", parse_mode="HTML")
    await state.clear()
    
    if balance_to_deduct and original_price:
        op_str = f"{original_price:.2f}".rstrip('0').rstrip('.')
        bd_str = f"{balance_to_deduct:.2f}".rstrip('0').rstrip('.')
        o5_str = f"{order[5]:.2f}".rstrip('0').rstrip('.')
        price_info = (
            f"💰 Загальна ціна: <b>{op_str} ₴</b>\n"
            f"💳 З них сплачено з балансу: <b>{bd_str} ₴</b>\n"
            f"💵 Сплачено на карту: <b>{o5_str} ₴</b>"
        )
    else:
        o5_str = f"{order[5]:.2f}".rstrip('0').rstrip('.')
        price_info = f"💰 Сума (карта): <b>{o5_str} ₴</b>"
        
    admin_text = (
        f"🚨 <b>Нове замовлення #{order_id}</b>\n\n"
        f"👤 Клієнт: @{order[2]} (ID: {order[1]})\n"
        f"📞 Отримувач: {order[3]}\n"
        f"🛒 Товар: {order[4]}\n"
        f"{price_info}"
    )
    
    photo_id = message.photo[-1].file_id
    
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_photo(
                chat_id=admin_id,
                photo=photo_id,
                caption=admin_text,
                reply_markup=get_admin_action_keyboard(order_id, order[1]),
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Failed to send to admin {admin_id}: {e}")

@router.message(OrderState.waiting_for_email)
async def process_email_for_sub(message: Message, state: FSMContext, bot: Bot):
    email = message.text
    data = await state.get_data()
    order_id = data.get('order_id')
    
    await db.update_order_contact_info(order_id, email)
    await message.answer("✅ <b>Дякуємо!</b>\nАдмін зв'яжеться з вами після перевірки та підключення.", parse_mode="HTML")
    
    order = await db.get_order(order_id)
    paid_via_balance = data.get('paid_via_balance')
    photo_id = data.get('payment_photo_id')
    
    from keyboards.inline import get_admin_action_keyboard
    from config import ADMIN_IDS
    
    if paid_via_balance:
        admin_text = (
            f"💰 <b>Нова оплата з балансу! (Підписка)</b>\n"
            f"🆔 Замовлення: #{order_id}\n"
            f"👤 Користувач: @{order[2]}\n"
            f"📧 Пошта: {order[3]}\n"
            f"🛍 Товар: {order[4]}\n"
            f"💵 Сума: {order[5]} ₴"
        )
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_message(admin_id, admin_text, reply_markup=get_admin_action_keyboard(order_id, message.from_user.id), parse_mode="HTML")
            except Exception:
                pass
    else:
        balance_to_deduct = data.get('balance_to_deduct')
        original_price = data.get('original_price')
        
        if balance_to_deduct and original_price:
            op_str = f"{original_price:.2f}".rstrip('0').rstrip('.')
            bd_str = f"{balance_to_deduct:.2f}".rstrip('0').rstrip('.')
            o5_str = f"{order[5]:.2f}".rstrip('0').rstrip('.')
            price_info = (
                f"💰 Загальна ціна: <b>{op_str} ₴</b>\n"
                f"💳 З них сплачено з балансу: <b>{bd_str} ₴</b>\n"
                f"💵 Сплачено на карту: <b>{o5_str} ₴</b>"
            )
        else:
            o5_str = f"{order[5]:.2f}".rstrip('0').rstrip('.')
            price_info = f"💰 Сума (карта): <b>{o5_str} ₴</b>"
            
        admin_text = (
            f"🚨 <b>Нове замовлення #{order_id} (Підписка)</b>\n\n"
            f"👤 Клієнт: @{order[2]} (ID: {order[1]})\n"
            f"📧 Пошта: {order[3]}\n"
            f"🛒 Товар: {order[4]}\n"
            f"{price_info}"
        )
        for admin_id in ADMIN_IDS:
            try:
                await bot.send_photo(
                    chat_id=admin_id,
                    photo=photo_id,
                    caption=admin_text,
                    reply_markup=get_admin_action_keyboard(order_id, order[1]),
                    parse_mode="HTML"
                )
            except Exception:
                pass
                
    await state.clear()

@router.callback_query(F.data.startswith("frag_"))
async def process_fragment_selection(callback: CallbackQuery, state: FSMContext):
    item_type = callback.data.split("_")[1]
    
    text = (
        "🔗 <b>Замовлення з Fragment</b>\n"

    )
    if item_type == "anon":
        text += "Ви обрали <b>Анонімний номер (+888)</b>.\n\n"
    elif item_type == "user":
        text += "Ви обрали <b>Унікальний Username</b>.\n\n"
    elif item_type == "gift":
        text += "Ви обрали <b>Telegram Gift</b>.\n\n"
    else:
        text += "Ви обрали <b>Кастомний NFT / Подарунок</b>.\n\n"
        
    text += (
        "Будь ласка, надішліть <b>посилання</b> на бажаний товар з сайту Fragment (або просто відправте скріншот чи назву того, що ви хочете).\n\n"
        "Після цього наш адміністратор перевірить наявність, розрахує ціну і зв'яжеться з вами в особистих повідомленнях."
    )
    
    from keyboards.inline import get_back_to_main_keyboard
    await edit_or_send_photo(callback, text, get_back_to_main_keyboard())
    await state.set_state(OrderState.waiting_for_fragment_link)
    await state.update_data(fragment_type=item_type)
    await callback.answer()

@router.message(OrderState.waiting_for_fragment_link)
async def process_fragment_link(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    fragment_type = data.get("fragment_type", "custom")
    
    from config import ADMIN_IDS
    admin_text = (
        f"🔔 <b>Новий запит на Fragment NFT!</b>\n\n"
        f"👤 <b>Користувач:</b> @{message.from_user.username or message.from_user.id}\n"
        f"🏷 <b>Тип:</b> {fragment_type}\n"
        f"📝 <b>Запит:</b>\n"
        f"{message.text or 'Вкладення (фото)'}"
    )
    
    for admin_id in ADMIN_IDS:
        try:
            if message.photo:
                await bot.send_photo(admin_id, message.photo[-1].file_id, caption=admin_text, parse_mode="HTML")
            else:
                await bot.send_message(admin_id, admin_text, parse_mode="HTML")
        except Exception as e:
            print(f"Failed to send fragment request to admin: {e}")
            
    await message.answer(
        "✅ <b>Запит успішно відправлено!</b>\n\n"
        "Адміністратор незабаром перегляне ваш запит і зв'яжеться з вами для уточнення деталей. Очікуйте! ⏳",
        parse_mode="HTML"
    )
    await state.clear()
