with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "r") as f:
    content = f.read()

old_topup = """@router.callback_query(F.data == "topup_balance")
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
    await callback.answer()"""

new_topup = """@router.callback_query(F.data == "topup_balance")
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
        "💳 <b>Поповнення балансу</b>\\n\\n"
        "Оберіть суму для поповнення або введіть її вручну повідомленням:\\n\\n"
        "<i>(Мінімальна сума: 10 ₴)</i>"
    )
    await edit_or_send_photo(callback, text, builder.as_markup())
    await state.update_data(prompt_msg_id=callback.message.message_id)
    await callback.answer()"""

content = content.replace(old_topup, new_topup)

old_start = """async def _start_topup_payment(message: Message, user, amount: float, state: FSMContext, callback: CallbackQuery = None):
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
        await message.answer_photo(photo=FSInputFile("banner.jpg"), caption=text, reply_markup=markup, parse_mode="HTML")"""

new_start = """async def _start_topup_payment(message: Message, user, amount: float, state: FSMContext, callback: CallbackQuery = None):
    # Create custom product for topup
    product_id = await db.get_or_create_custom_product("Поповнення балансу", amount)
    
    # We pretend this is a normal order
    await state.update_data(product_id=product_id, price=amount, original_price=amount, balance_to_deduct=0)
    
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
        await message.answer_photo(photo=FSInputFile("banner.jpg"), caption=text, reply_markup=markup, parse_mode="HTML")"""

content = content.replace(old_start, new_start)

with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "w") as f:
    f.write(content)
