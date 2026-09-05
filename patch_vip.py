import re

with open("/Users/macbook/tg-bot/database/db.py", "r") as f:
    content = f.read()

vip_logic = """
def get_vip_rank(spent: float) -> tuple[str, float]:
    \"\"\"Returns (Rank Name, Discount Percentage)\"\"\"
    if spent >= 2000:
        return ("🥇 Золото", 0.05)
    elif spent >= 500:
        return ("🥈 Срібло", 0.02)
    else:
        return ("🥉 Бронза", 0.0)
"""

if "def get_vip_rank" not in content:
    content = content + "\n" + vip_logic

with open("/Users/macbook/tg-bot/database/db.py", "w") as f:
    f.write(content)
