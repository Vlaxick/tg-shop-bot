with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "r") as f:
    content = f.read()

casino_handlers = """
@router.callback_query(F.data == "casino")
async def process_casino_menu(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = await db.get_user(user_id)
    balance = user[3] if user else 0.0
    
    text = (
        "🎰 <b>Вітаємо в Казино!</b>\\n\\n"
        "Правила прості: ви робите ставку і крутите слоти.\\n"
        "Виграшні комбінації (3 в ряд):\\n"
        "🍒🍒🍒 або 🍋🍋🍋 = <b>x5</b> від ставки\\n"
        "💎💎💎 = <b>Джекпот (x10)</b>\\n\\n"
        f"Ваш баланс: <b>{balance} ₴</b>\\n"
        "Оберіть суму ставки:"
    )
    from keyboards.inline import get_casino_keyboard
    await edit_or_send_photo(callback, text, get_casino_keyboard())
    await callback.answer()

import asyncio

@router.callback_query(F.data.startswith("bet_"))
async def process_casino_bet(callback: CallbackQuery, bot: Bot):
    bet = float(callback.data.split("_")[1])
    user_id = callback.from_user.id
    
    # deduct balance first
    success = await db.deduct_balance(user_id, bet)
    if not success:
        await callback.answer("❌ Недостатньо коштів на балансі!", show_alert=True)
        return
        
    await callback.message.delete()
    msg = await callback.message.answer_dice(emoji="🎰")
    
    # Value 1, 22, 43 is x5. Value 64 is x10.
    # We must wait a few seconds for the animation
    await asyncio.sleep(2.0)
    
    win_amount = 0
    if msg.dice.value == 64: # 777
        win_amount = bet * 10
        await bot.send_message(user_id, f"🎉 <b>ДЖЕКПОТ!</b> Ви виграли <b>{win_amount} ₴</b>!", parse_mode="HTML")
    elif msg.dice.value in (1, 22, 43):
        win_amount = bet * 5
        await bot.send_message(user_id, f"🎊 <b>ВИГРАШ!</b> Ви виграли <b>{win_amount} ₴</b>!", parse_mode="HTML")
    else:
        await bot.send_message(user_id, f"😔 На жаль, ви програли. Спробуйте ще раз!")
        
    if win_amount > 0:
        await db.add_balance(user_id, win_amount)
        
    # Send menu back
    await process_casino_menu(callback)
"""

if "def process_casino_menu" not in content:
    content = content + "\n" + casino_handlers

with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "w") as f:
    f.write(content)
