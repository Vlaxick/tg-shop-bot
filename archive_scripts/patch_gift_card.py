with open("/Users/macbook/tg-bot/states/order.py", "r") as f:
    content = f.read()

if "waiting_for_gift_amount" not in content:
    content = content.replace("waiting_for_promo = State()", "waiting_for_promo = State()\n    waiting_for_gift_amount = State()")

with open("/Users/macbook/tg-bot/states/order.py", "w") as f:
    f.write(content)

with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "r") as f:
    content = f.read()

old_cabinet_kb = """    builder.row(
        InlineKeyboardButton(text="🎁 Щоденний бонус", callback_data="daily_bonus"),
        InlineKeyboardButton(text="🎟 Промокод", callback_data="enter_promo")
    )
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu", style="danger"))"""

new_cabinet_kb = """    builder.row(
        InlineKeyboardButton(text="🎁 Щоденний бонус", callback_data="daily_bonus"),
        InlineKeyboardButton(text="🎟 Ввести промокод", callback_data="enter_promo")
    )
    builder.row(
        InlineKeyboardButton(text="💳 Подарувати баланс (Створити промокод)", callback_data="create_gift")
    )
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu", style="danger"))"""

content = content.replace(old_cabinet_kb, new_cabinet_kb)

gift_handlers = """
@router.callback_query(F.data == "create_gift")
async def process_create_gift(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    balance = user[3] if user else 0.0
    
    if balance <= 0:
        await callback.answer("❌ У вас порожній баланс!", show_alert=True)
        return
        
    await state.set_state(OrderState.waiting_for_gift_amount)
    text = (
        f"💳 <b>Створення подарункового сертифікату</b>\\n\\n"
        f"Ваш баланс: {balance} ₴\\n"
        "Введіть суму, яку хочете перетворити на промокод (вона спишеться з балансу):\\n\\n"
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
        f"🎉 <b>Сертифікат успішно створено!</b>\\n\\n"
        f"Ваш код: <code>{code}</code>\\n"
        f"Номінал: <b>{amount} ₴</b>\\n\\n"
        "Надішліть цей код другу, і він зможе активувати його в розділі 'Ввести промокод'!",
        parse_mode="HTML"
    )
"""

if "def process_create_gift" not in content:
    content = content + "\n" + gift_handlers

with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "w") as f:
    f.write(content)
