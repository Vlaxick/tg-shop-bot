with open("/Users/macbook/tg-bot/handlers/admin_handlers.py", "r") as f:
    content = f.read()

content = content.replace("from aiogram.types import CallbackQuery", "from aiogram.types import CallbackQuery, Message\nfrom aiogram.filters import Command")

admin_cmds = """
@router.message(Command("addbalance"))
async def cmd_addbalance(message: Message):
    if not is_admin(message.from_user.id):
        return
    args = message.text.split()
    if len(args) != 3:
        await message.answer("❌ Використання: /addbalance <ID> <Сума>")
        return
    try:
        user_id = int(args[1])
        amount = float(args[2])
        await db.add_balance(user_id, amount, is_referral=False)
        await message.answer(f"✅ Успішно додано <b>{amount} ₴</b> користувачу <code>{user_id}</code>", parse_mode="HTML")
    except ValueError:
        await message.answer("❌ Помилка: ID та Сума мають бути числами.")

@router.message(Command("setbalance"))
async def cmd_setbalance(message: Message):
    if not is_admin(message.from_user.id):
        return
    args = message.text.split()
    if len(args) != 3:
        await message.answer("❌ Використання: /setbalance <ID> <Сума>")
        return
    try:
        user_id = int(args[1])
        amount = float(args[2])
        
        # We need to set balance exactly. We can do it via raw execute here since db.py might lack set_balance
        import aiosqlite
        from database.db import DB_PATH
        async with aiosqlite.connect(DB_PATH) as _db:
            await _db.execute('UPDATE users SET balance = ? WHERE user_id = ?', (amount, user_id))
            await _db.commit()
            
        await message.answer(f"✅ Баланс користувача <code>{user_id}</code> встановлено на <b>{amount} ₴</b>", parse_mode="HTML")
    except ValueError:
        await message.answer("❌ Помилка: ID та Сума мають бути числами.")

@router.message(Command("user"))
async def cmd_user(message: Message):
    if not is_admin(message.from_user.id):
        return
    args = message.text.split()
    if len(args) != 2:
        await message.answer("❌ Використання: /user <ID>")
        return
    try:
        user_id = int(args[1])
        user = await db.get_user(user_id)
        if not user:
            await message.answer("❌ Користувача не знайдено.")
            return
            
        stats = await db.get_user_stats(user_id)
        purchases = stats[0]
        spent = stats[1]
        
        text = (
            f"👤 <b>Користувач {user_id}</b>\\n"
            f"Нік: @{user[1]}\\n"
            f"Баланс: {user[3]} ₴\\n"
            f"Реферальні: {user[4]} ₴\\n"
            f"Покупок: {purchases} (На суму: {spent} ₴)"
        )
        await message.answer(text, parse_mode="HTML")
    except ValueError:
        await message.answer("❌ Помилка: ID має бути числом.")
"""

content = content.replace("router = Router()", "router = Router()\n" + admin_cmds)

with open("/Users/macbook/tg-bot/handlers/admin_handlers.py", "w") as f:
    f.write(content)
