from aiogram.fsm.state import State, StatesGroup


class SupportState(StatesGroup):
    user_in_ticket = State()
    admin_in_ticket = State()
