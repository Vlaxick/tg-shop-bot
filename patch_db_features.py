import re

with open("/Users/macbook/tg-bot/database/db.py", "r") as f:
    content = f.read()

# 1. Init tables updates
old_init = """        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                referrer_id INTEGER,
                balance REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')"""

new_init = """        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                referrer_id INTEGER,
                balance REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                referral_earnings REAL DEFAULT 0,
                last_bonus_claim TIMESTAMP
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS promocodes (
                code TEXT PRIMARY KEY,
                amount REAL,
                uses_left INTEGER
            )
        ''')
        
        # Add columns to existing users table if they don't exist
        try:
            await db.execute('ALTER TABLE users ADD COLUMN referral_earnings REAL DEFAULT 0')
        except:
            pass
        try:
            await db.execute('ALTER TABLE users ADD COLUMN last_bonus_claim TIMESTAMP')
        except:
            pass
"""

content = content.replace(old_init, new_init)

# 2. Add functions for bonus and promocodes
funcs = """
async def claim_daily_bonus(user_id: int) -> float:
    import random
    from datetime import datetime, timedelta
    
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT last_bonus_claim FROM users WHERE user_id = ?', (user_id,)) as cursor:
            res = await cursor.fetchone()
            
        now = datetime.now()
        if res and res[0]:
            last_claim = datetime.fromisoformat(res[0])
            if now - last_claim < timedelta(hours=24):
                return 0.0 # Not ready yet
                
        bonus_amount = round(random.uniform(1.0, 5.0), 2)
        await db.execute('UPDATE users SET balance = balance + ?, last_bonus_claim = ? WHERE user_id = ?', (bonus_amount, now.isoformat(), user_id))
        await db.commit()
        return bonus_amount

async def get_next_bonus_time(user_id: int) -> str:
    from datetime import datetime, timedelta
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT last_bonus_claim FROM users WHERE user_id = ?', (user_id,)) as cursor:
            res = await cursor.fetchone()
            
        if not res or not res[0]:
            return "ready"
            
        last_claim = datetime.fromisoformat(res[0])
        now = datetime.now()
        diff = now - last_claim
        if diff >= timedelta(hours=24):
            return "ready"
            
        remaining = timedelta(hours=24) - diff
        hours, remainder = divmod(remaining.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{hours} год {minutes} хв"

async def create_promocode(code: str, amount: float, uses: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('INSERT OR REPLACE INTO promocodes (code, amount, uses_left) VALUES (?, ?, ?)', (code, amount, uses))
        await db.commit()

async def activate_promocode(user_id: int, code: str) -> float:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT amount, uses_left FROM promocodes WHERE code = ? COLLATE NOCASE', (code,)) as cursor:
            res = await cursor.fetchone()
            
        if not res or res[1] <= 0:
            return 0.0
            
        amount = res[0]
        uses_left = res[1] - 1
        
        await db.execute('UPDATE promocodes SET uses_left = ? WHERE code = ? COLLATE NOCASE', (uses_left, code))
        await db.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
        await db.commit()
        return amount
"""

content = content + "\n" + funcs

with open("/Users/macbook/tg-bot/database/db.py", "w") as f:
    f.write(content)
