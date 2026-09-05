import re

with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "r") as f:
    content = f.read()

handler = """
@router.callback_query(F.data == "referrals")
async def process_referrals(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    balance = user[3] if user else 0.0
    bot_info = await callback.bot.get_me()
    bot_username = bot_info.username
    ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"
    
    text = (
        "🎁 <b>Реферальна програма та Баланс</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"💰 <b>Ваш баланс:</b> {balance} ₴\n\n"
        "🤝 <b>Запрошуйте друзів та заробляйте:</b>\n"
        "• <b>50%</b> від суми першої покупки вашого друга!\n"
        "• <b>5%</b> від усіх наступних покупок друга!\n\n"
        f"🔗 <b>Ваше реферальне посилання:</b>\n<code>{ref_link}</code>\n\n"
        "<i>Просто надішліть це посилання друзям. Коли вони здійснять покупку, гроші автоматично зарахуються на ваш баланс!</i>"
    )
    
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu", style="danger"))
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    await callback.answer()
"""

# append to the end of user_handlers.py
if "process_referrals" not in content:
    with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "a") as f:
        f.write("\nfrom aiogram.utils.keyboard import InlineKeyboardBuilder\n" + handler)

