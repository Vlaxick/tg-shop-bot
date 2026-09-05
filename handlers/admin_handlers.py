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
    await callback.message.edit_caption(
        caption=callback.message.caption + "\n\n✅ <b>Статус:</b> Підтверджено",
        parse_mode="HTML"
    )
    await callback.answer("Замовлення підтверджено!")
    
    # Notify User
    try:
        await bot.send_message(
            chat_id=user_id,
            text=f"✅ Ваше замовлення #{order_id} було успішно підтверджене!\nОчікуйте товар найближчим часом."
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
    await callback.message.edit_caption(
        caption=callback.message.caption + "\n\n❌ <b>Статус:</b> Відхилено",
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
