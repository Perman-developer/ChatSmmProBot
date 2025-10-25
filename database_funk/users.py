import aiosqlite
from config import USERS_DB
from utils.time import TASHKENT_TIME
from datetime import datetime, timedelta


# 🧱 USERS jadvalini yaratish
async def CREATE_USERS_TABLE():
    async with aiosqlite.connect(USERS_DB) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                balance REAL DEFAULT 0,
                deposit_balance REAL DEFAULT 0,
                referrals_count INTEGER DEFAULT 0,
                ref_balance REAL DEFAULT 0,

                joined_at TEXT,
                is_active INTEGER DEFAULT 1,
                is_banned INTEGER DEFAULT 0
            )
        """)
        await db.commit()


# 👤 Yangi foydalanuvchi qo‘shish (agar mavjud bo‘lmasa)
async def ADD_USER(user_id):
    async with aiosqlite.connect(USERS_DB) as db:
        cursor = await db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        exists = await cursor.fetchone()

        if not exists:
            await db.execute("""
                INSERT INTO users (user_id, joined_at, is_active)
                VALUES (?, ?, 1)
            """, (user_id, TASHKENT_TIME()))
        else:
            # Mavjud bo‘lsa — uni aktiv holatga qaytaramiz
            await db.execute("""
                UPDATE users SET is_active = 1 WHERE user_id = ?
            """, (user_id,))
        await db.commit()


# 🔍 Foydalanuvchi ma’lumotlarini olish
async def GET_USER(user_id):
    async with aiosqlite.connect(USERS_DB) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = await cursor.fetchone()

        if user:
            return dict(user)


# 💰 Balans qo‘shish
async def ADD_BALL(user_id, amount):
    async with aiosqlite.connect(USERS_DB) as db:
        await db.execute(
            "UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id)
        )
        await db.commit()


# 💰 Balans kamaytirish
async def SUB_BALL(user_id, amount):
    async with aiosqlite.connect(USERS_DB) as db:
        await db.execute(
            "UPDATE users SET balance = balance - ? WHERE user_id = ?", (amount, user_id)
        )
        await db.commit()


# 🤝 Referal balansi va sonini oshirish
async def ADD_REF_BAL(user_id, add_ref_bal=None):
    async with aiosqlite.connect(USERS_DB) as db:
        if add_ref_bal is not None:
            await ADD_BALL(user_id, add_ref_bal)
            await db.execute(
                "UPDATE users SET referrals_count = referrals_count + 1 WHERE user_id = ?",
                (user_id,)
            )
            await db.commit()
            return True


# 🚫 Foydalanuvchini ban qilish
async def BAN_USER(user_id):
    async with aiosqlite.connect(USERS_DB) as db:
        await db.execute(
            "UPDATE users SET is_banned = 1, is_active = 0 WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()


# ✅ Foydalanuvchini unban qilish
async def UNBAN_USER(user_id):
    async with aiosqlite.connect(USERS_DB) as db:
        await db.execute(
            "UPDATE users SET is_banned = 0, is_active = 1 WHERE user_id = ?",
            (user_id,)
        )
        await db.commit()



# 📊 STATISTIKA uchun funksiya
async def GET_STATISTICS():
    try:
        async with aiosqlite.connect(USERS_DB) as db:
            db.row_factory = aiosqlite.Row

            # 🔹 Asosiy sonlar
            cursor = await db.execute("SELECT COUNT(*) AS c FROM users")
            row = await cursor.fetchone()
            users_count = row["c"]
            await cursor.close()

            cursor = await db.execute("SELECT COUNT(*) AS c FROM users WHERE is_active = 1")
            row = await cursor.fetchone()
            active_users = row["c"]
            await cursor.close()

            cursor = await db.execute("SELECT COUNT(*) AS c FROM users WHERE is_banned = 1")
            row = await cursor.fetchone()
            banned_users = row["c"]
            await cursor.close()

            left_users = users_count - active_users - banned_users  # chiqib ketganlar

            # 🔹 Sanalar
            now = datetime.utcnow() + timedelta(hours=5)
            day_ago = (now - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
            week_ago = (now - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
            month_ago = (now - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")

            # 🔹 Oxirgi 24 soat, 7 kun, 30 kunda qo‘shilganlar
            cursor = await db.execute("SELECT COUNT(*) AS c FROM users WHERE joined_at >= ?", (day_ago,))
            row = await cursor.fetchone()
            day_new = row["c"]
            await cursor.close()

            cursor = await db.execute("SELECT COUNT(*) AS c FROM users WHERE joined_at >= ?", (week_ago,))
            row = await cursor.fetchone()
            week_new = row["c"]
            await cursor.close()

            cursor = await db.execute("SELECT COUNT(*) AS c FROM users WHERE joined_at >= ?", (month_ago,))
            row = await cursor.fetchone()
            month_new = row["c"]
            await cursor.close()

            # 🔹 Balans statistikasi
            cursor = await db.execute("SELECT COUNT(*) AS c FROM users WHERE balance > 0")
            row = await cursor.fetchone()
            has_balance = row["c"]
            await cursor.close()

            cursor = await db.execute("SELECT SUM(balance) AS s FROM users")
            row = await cursor.fetchone()
            total_balance = row["s"] or 0
            await cursor.close()

            return {
                "users_count": users_count,
                "a": active_users,
                "b": left_users,
                "day": day_new,
                "week": week_new,
                "month": month_new,
                "active_day": active_users,   # (faollik kuzatish yo‘q, shunchaki aktivlar)
                "active_week": active_users,
                "active_month": active_users,
                "has_balance": has_balance,
                "total_balance": round(total_balance, 2)
            }

    except Exception as e:
        await send_error(e)


