with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "r") as f:
    content = f.read()

old_cabinet_text = """        text = (
            f"👤 <b>Ваш ID:</b> <code>{user_id}</code>\\n\\n"
            f"💰 <b>Баланс:</b> {user_data[3]} ₴\\n"
            f"🎁 <b>Зароблено на рефералах:</b> {user_data[4]} ₴\\n\\n"
            f"🛒 <b>Всього покупок:</b> {purchases}\\n"
            f"💸 <b>Витрачено:</b> {spent} ₴"
        )"""

new_cabinet_text = """        from database.db import get_vip_rank
        rank_name, discount = get_vip_rank(spent)
        
        discount_text = f" (Знижка {int(discount*100)}%)" if discount > 0 else ""
        
        text = (
            f"👤 <b>Ваш ID:</b> <code>{user_id}</code>\\n"
            f"👑 <b>Ранг:</b> {rank_name}{discount_text}\\n\\n"
            f"💰 <b>Баланс:</b> {user_data[3]} ₴\\n"
            f"🎁 <b>Зароблено на рефералах:</b> {user_data[4]} ₴\\n\\n"
            f"🛒 <b>Всього покупок:</b> {purchases}\\n"
            f"💸 <b>Витрачено:</b> {spent} ₴"
        )"""

content = content.replace(old_cabinet_text, new_cabinet_text)

with open("/Users/macbook/tg-bot/handlers/user_handlers.py", "w") as f:
    f.write(content)
