with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "r") as f:
    content = f.read()

new_start = """@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    data = await state.get_data()
    balance_used = data.get("balance_used")
    if balance_used:
        await db.add_balance(message.from_user.id, balance_used)
    await state.clear()"""

content = content.replace("""@router.message(CommandStart())
async def cmd_start(message: Message):""", new_start)

# We also need to add state: FSMContext to cmd_start imports if it's not in the signature, but we just replaced it.
# Wait, cmd_start had state in my prompt?
# Let's check original cmd_start:
# @router.message(CommandStart())
# async def cmd_start(message: Message):

with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "w") as f:
    f.write(content)
