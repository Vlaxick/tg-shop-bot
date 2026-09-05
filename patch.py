import re

with open("/Users/macbook/tg-bot/handlers/order_handlers.py", "r") as f:
    content = f.read()

new_handler = """STOCK_GIFTS = {
    "buy_gift_heart": {"name": "💝 Серце", "price": 12},
    "buy_gift_bear": {"name": "🧸 Ведмедик", "price": 12},
    "buy_gift_box": {"name": "🎁 Подарунок", "price": 20},
    "buy_gift_rose": {"name": "🌹 Троянда", "price": 20},
    "buy_gift_cake": {"name": "🎂 Торт", "price": 40},
    "buy_gift_bouquet": {"name": "💐 Букет", "price": 40},
    "buy_gift_champagne": {"name": "🍾 Шампанське", "price": 40},
    "buy_gift_rocket": {"name": "🚀 Ракета", "price": 40},
    "buy_gift_trophy": {"name": "🏆 Кубок", "price": 80},
    "buy_gift_ring": {"name": "💍 Каблучка", "price": 80},
    "buy_gift_diamond": {"name": "💎 Діамант", "price": 80},
}

@router.callback_query(F.data.startswith("buy_gift_"))
async def process_buy_gift_button(callback: CallbackQuery, state: FSMContext):
    gift_data = STOCK_GIFTS.get(callback.data)
    if not gift_data:
        await callback.answer("Товар не знайдено", show_alert=True)
        return
    await start_order_recipient_flow(callback, state, gift_data["name"], gift_data["price"], 0)

@router.callback_query(F.data.startswith("buy_") & ~F.data.startswith("buy_gift_"))"""

content = content.replace('@router.callback_query(F.data.startswith("buy_"))', new_handler)

with open("/Users/macbook/tg-bot/handlers/order_handlers.py", "w") as f:
    f.write(content)
