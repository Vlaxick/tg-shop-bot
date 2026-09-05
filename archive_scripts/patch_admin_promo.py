with open("/Users/macbook/tg-bot/handlers/admin_handlers.py", "r") as f:
    content = f.read()

promo_code = """
@router.message(Command("createpromo"))
async def cmd_createpromo(message: Message):
    if not is_admin(message.from_user.id):
        return
    args = message.text.split()
    if len(args) != 4:
        await message.answer("❌ Використання: /createpromo <КОД> <Сума> <К-ть_використань>")
        return
    try:
        code = args[1]
        amount = float(args[2])
        uses = int(args[3])
        await db.create_promocode(code, amount, uses)
        await message.answer(f"✅ Промокод <code>{code}</code> на <b>{amount} ₴</b> створено! (Ліміт: {uses})", parse_mode="HTML")
    except ValueError:
        await message.answer("❌ Помилка: Сума та Кількість мають бути числами.")
"""

if "def cmd_createpromo" not in content:
    content = content.replace("router = Router()\n", "router = Router()\n" + promo_code)

with open("/Users/macbook/tg-bot/handlers/admin_handlers.py", "w") as f:
    f.write(content)
