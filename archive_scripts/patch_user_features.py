with open("/Users/macbook/tg-bot/states/order.py", "r") as f:
    content = f.read()

if "waiting_for_promo" not in content:
    content = content.replace("waiting_for_payment_proof = State()", "waiting_for_payment_proof = State()\n    waiting_for_promo = State()")

with open("/Users/macbook/tg-bot/states/order.py", "w") as f:
    f.write(content)

with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "r") as f:
    content = f.read()

# 1. Update process_cabinet buttons
old_cabinet = """    builder.row(InlineKeyboardButton(text="👥 Реферальна система", callback_data="referrals"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu", style="danger"))"""

new_cabinet = """    builder.row(InlineKeyboardButton(text="👥 Реферальна система", callback_data="referrals"))
    builder.row(
        InlineKeyboardButton(text="🎁 Щоденний бонус", callback_data="daily_bonus"),
        InlineKeyboardButton(text="🎟 Промокод", callback_data="enter_promo")
    )
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu", style="danger"))"""

content = content.replace(old_cabinet, new_cabinet)

# 2. Add daily bonus handler
bonus_handler = """
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
"""

if "def process_daily_bonus" not in content:
    content = content.replace("router = Router()\n", "router = Router()\n" + bonus_handler)

# 3. Add promo handlers
promo_handlers = """
@router.callback_query(F.data == "enter_promo")
async def process_enter_promo(callback: CallbackQuery, state: FSMContext):
    await state.set_state(OrderState.waiting_for_promo)
    text = "🎟 <b>Введіть ваш промокод:</b>\\n\\n(Або натисніть /cancel для скасування)"
    await edit_or_send_photo(callback, text)
    await callback.answer()

@router.message(OrderState.waiting_for_promo)
async def process_promo_input(message: Message, state: FSMContext):
    code = message.text.strip()
    amount = await db.activate_promocode(message.from_user.id, code)
    
    await state.clear()
    
    if amount > 0:
        await message.answer(f"✅ <b>Промокод активовано!</b>\\nВам нараховано <b>{amount} ₴</b> на баланс.", parse_mode="HTML")
    else:
        await message.answer("❌ Промокод недійсний або його ліміт вичерпано.")
"""

if "def process_enter_promo" not in content:
    content = content.replace("router = Router()\n", "router = Router()\n" + promo_handlers)

# 4. Update support FAQ
old_support = """@router.callback_query(F.data == "support")
async def process_support(callback: CallbackQuery):
    text = (
        "ℹ️ <b>Підтримка та Правила</b>\\n\\n"
        "1️⃣ Товари видаються автоматично після оплати або протягом короткого часу адміністратором.\\n"
        "2️⃣ Повернення коштів можливе лише у випадку, якщо товар виявився неробочим з нашої вини.\\n"
        "3️⃣ За шахрайство або спробу обману — вічний бан.\\n\\n"
        "Якщо у вас виникли проблеми з покупкою, зверніться до нашої підтримки: @your_admin_username"
    )
    
    await edit_or_send_photo(callback, text, get_back_to_main_keyboard())
    await callback.answer()"""

new_support = """@router.callback_query(F.data == "support")
async def process_support(callback: CallbackQuery):
    text = (
        "ℹ️ <b>Підтримка та Правила</b>\\n\\n"
        "Оберіть питання, яке вас цікавить, або напишіть адміністратору безпосередньо."
    )
    from keyboards.inline import get_faq_keyboard
    await edit_or_send_photo(callback, text, get_faq_keyboard())
    await callback.answer()

@router.callback_query(F.data.startswith("faq_"))
async def process_faq(callback: CallbackQuery):
    faq_type = callback.data.split("_")[1]
    from keyboards.inline import get_faq_keyboard
    
    if faq_type == "delivery":
        text = "⏳ <b>Як довго видається товар?</b>\\n\\nЗазвичай замовлення обробляються автоматично протягом 1-5 хвилин після підтвердження оплати. Деякі товари (наприклад, Telegram Premium) можуть видаватись до 10 хвилин."
    elif faq_type == "safety":
        text = "🛡 <b>Чи безпечно купувати Telegram Stars?</b>\\n\\nТак, це абсолютно безпечно! Ми купуємо зірки офіційними методами (через Fragment або Apple/Google Pay), тому ваш акаунт не заблокують."
    elif faq_type == "balance":
        text = "💰 <b>Як використати баланс?</b>\\n\\nБаланс можна використовувати для повної або часткової оплати будь-яких товарів. Просто оберіть товар і натисніть «Списати баланс» при виборі способу оплати."
    else:
        text = "ℹ️ Невідоме питання."
        
    await edit_or_send_photo(callback, text, get_faq_keyboard())
    await callback.answer()"""

content = content.replace(old_support, new_support)


with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "w") as f:
    f.write(content)
