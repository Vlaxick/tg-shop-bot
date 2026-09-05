import re

with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "r") as f:
    content = f.read()

# 1. Import FSInputFile
if "FSInputFile" not in content:
    content = content.replace("from aiogram.types import Message, CallbackQuery, InlineKeyboardButton", "from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, FSInputFile")

# 2. cmd_start text and photo
new_start_text = """    text = (
        "😋 Привіт, <b>{username}</b>!\\n\\n"
        "Тут ви можете швидко придбати цифрові товари та підписки на свій акаунт.\\n\\n"
        "⭐️ За допомогою нашого сервісу вже виконано безліч успішних замовлень!"
    ).format(username=message.from_user.first_name)
    
    photo = FSInputFile("banner.jpg")
    await message.answer_photo(photo=photo, caption=text, reply_markup=get_main_menu_keyboard(), parse_mode="HTML")"""

# Find where `text = (` starts in cmd_start
import re
start_idx = content.find('    text = (\n        "👋 Вітаємо')
end_idx = content.find('    await message.answer(text, reply_markup=get_main_menu_keyboard())') + len('    await message.answer(text, reply_markup=get_main_menu_keyboard())')
if start_idx != -1 and end_idx != -1:
    content = content[:start_idx] + new_start_text + content[end_idx:]

# 3. process_main_menu
old_main_menu = """@router.callback_query(F.data == "main_menu")
async def process_main_menu(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    balance_used = data.get("balance_used")
    if balance_used:
        await db.add_balance(callback.from_user.id, balance_used)
    await state.clear()
    text = "👋 Вітаємо у нашому магазині цифрових товарів!\\n\\nОберіть потрібний розділ нижче:"
    await callback.message.edit_text(text, reply_markup=get_main_menu_keyboard())
    await callback.answer()"""

new_main_menu = """@router.callback_query(F.data == "main_menu")
async def process_main_menu(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    balance_used = data.get("balance_used")
    if balance_used:
        await db.add_balance(callback.from_user.id, balance_used)
    await state.clear()
    
    text = (
        "😋 Привіт, <b>{username}</b>!\\n\\n"
        "Тут ви можете швидко придбати цифрові товари та підписки на свій акаунт.\\n\\n"
        "⭐️ За допомогою нашого сервісу вже виконано безліч успішних замовлень!"
    ).format(username=callback.from_user.first_name)
    
    photo = FSInputFile("banner.jpg")
    await callback.message.delete()
    await callback.message.answer_photo(photo=photo, caption=text, reply_markup=get_main_menu_keyboard(), parse_mode="HTML")
    await callback.answer()"""

content = content.replace(old_main_menu, new_main_menu)

# 4. process_cabinet
old_cabinet = """@router.callback_query(F.data == "cabinet")
async def process_cabinet(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    balance = user[3] if user else 0.0
    referral_earnings = user[4] if user and len(user) > 4 else 0.0
    
    total_purchases, total_spent = await db.get_user_stats(user_id)
    
    text = (
        "👤 <b>Мій кабінет</b>\\n"
        "━━━━━━━━━━━━━━━━━━\\n\\n"
        f"🛍 <b>Покупок:</b> {total_purchases}\\n"
        f"💸 <b>Витрачено:</b> {total_spent} ₴\\n\\n"
        f"💰 <b>Поточний баланс:</b> {balance} ₴\\n"
        f"🎁 <b>Зароблено з рефералів:</b> {referral_earnings} ₴\\n"
    )
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu", style="danger"))
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()"""

new_cabinet = """@router.callback_query(F.data == "cabinet")
async def process_cabinet(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    balance = user[3] if user else 0.0
    referral_earnings = user[4] if user and len(user) > 4 else 0.0
    
    total_purchases, total_spent = await db.get_user_stats(user_id)
    
    text = (
        "🎩 <b>Ваш профіль</b>\\n\\n"
        f"👤 <b>Ваш ID:</b> <code>{user_id}</code>\\n"
        f"👥 <b>Реферальний баланс:</b> {referral_earnings} ₴\\n\\n"
        f"🛍 <b>Всього покупок:</b> {total_purchases}\\n"
        f"💸 <b>Загальний депозит:</b> {total_spent} ₴\\n\\n"
        f"💰 <b>Баланс:</b> {balance} ₴"
    )
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="👥 Реферальна система", callback_data="referrals"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu", style="danger"))
    
    photo = FSInputFile("banner.jpg")
    await callback.message.delete()
    await callback.message.answer_photo(photo=photo, caption=text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()"""

content = content.replace(old_cabinet, new_cabinet)

# 5. Make sure other handlers that edit_text handle the transition from photo to text correctly.
# If a message is a photo, edit_text will throw an error "Message is not modified" or "There is no text in the message to edit" because you can't edit_text on a photo.
# You have to delete() and answer().
# We need to replace all `await callback.message.edit_text` with `await callback.message.delete(); await callback.message.answer` IF they might come from a photo menu.
# Actually, it's safer to always delete and answer for all top-level menus if they are mixed with photos.
# Let's replace edit_text in process_shop, process_my_orders, process_referrals, process_category.

def replace_edit_text(func_name, match_text, replace_with):
    global content
    content = content.replace(match_text, replace_with)

# process_shop
replace_edit_text('process_shop', 
    'await callback.message.edit_text(text, reply_markup=get_categories_keyboard(categories))',
    'await callback.message.delete()\n    await callback.message.answer(text, reply_markup=get_categories_keyboard(categories))')

# process_category
replace_edit_text('process_category',
    'await callback.message.edit_text(text, reply_markup=get_stars_keyboard(category_id), parse_mode="HTML")',
    'await callback.message.delete()\n        await callback.message.answer(text, reply_markup=get_stars_keyboard(category_id), parse_mode="HTML")')
replace_edit_text('process_category',
    'await callback.message.edit_text(text, reply_markup=get_fragment_keyboard(), parse_mode="HTML")',
    'await callback.message.delete()\n        await callback.message.answer(text, reply_markup=get_fragment_keyboard(), parse_mode="HTML")')
replace_edit_text('process_category',
    'await callback.message.edit_text(text, reply_markup=get_products_keyboard(products, category_id), parse_mode="HTML")',
    'await callback.message.delete()\n        await callback.message.answer(text, reply_markup=get_products_keyboard(products, category_id), parse_mode="HTML")')

# process_product
replace_edit_text('process_product',
    'await callback.message.edit_text(text, reply_markup=get_product_action_keyboard(product_id, category_id), parse_mode="HTML")',
    'await callback.message.delete()\n    await callback.message.answer(text, reply_markup=get_product_action_keyboard(product_id, category_id), parse_mode="HTML")')

# process_my_orders
replace_edit_text('process_my_orders',
    'await callback.message.edit_text(text, reply_markup=get_back_to_main_keyboard(), parse_mode="HTML")',
    'await callback.message.delete()\n    await callback.message.answer(text, reply_markup=get_back_to_main_keyboard(), parse_mode="HTML")')

# process_support
replace_edit_text('process_support',
    'await callback.message.edit_text(text, reply_markup=get_back_to_main_keyboard(), parse_mode="HTML")',
    'await callback.message.delete()\n    await callback.message.answer(text, reply_markup=get_back_to_main_keyboard(), parse_mode="HTML")')

# process_referrals
replace_edit_text('process_referrals',
    'await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")',
    'await callback.message.delete()\n    await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")')

with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "w") as f:
    f.write(content)
