import re

with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "r") as f:
    content = f.read()

refund_logic = """    data = await state.get_data()
    balance_used = data.get("balance_used")
    if balance_used:
        await db.add_balance(message.from_user.id, balance_used)
"""

refund_logic_cb = """    data = await state.get_data()
    balance_used = data.get("balance_used")
    if balance_used:
        await db.add_balance(callback.from_user.id, balance_used)
"""

content = content.replace(refund_logic, "")
content = content.replace(refund_logic_cb, "")

with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "w") as f:
    f.write(content)

