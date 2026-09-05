with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "r") as f:
    content = f.read()

# Make sure StateFilter is imported
if "from aiogram.filters import StateFilter" not in content:
    content = content.replace("from aiogram.filters import CommandStart, Command", "from aiogram.filters import CommandStart, Command, StateFilter")

# Replace cmd_cancel
old_cancel = """@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Дію скасовано. Напишіть /start для повернення в головне меню.")
"""

new_cancel = """@router.message(Command("cancel"), StateFilter("*"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Дію скасовано. Напишіть /start для повернення в головне меню.")
"""

content = content.replace(old_cancel, new_cancel)

with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "w") as f:
    f.write(content)

