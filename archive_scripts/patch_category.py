
with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "r") as f:
    content = f.read()

new_process_category = """@router.callback_query(F.data.startswith("cat_"))
async def process_category(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    balance_used = data.get("balance_used")
    if balance_used:
        await db.add_balance(callback.from_user.id, balance_used)
    await state.clear()
    
    category_id = int(callback.data.split("_")[1])"""

content = content.replace("""@router.callback_query(F.data.startswith("cat_"))
async def process_category(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[1])""", new_process_category)

# Same for main_menu callback
new_process_main_menu = """@router.callback_query(F.data == "main_menu")
async def process_main_menu(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    balance_used = data.get("balance_used")
    if balance_used:
        await db.add_balance(callback.from_user.id, balance_used)
    await state.clear()"""

content = content.replace("""@router.callback_query(F.data == "main_menu")
async def process_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()""", new_process_main_menu)

# Same for shop callback
new_process_shop = """@router.callback_query(F.data == "shop")
async def process_shop(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    balance_used = data.get("balance_used")
    if balance_used:
        await db.add_balance(callback.from_user.id, balance_used)
    await state.clear()"""

content = content.replace("""@router.callback_query(F.data == "shop")
async def process_shop(callback: CallbackQuery, state: FSMContext):
    await state.clear()""", new_process_shop)

with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "w") as f:
    f.write(content)
