from aiogram.fsm.state import State, StatesGroup

class AdminState(StatesGroup):
    waiting_for_broadcast_message = State()

class AdminProductState(StatesGroup):
    waiting_for_new_category_name = State()
    
    waiting_for_product_category = State()
    waiting_for_product_name = State()
    waiting_for_product_desc = State()
    waiting_for_product_price = State()
