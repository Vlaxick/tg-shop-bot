from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def get_admin_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍 Відкриті замовлення"), KeyboardButton(text="💬 Відкриті тікети")],
            [KeyboardButton(text="📊 Статистика"), KeyboardButton(text="📢 Розсилка")],
            [KeyboardButton(text="📦 Управління товарами")]
        ],
        resize_keyboard=True,
        is_persistent=True
    )
