from aiogram.fsm.state import State, StatesGroup

class OrderState(StatesGroup):
    waiting_for_stars_amount = State()
    waiting_for_recipient = State()
    waiting_for_friend_contact = State()
    waiting_for_payment_method = State()
    waiting_for_payment_proof = State()
    waiting_for_promo = State()
    waiting_for_gift_amount = State()
    waiting_for_topup_amount = State()
    waiting_for_fragment_link = State()
