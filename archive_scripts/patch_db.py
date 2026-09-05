
with open("/Users/macbook/tg-bot/database/db.py", "r") as f:
    content = f.read()

# Replace add_balance
old_add_balance = """async def add_balance(user_id: int, amount: float):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
        await db.commit()"""

new_add_balance = """async def add_balance(user_id: int, amount: float, is_referral: bool = False):
    async with aiosqlite.connect(DB_PATH) as db:
        if is_referral:
            await db.execute('UPDATE users SET balance = balance + ?, referral_earnings = referral_earnings + ? WHERE user_id = ?', (amount, amount, user_id))
        else:
            await db.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
        await db.commit()"""

content = content.replace(old_add_balance, new_add_balance)

# Add get_user_stats
new_stats = """
async def get_user_stats(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('''
            SELECT COUNT(o.id), SUM(p.price) 
            FROM orders o 
            JOIN products p ON o.product_id = p.id 
            WHERE o.user_id = ? AND o.status IN ('paid', 'approved')
        ''', (user_id,)) as cursor:
            res = await cursor.fetchone()
            return res[0] or 0, res[1] or 0.0
"""

content += new_stats

with open("/Users/macbook/tg-bot/database/db.py", "w") as f:
    f.write(content)
