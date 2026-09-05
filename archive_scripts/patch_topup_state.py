with open("/Users/macbook/tg-bot/states/order.py", "r") as f:
    content = f.read()

if "waiting_for_topup_amount" not in content:
    content = content.replace("waiting_for_gift_amount = State()", "waiting_for_gift_amount = State()\n    waiting_for_topup_amount = State()")

with open("/Users/macbook/tg-bot/states/order.py", "w") as f:
    f.write(content)

with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "r") as f:
    content = f.read()

topup_handlers = """
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
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu", style="danger"))
    
    text = (
        "💳 <b>Поповнення балансу</b>\\n\\n"
        "Оберіть суму для поповнення або введіть її вручну повідомленням:\\n\\n"
        "<i>(Мінімальна сума: 10 ₴)</i>"
    )
    await edit_or_send_photo(callback, text, builder.as_markup())
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
    
    # We pretend this is a normal order
    await state.update_data(product_id=product_id, price=amount, original_price=amount, balance_to_deduct=0)
    
    from keyboards.inline import get_payment_method_keyboard
    text = (
        f"💳 <b>Оберіть спосіб оплати для поповнення балансу на {amount} ₴:</b>"
    )
    markup = get_payment_method_keyboard(amount, category_id=0, balance=0, is_partial=False)
    
    await state.set_state(OrderState.waiting_for_payment_method)
    
    if callback:
        await edit_or_send_photo(callback, text, markup)
        await callback.answer()
    else:
        from aiogram.types import FSInputFile
        try:
            await message.delete()
        except:
            pass
        await message.answer_photo(photo=FSInputFile("banner.jpg"), caption=text, reply_markup=markup, parse_mode="HTML")
"""

if "def process_topup_balance" not in content:
    content = content + "\n" + topup_handlers

with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "w") as f:
    f.write(content)
