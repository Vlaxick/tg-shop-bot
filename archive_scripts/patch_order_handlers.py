
with open("/Users/macbook/tg-bot/handlers/order_handlers.py", "r") as f:
    content = f.read()

# Add FSInputFile
if "FSInputFile" not in content:
    content = content.replace("from aiogram.types import Message, CallbackQuery", "from aiogram.types import Message, CallbackQuery, FSInputFile")

# Add helper
helper = """async def edit_or_send_photo(callback: CallbackQuery, text: str, markup=None):
    from aiogram.types import FSInputFile
    try:
        if callback.message.photo:
            await callback.message.edit_caption(caption=text, reply_markup=markup, parse_mode="HTML")
        else:
            await callback.message.delete()
            await callback.message.answer_photo(photo=FSInputFile("banner.jpg"), caption=text, reply_markup=markup, parse_mode="HTML")
    except Exception as e:
        try:
            await callback.message.delete()
        except:
            pass
        await callback.message.answer_photo(photo=FSInputFile("banner.jpg"), caption=text, reply_markup=markup, parse_mode="HTML")
"""

if "async def edit_or_send_photo" not in content:
    content = content.replace("router = Router()", "router = Router()\n\n" + helper)

# Replace all callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
# We will use regex to find and replace
# A simpler way is to just replace `.edit_text` calls manually or with regex.


# 1. replace: await message_or_callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
content = content.replace('await message_or_callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")', 
                          'await edit_or_send_photo(message_or_callback, text, markup)')

# 2. replace: await callback.message.edit_text(text, reply_markup=get_back_to_main_keyboard(), parse_mode="HTML")
content = content.replace('await callback.message.edit_text(text, reply_markup=get_back_to_main_keyboard(), parse_mode="HTML")',
                          'await edit_or_send_photo(callback, text, get_back_to_main_keyboard())')

# 3. replace: await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
content = content.replace('await callback.message.edit_text(text, reply_markup=markup, parse_mode="HTML")',
                          'await edit_or_send_photo(callback, text, markup)')

# 4. the partial payment one:
# await callback.message.edit_text(
#        f"✅ <b>Баланс списано!</b> ({balance} ₴)\n\n"
#        f"Залишилось доплатити: <b>{new_price} ₴</b>\n"
#        "Оберіть спосіб доплати:",
#        reply_markup=markup,
#        parse_mode="HTML"
#    )
old_partial = """    await callback.message.edit_text(
        f"✅ <b>Баланс списано!</b> ({balance} ₴)\\n\\n"
        f"Залишилось доплатити: <b>{new_price} ₴</b>\\n"
        "Оберіть спосіб доплати:",
        reply_markup=markup,
        parse_mode="HTML"
    )"""
new_partial = """    text_partial = (
        f"✅ <b>Баланс списано!</b> ({balance} ₴)\\n\\n"
        f"Залишилось доплатити: <b>{new_price} ₴</b>\\n"
        "Оберіть спосіб доплати:"
    )
    await edit_or_send_photo(callback, text_partial, markup)"""
content = content.replace(old_partial, new_partial)

# 5. The pay_balance success:
# await callback.message.edit_text("✅ <b>Оплата успішна!</b>\n\nКошти списано з балансу. Очікуйте на видачу товару.", parse_mode="HTML")
old_balance_success = """    await callback.message.edit_text("✅ <b>Оплата успішна!</b>\\n\\nКошти списано з балансу. Очікуйте на видачу товару.", parse_mode="HTML")"""
new_balance_success = """    await edit_or_send_photo(callback, "✅ <b>Оплата успішна!</b>\\n\\nКошти списано з балансу. Очікуйте на видачу товару.", get_back_to_main_keyboard())"""
content = content.replace(old_balance_success, new_balance_success)

# 6. The pay_crypto warning (not implemented, wait pay_crypto is an answer alert)
# No edit_text there.

# 7. payment verification failed
# await callback.message.edit_text(
#        "⏳ Оплата ще не надійшла.\n\n"
#        "Спробуйте перевірити ще раз за кілька секунд.",
#        reply_markup=markup,
#        parse_mode="HTML"
#    )
old_verif = """    await callback.message.edit_text(
        "⏳ Оплата ще не надійшла.\\n\\n"
        "Спробуйте перевірити ще раз за кілька секунд.",
        reply_markup=markup,
        parse_mode="HTML"
    )"""
new_verif = """    await edit_or_send_photo(callback, "⏳ Оплата ще не надійшла.\\n\\nСпробуйте перевірити ще раз за кілька секунд.", markup)"""
content = content.replace(old_verif, new_verif)

with open("/Users/macbook/tg-bot/handlers/order_handlers.py", "w") as f:
    f.write(content)
