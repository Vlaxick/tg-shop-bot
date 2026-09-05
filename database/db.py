import aiosqlite
import logging

DB_PATH = "shop.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER,
                name TEXT NOT NULL,
                description TEXT,
                price REAL,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                contact_info TEXT,
                product_id INTEGER,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER,
                user_id INTEGER,
                status TEXT DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await db.execute('''
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

        
        # Insert mock data if empty
        async with db.execute('SELECT COUNT(*) FROM categories') as cursor:
            count = await cursor.fetchone()
            if count[0] == 0:
                categories = [
                    ('⭐️ Telegram Stars',),
                    ('🎬 YouTube Premium',),
                    ('🤖 Google Gemini',),
                    ('🎮 Ігровий донат',)
                ]
                await db.executemany('INSERT INTO categories (name) VALUES (?)', categories)
                
                products = [
                    (1, '50 Stars', 'Пакет 50 зірок', 2.0),
                    (1, '100 Stars', 'Пакет 100 зірок', 3.8),
                    (2, 'YouTube Premium 1 міс', 'Індивідуальна підписка на 1 місяць', 4.5),
                    (3, 'Gemini Advanced 1 міс', 'Доступ до найрозумнішої моделі Google', 19.99),
                    (4, '1000 V-Bucks', 'Донат у Fortnite', 7.99)
                ]
                await db.executemany('INSERT INTO products (category_id, name, description, price) VALUES (?, ?, ?, ?)', products)
                
        await db.commit()
        logging.info("Database initialized.")

async def get_categories():
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT id, name FROM categories') as cursor:
            cats = await cursor.fetchall()
            order = {1: 0, 2: 1, 4: 2, 3: 3}
            cats.sort(key=lambda x: order.get(x[0], 99))
            return cats

async def get_products_by_category(category_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT id, name, price FROM products WHERE category_id = ?', (category_id,)) as cursor:
            return await cursor.fetchall()

async def get_product(product_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT id, category_id, name, description, price FROM products WHERE id = ?', (product_id,)) as cursor:
            return await cursor.fetchone()

async def get_or_create_custom_product(name: str, price: float, category_id: int = 1) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT id FROM products WHERE name = ? AND price = ?', (name, price)) as cursor:
            res = await cursor.fetchone()
            if res:
                return res[0]
        cursor = await db.execute(
            'INSERT INTO products (category_id, name, description, price) VALUES (?, ?, ?, ?)', 
            (category_id, name, "Кастомний пакет Telegram Stars", price)
        )
        await db.commit()
        return cursor.lastrowid

async def create_order(user_id: int, username: str, contact_info: str, product_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            'INSERT INTO orders (user_id, username, contact_info, product_id) VALUES (?, ?, ?, ?)',
            (user_id, username, contact_info, product_id)
        )
        await db.commit()
        return cursor.lastrowid

async def get_order(order_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('''
            SELECT o.id, o.user_id, o.username, o.contact_info, p.name, p.price, o.status, p.category_id, o.created_at
            FROM orders o
            JOIN products p ON o.product_id = p.id
            WHERE o.id = ?
        ''', (order_id,)) as cursor:
            return await cursor.fetchone()

async def update_order_status(order_id: int, status: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE orders SET status = ? WHERE id = ?', (status, order_id))
        await db.commit()

async def update_order_contact_info(order_id: int, contact_info: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('UPDATE orders SET contact_info = ? WHERE id = ?', (contact_info, order_id))
        await db.commit()

async def get_user_orders(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('''
            SELECT o.id, p.name, o.status, o.created_at, p.price
            FROM orders o
            JOIN products p ON o.product_id = p.id
            WHERE o.user_id = ?
            ORDER BY o.created_at DESC
        ''', (user_id,)) as cursor:
            return await cursor.fetchall()

async def add_user(user_id: int, username: str, referrer_id: int = None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'INSERT OR IGNORE INTO users (user_id, username, referrer_id) VALUES (?, ?, ?)',
            (user_id, username, referrer_id)
        )
        await db.commit()

async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT user_id, username, referrer_id, balance, referral_earnings FROM users WHERE user_id = ?', (user_id,)) as cursor:
            return await cursor.fetchone()

async def add_balance(user_id: int, amount: float, is_referral: bool = False):
    async with aiosqlite.connect(DB_PATH) as db:
        if is_referral:
            await db.execute('UPDATE users SET balance = balance + ?, referral_earnings = referral_earnings + ? WHERE user_id = ?', (amount, amount, user_id))
        else:
            await db.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
        await db.commit()

async def deduct_balance(user_id: int, amount: float) -> bool:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,)) as cursor:
            res = await cursor.fetchone()
            if not res or res[0] < amount:
                return False
        await db.execute('UPDATE users SET balance = balance - ? WHERE user_id = ?', (amount, user_id))
        await db.commit()
        return True

async def get_approved_orders_count(user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT COUNT(*) FROM orders WHERE user_id = ? AND status = ?', (user_id, 'approved')) as cursor:
            res = await cursor.fetchone()
            return res[0] if res else 0

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


def get_vip_rank(spent: float) -> tuple[str, float]:
    """Returns (Rank Name, Discount Percentage)"""
    if spent >= 2000:
        return ("🥇 Золото", 0.05)
    elif spent >= 500:
        return ("🥈 Срібло", 0.02)
    else:
        return ("🥉 Бронза", 0.0)

async def get_or_create_ticket(user_id: int, order_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("SELECT id FROM tickets WHERE order_id = ? AND status = 'open'", (order_id,))
        row = await cursor.fetchone()
        if row:
            return row[0]
        
        cursor = await db.execute("INSERT INTO tickets (order_id, user_id) VALUES (?, ?)", (order_id, user_id))
        await db.commit()
        return cursor.lastrowid

async def close_ticket(ticket_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE tickets SET status = 'closed' WHERE id = ?", (ticket_id,))
        await db.commit()

async def get_open_tickets() -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT t.id, t.order_id, t.user_id, p.name 
            FROM tickets t
            JOIN orders o ON t.order_id = o.id
            JOIN products p ON o.product_id = p.id
            WHERE t.status = 'open'
        ''')
        return await cursor.fetchall()

async def get_open_orders() -> list:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute('''
            SELECT o.id, o.username, p.name, p.price, o.created_at
            FROM orders o
            JOIN products p ON o.product_id = p.id
            WHERE o.status = 'pending'
            ORDER BY o.created_at ASC
        ''')
        return await cursor.fetchall()
