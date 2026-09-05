# pyrefly: ignore [missing-import]
from aiogram import Router, F, Bot
# pyrefly: ignore [missing-import]
from aiogram.types import CallbackQuery
from database import db
from config import ADMIN_IDS

router = Router()

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

@router.callback_query(F.data.startswith("admin_approve_"))
async def process_admin_approve(callback: CallbackQuery, bot: Bot):
    if not is_admin(callback.from_user.id):
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
            caption=callback.message.html_text + "\n\n✅ <b>Статус:</b> Підтверджено",
            parse_mode="HTML"
        )
    elif callback.message.text:
        await callback.message.edit_text(
            text=callback.message.html_text + "\n\n✅ <b>Статус:</b> Підтверджено",
            parse_mode="HTML"
        )
    await callback.answer("Замовлення підтверджено!")
    
    # Notify User
    try:
        from keyboards.inline import get_order_approved_keyboard
        order = await db.get_order(order_id)
        if order and order[7] in (3, 5):
            msg_text = f"✅ Ваше замовлення #{order_id} було успішно підтверджене!\nОчікуйте повідомлення від адміна."
        else:
            msg_text = f"✅ Ваше замовлення #{order_id} було успішно підтверджене!\nОчікуйте товар найближчим часом."
            
        await bot.send_message(
            chat_id=user_id,
            text=msg_text,
            reply_markup=get_order_approved_keyboard()
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
async def process_admin_reply_callback(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас немає прав для цієї дії.", show_alert=True)
        return
        
    data_parts = callback.data.split("_")
    target_user_id = int(data_parts[2])
    order_id = int(data_parts[3])
    
    await state.set_state(SupportState.waiting_for_reply)
    await state.update_data(reply_user_id=target_user_id, reply_order_id=order_id)
    
    await callback.message.answer(f"Напишіть вашу відповідь для користувача (Замовлення #{order_id}):\n(Текст або фото/відео)")
    await callback.answer()

@router.message(SupportState.waiting_for_reply)
async def process_admin_reply_message(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return
        
    data = await state.get_data()
    target_user_id = data.get('reply_user_id')
    order_id = data.get('reply_order_id')
    
    from keyboards.inline import get_back_to_main_keyboard
    user_text = f"💬 <b>Відповідь від підтримки</b> (Замовлення #{order_id}):"
    
    try:
        await bot.send_message(target_user_id, user_text, parse_mode="HTML")
        await message.copy_to(target_user_id)
        await bot.send_message(target_user_id, "<i>Щоб відповісти, перейдіть в Мої замовлення та знову натисніть Зв'язатись з підтримкою.</i>", reply_markup=get_back_to_main_keyboard(), parse_mode="HTML")
        await message.answer("✅ Відповідь успішно надіслана користувачу!")
    except Exception as e:
        await message.answer(f"❌ Помилка при відправці: {e}")
        
    await state.clear()
