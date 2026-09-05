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
