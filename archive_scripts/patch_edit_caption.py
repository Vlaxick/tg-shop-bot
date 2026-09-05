import re

with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "r") as f:
    content = f.read()

# Replace all occurrences of delete() + answer() with edit_caption()
# Specifically:
# await callback.message.delete()
# await callback.message.answer(text, reply_markup=...)
# -> await callback.message.edit_caption(caption=text, reply_markup=..., parse_mode="HTML")

# For main_menu and cabinet which currently use delete + answer_photo
# We need to change them to use edit_caption too, assuming the message is already a photo.
# BUT wait! If the user sends /start, they get a new photo. If they click a button, the photo is already there, so edit_caption works.
# What if it fails (e.g. they somehow click an old inline keyboard that was text)?
# We can use a try-except block or a custom helper function:

helper = """async def edit_or_send_photo(callback: CallbackQuery, text: str, markup=None):
    from aiogram.types import FSInputFile
    try:
        if callback.message.photo:
            await callback.message.edit_caption(caption=text, reply_markup=markup, parse_mode="HTML")
        else:
            await callback.message.delete()
            await callback.message.answer_photo(photo=FSInputFile("banner.jpg"), caption=text, reply_markup=markup, parse_mode="HTML")
    except Exception as e:
        # Fallback if something goes wrong
        try:
            await callback.message.delete()
        except:
            pass
        await callback.message.answer_photo(photo=FSInputFile("banner.jpg"), caption=text, reply_markup=markup, parse_mode="HTML")
"""

# We should add this helper to `user_handlers.py` right after `router = Router()`

if "async def edit_or_send_photo" not in content:
    content = content.replace("router = Router()", "router = Router()\n\n" + helper)

# Now replace the specific handler bodies

def replace_handler_body(func_name, find_str, replace_str):
    global content
    content = content.replace(find_str, replace_str)

# process_main_menu
replace_handler_body("process_main_menu",
"""    photo = FSInputFile("banner.jpg")
    try:
        await callback.message.delete()
    except:
        pass
    await callback.message.answer_photo(photo=photo, caption=text, reply_markup=get_main_menu_keyboard(), parse_mode="HTML")""",
"""    await edit_or_send_photo(callback, text, get_main_menu_keyboard())""")

# process_cabinet
replace_handler_body("process_cabinet",
"""    photo = FSInputFile("banner.jpg")
    await callback.message.delete()
    await callback.message.answer_photo(photo=photo, caption=text, reply_markup=builder.as_markup(), parse_mode="HTML")""",
"""    await edit_or_send_photo(callback, text, builder.as_markup())""")

# process_shop
replace_handler_body("process_shop",
"""    await callback.message.delete()
    await callback.message.answer(text, reply_markup=get_categories_keyboard(categories))""",
"""    await edit_or_send_photo(callback, text, get_categories_keyboard(categories))""")

# process_category (all 3 variants)
replace_handler_body("process_category",
"""        await callback.message.delete()
        await callback.message.answer(text, reply_markup=get_stars_keyboard(category_id), parse_mode="HTML")""",
"""        await edit_or_send_photo(callback, text, get_stars_keyboard(category_id))""")

replace_handler_body("process_category",
"""        await callback.message.delete()
        await callback.message.answer(text, reply_markup=get_fragment_keyboard(), parse_mode="HTML")""",
"""        await edit_or_send_photo(callback, text, get_fragment_keyboard())""")

replace_handler_body("process_category",
"""        await callback.message.delete()
        await callback.message.answer(text, reply_markup=get_products_keyboard(products, category_id), parse_mode="HTML")""",
"""        await edit_or_send_photo(callback, text, get_products_keyboard(products, category_id))""")

# process_product
replace_handler_body("process_product",
"""    await callback.message.delete()
    await callback.message.answer(text, reply_markup=get_product_action_keyboard(product_id, category_id), parse_mode="HTML")""",
"""    await edit_or_send_photo(callback, text, get_product_action_keyboard(product_id, category_id))""")

# process_my_orders
replace_handler_body("process_my_orders",
"""    await callback.message.delete()
    await callback.message.answer(text, reply_markup=get_back_to_main_keyboard(), parse_mode="HTML")""",
"""    await edit_or_send_photo(callback, text, get_back_to_main_keyboard())""")

# process_support
replace_handler_body("process_support",
"""    await callback.message.delete()
    await callback.message.answer(text, reply_markup=get_back_to_main_keyboard(), parse_mode="HTML")""",
"""    await edit_or_send_photo(callback, text, get_back_to_main_keyboard())""")

# process_referrals
replace_handler_body("process_referrals",
"""    await callback.message.delete()
    await callback.message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")""",
"""    await edit_or_send_photo(callback, text, builder.as_markup())""")

# wait, are there any other callback.message.edit_text? Let's replace them too!
# e.g., if any of the above were still edit_text
replace_handler_body("process_shop",
"""    await callback.message.edit_text(text, reply_markup=get_categories_keyboard(categories))""",
"""    await edit_or_send_photo(callback, text, get_categories_keyboard(categories))""")


with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "w") as f:
    f.write(content)
