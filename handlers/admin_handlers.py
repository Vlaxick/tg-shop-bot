# pyrefly: ignore [missing-import]
from aiogram import Bot, F, Router

# pyrefly: ignore [missing-import]
from aiogram.types import CallbackQuery

from config import ADMIN_IDS
from database import db

router = Router()

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

@router.callback_query(F.data.startswith("admin_take_"))
async def process_admin_take(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.fromuser.id if hasattr(callback, 'fromuser') else callback.from_user.id):
        await callback.answer("У вас немає прав для цієї дії.", show_alert=True)
        return

    data_parts = callback.data.split("_")
    order_id = int(data_parts[2])
    user_id = int(data_parts[3])
    
    # Update DB
    await db.update_order_status(order_id, "in_progress")
    
    # Notify Admin
    from keyboards.inline import get_admin_action_keyboard
    markup = get_admin_action_keyboard(order_id, user_id, "in_progress")
    if callback.message.caption:
        await callback.message.edit_caption(
            caption=callback.message.html_text + "\n\n⏳ <b>Статус:</b> В роботі",
            reply_markup=markup,
            parse_mode="HTML"
        )
    elif callback.message.text:
        await callback.message.edit_text(
            text=callback.message.html_text + "\n\n⏳ <b>Статус:</b> В роботі",
            reply_markup=markup,
            parse_mode="HTML"
        )
    await callback.answer("Замовлення взято в роботу!")
    
    # Notify User
    try:
        from keyboards.inline import get_order_in_progress_keyboard
        msg_text = f"⏳ Ваше замовлення #{order_id} було взято в роботу!\nЯкщо у вас є питання, ви можете зв'язатись із підтримкою."
        await bot.send_message(
            chat_id=user_id,
            text=msg_text,
            reply_markup=get_order_in_progress_keyboard(order_id)
        )
    except Exception as e:
        print(f"Failed to notify user {user_id}: {e}")

@router.callback_query(F.data.startswith("admin_approve_"))
async def process_admin_approve(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.fromuser.id if hasattr(callback, 'fromuser') else callback.from_user.id):
        await callback.answer("У вас немає прав для цієї дії.", show_alert=True)
        return

    data_parts = callback.data.split("_")
    order_id = int(data_parts[2])
    user_id = int(data_parts[3])
    
    # Update DB
    await db.update_order_status(order_id, "approved")
    
    # Notify Admin
    if callback.message.caption:
        await callback.message.edit_caption(
            caption=callback.message.html_text.replace("\n\n⏳ <b>Статус:</b> В роботі", "") + "\n\n✅ <b>Статус:</b> Виконано",
            parse_mode="HTML"
        )
    elif callback.message.text:
        await callback.message.edit_text(
            text=callback.message.html_text.replace("\n\n⏳ <b>Статус:</b> В роботі", "") + "\n\n✅ <b>Статус:</b> Виконано",
            parse_mode="HTML"
        )
    await callback.answer("Замовлення підтверджено!")
    
    # Notify User
    try:
        from keyboards.inline import get_order_approved_keyboard
        order = await db.get_order(order_id)
        msg_text = f"✅ Ваше замовлення #{order_id} було успішно виконане!\n\nВи можете залишити відгук про нашу роботу нижче."
        await bot.send_message(
            chat_id=user_id,
            text=msg_text,
            reply_markup=get_order_approved_keyboard(order_id)
        )
    except Exception as e:
        print(f"Failed to notify user {user_id}: {e}")

@router.callback_query(F.data.startswith("admin_reject_"))
async def process_admin_reject(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас немає прав для цієї дії.", show_alert=True)
        return

    data_parts = callback.data.split("_")
    order_id = int(data_parts[2])
    user_id = int(data_parts[3])
    
    # Update DB
    await db.update_order_status(order_id, "rejected")
    
    # Notify Admin
    if callback.message.caption:
        await callback.message.edit_caption(
            caption=callback.message.html_text + "\n\n❌ <b>Статус:</b> Відхилено",
            parse_mode="HTML"
        )
    elif callback.message.text:
        await callback.message.edit_text(
            text=callback.message.html_text + "\n\n❌ <b>Статус:</b> Відхилено",
            parse_mode="HTML"
        )
    await callback.answer("Замовлення відхилено!")
    
    # Notify User
    try:
        await bot.send_message(
            chat_id=user_id,
            text=f"❌ Ваше замовлення #{order_id} було відхилене адміністратором.\nЗверніться в підтримку для уточнення деталей."
        )
    except Exception as e:
        print(f"Failed to notify user {user_id}: {e}")

from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from states.support import SupportState


@router.callback_query(F.data.startswith("admin_reply_"))
async def process_admin_reply_callback(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас немає прав для цієї дії.", show_alert=True)
        return
        
    data_parts = callback.data.split("_")
    target_user_id = int(data_parts[2])
    order_id = int(data_parts[3])
    
    await state.set_state(SupportState.admin_in_ticket)
    await state.update_data(reply_user_id=target_user_id, reply_order_id=order_id)
    
    from keyboards.inline import get_ticket_admin_active_keyboard
    await bot.send_message(
        callback.from_user.id, 
        f"✅ Ви увійшли в режим чату з користувачем по замовленню #{order_id}.\nВсі ваші повідомлення будуть пересилатися йому.",
        reply_markup=get_ticket_admin_active_keyboard(order_id)
    )
    await callback.answer()

@router.message(F.text == "🛍 Відкриті замовлення")
async def admin_open_orders(message: Message, bot: Bot):
    if not is_admin(message.from_user.id): return
    from database import db
    orders = await db.get_open_orders()
    if not orders:
        await message.answer("Немає відкритих замовлень.")
        return
    from keyboards.inline import get_open_orders_admin_keyboard
    await message.answer("🛍 <b>Відкриті замовлення:</b>", reply_markup=get_open_orders_admin_keyboard(orders), parse_mode="HTML")

@router.message(F.text == "💬 Відкриті тікети")
async def admin_open_tickets(message: Message, bot: Bot):
    if not is_admin(message.from_user.id): return
    from database import db
    tickets = await db.get_open_tickets()
    if not tickets:
        await message.answer("Немає відкритих тікетів.")
        return
    from keyboards.inline import get_open_tickets_keyboard
    await message.answer("💬 <b>Відкриті тікети:</b>", reply_markup=get_open_tickets_keyboard(tickets), parse_mode="HTML")

@router.callback_query(F.data.startswith("admin_view_order_"))
async def admin_view_order(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id): return
    order_id = int(callback.data.split("_")[3])
    from database import db
    order = await db.get_order(order_id)
    if not order:
        await callback.answer("Замовлення не знайдено", show_alert=True)
        return
    
    admin_text = (
        f"🛍 <b>Нове замовлення #{order[0]}</b>\n\n"
        f"👤 Користувач: {order[2]} (ID: {order[1]})\n"
        f"📞 Контакти: {order[3]}\n\n"
        f"📦 Товар: {order[4]}\n"
        f"💵 Сума: {order[5]} ₴\n\n"
        f"Оберіть дію:"
    )
    from keyboards.inline import get_admin_action_keyboard
    await callback.message.answer(admin_text, reply_markup=get_admin_action_keyboard(order[0], order[1]), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == "exit_admin_reply", SupportState.admin_in_ticket)
async def exit_admin_reply(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Ви вийшли з режиму відповіді.")
    await callback.answer()

@router.callback_query(F.data.startswith("close_ticket_admin_"), SupportState.admin_in_ticket)
async def close_ticket_admin(callback: CallbackQuery, state: FSMContext, bot: Bot):
    order_id = int(callback.data.split("_")[3])
    data = await state.get_data()
    target_user_id = data.get('reply_user_id')
    
    # We need ticket_id to close it. But we can just close by order_id since there's max 1 open ticket per order
    # Actually wait, we don't have close_ticket_by_order in db.
    # We can write a quick execute here.
    import aiosqlite

    from database.db import DB_PATH
    async with aiosqlite.connect(DB_PATH) as _db:
        await _db.execute("UPDATE tickets SET status = 'closed' WHERE order_id = ? AND status = 'open'", (order_id,))
        await _db.commit()
    
    await state.clear()
    await callback.message.edit_text(f"Тікет #{order_id} закрито.")
    
    if target_user_id:
        from keyboards.inline import get_back_to_main_keyboard
        try:
            await bot.send_message(target_user_id, "⚠️ Адміністратор завершив цей чат.", reply_markup=get_back_to_main_keyboard())
        except:
            pass
    await callback.answer()

@router.message(SupportState.admin_in_ticket)
async def process_admin_reply_message(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return
        
    data = await state.get_data()
    target_user_id = data.get('reply_user_id')
    order_id = data.get('reply_order_id')
    
    user_text = f"💬 <b>Відповідь від підтримки</b> (Замовлення #{order_id}):\n\n"
    
    try:
        if message.text:
            await bot.send_message(target_user_id, user_text + f"<i>{message.text}</i>", parse_mode="HTML")
        elif message.photo:
            caption = user_text + (f"<i>{message.caption}</i>" if message.caption else "")
            await bot.send_photo(target_user_id, photo=message.photo[-1].file_id, caption=caption, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Помилка при відправці: {e}")

@router.message(F.text == "📊 Статистика")
async def admin_stats(message: Message):
    if not is_admin(message.from_user.id): return
    from database import db
    stats = await db.get_global_stats()
    
    text = (
        "📊 <b>Глобальна статистика магазину:</b>\n\n"
        f"👥 Всього користувачів: <b>{stats['users_count']}</b>\n"
        f"📦 Всього замовлень: <b>{stats['orders_count']}</b>\n"
        f"✅ Успішних замовлень: <b>{stats['approved_orders']}</b>\n"
        f"💰 Загальний дохід: <b>{stats['revenue']:.2f} ₴</b>"
    )
    await message.answer(text, parse_mode="HTML")

from states.admin import AdminState

@router.message(F.text == "📢 Розсилка")
async def admin_broadcast_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    await state.set_state(AdminState.waiting_for_broadcast_message)
    await message.answer(
        "📢 <b>Режим розсилки</b>\n\n"
        "Надішліть повідомлення (текст, фото або відео), яке потрібно розіслати всім користувачам бота.\n\n"
        "<i>Для скасування натисніть /cancel або оберіть будь-який інший пункт меню.</i>",
        parse_mode="HTML"
    )

@router.message(AdminState.waiting_for_broadcast_message)
async def admin_broadcast_send(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id): return
    
    # If they pressed a menu button, cancel
    if message.text in ["🛍 Відкриті замовлення", "💬 Відкриті тікети", "📊 Статистика", "📢 Розсилка"]:
        await state.clear()
        # let it propagate
        return
        
    await state.clear()
    
    from database import db
    users = await db.get_all_users_ids()
    if not users:
        await message.answer("❌ У базі немає користувачів для розсилки.")
        return
        
    await message.answer(f"⏳ Розпочинаю розсилку для {len(users)} користувачів...")
    
    success = 0
    failed = 0
    import asyncio
    
    for uid in users:
        try:
            await message.copy_to(uid)
            success += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05) # Prevent flood wait
        
    await message.answer(
        "✅ <b>Розсилка завершена!</b>\n\n"
        f"📨 Успішно доставлено: {success}\n"
        f"🚫 Заблокували бота / Помилок: {failed}",
        parse_mode="HTML"
    )

from states.admin import AdminProductState

@router.message(F.text == "📦 Управління товарами")
async def admin_product_manager(message: Message):
    if not is_admin(message.from_user.id): return
    from keyboards.inline import get_admin_product_manager_keyboard
    await message.answer("📦 <b>Менеджер товарів</b>\nОберіть дію:", reply_markup=get_admin_product_manager_keyboard(), parse_mode="HTML")

@router.callback_query(F.data == "admin_cancel_product")
async def admin_cancel_product(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id): return
    await state.clear()
    await callback.message.edit_text("❌ Дію скасовано.")
    await callback.answer()

# --- ADD CATEGORY ---
@router.callback_query(F.data == "admin_add_category")
async def admin_add_category_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id): return
    await state.set_state(AdminProductState.waiting_for_new_category_name)
    await callback.message.edit_text("Введіть назву нової категорії:")
    await callback.answer()

@router.message(AdminProductState.waiting_for_new_category_name)
async def admin_add_category_save(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    from database import db
    await db.add_category(message.text)
    await state.clear()
    await message.answer(f"✅ Категорію <b>{message.text}</b> додано!", parse_mode="HTML")

# --- ADD PRODUCT ---
@router.callback_query(F.data == "admin_add_product")
async def admin_add_product_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id): return
    from database import db
    from keyboards.inline import get_admin_categories_selection_keyboard
    categories = await db.get_categories()
    if not categories:
        await callback.message.edit_text("❌ Спочатку додайте хоча б одну категорію.")
        return
    await state.set_state(AdminProductState.waiting_for_product_category)
    await callback.message.edit_text("Оберіть категорію для нового товару:", reply_markup=get_admin_categories_selection_keyboard(categories))
    await callback.answer()

@router.callback_query(F.data.startswith("admin_sel_cat_"), AdminProductState.waiting_for_product_category)
async def admin_sel_cat(callback: CallbackQuery, state: FSMContext):
    cat_id = int(callback.data.split("_")[3])
    await state.update_data(new_prod_cat_id=cat_id)
    await state.set_state(AdminProductState.waiting_for_product_name)
    await callback.message.edit_text("Введіть <b>назву</b> товару:", parse_mode="HTML")
    await callback.answer()

@router.message(AdminProductState.waiting_for_product_name)
async def admin_add_product_name(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    await state.update_data(new_prod_name=message.text)
    await state.set_state(AdminProductState.waiting_for_product_desc)
    await message.answer("Введіть <b>опис</b> товару:", parse_mode="HTML")

@router.message(AdminProductState.waiting_for_product_desc)
async def admin_add_product_desc(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    await state.update_data(new_prod_desc=message.text)
    await state.set_state(AdminProductState.waiting_for_product_price)
    await message.answer("Введіть <b>ціну</b> товару (число, наприклад 150 або 299.99):", parse_mode="HTML")

@router.message(AdminProductState.waiting_for_product_price)
async def admin_add_product_price(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id): return
    try:
        price = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("❌ Будь ласка, введіть коректне число.")
        return
        
    data = await state.get_data()
    from database import db
    await db.add_product(
        category_id=data['new_prod_cat_id'],
        name=data['new_prod_name'],
        description=data['new_prod_desc'],
        price=price
    )
    await state.clear()
    await message.answer(f"✅ Товар <b>{data['new_prod_name']}</b> за {price}₴ успішно додано!", parse_mode="HTML")

# --- DELETE PRODUCT ---
@router.callback_query(F.data == "admin_delete_product")
async def admin_delete_product_start(callback: CallbackQuery):
    if not is_admin(callback.from_user.id): return
    from database import db
    from keyboards.inline import get_admin_products_deletion_keyboard
    products = await db.get_all_products()
    if not products:
        await callback.message.edit_text("Немає товарів для видалення.")
        return
    await callback.message.edit_text("Оберіть товар для <b>ВИДАЛЕННЯ</b>:", reply_markup=get_admin_products_deletion_keyboard(products), parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data.startswith("admin_del_prod_"))
async def admin_del_prod_exec(callback: CallbackQuery):
    if not is_admin(callback.from_user.id): return
    prod_id = int(callback.data.split("_")[3])
    from database import db
    await db.delete_product(prod_id)
    await callback.message.edit_text(f"✅ Товар #{prod_id} видалено.")
    await callback.answer()
