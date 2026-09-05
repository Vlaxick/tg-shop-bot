with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "r") as f:
    content = f.read()

# Add Cancel command handler
cancel_code = """@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Дію скасовано. Напишіть /start для повернення в головне меню.")
"""

if "CommandStart" in content:
    content = content.replace("from aiogram.filters import CommandStart", "from aiogram.filters import CommandStart, Command")
    
if "cmd_cancel" not in content:
    # insert before cmd_start
    content = content.replace("@router.message(CommandStart())", cancel_code + "\n@router.message(CommandStart())")

with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "w") as f:
    f.write(content)
