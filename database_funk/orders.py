import aiosqlite
from config import ORDERS_DB
from loader import bot
from texts.users import MSG10, MSG11
from database_funk.api_funk import GET_STATUS
from utils.error import send_error
from utils.time import TASHKENT_TIME
from database_funk.users import ADD_BALL

# ===========================================
# 🧱 Jadval yaratish
# ===========================================
async def CREATE_ORDERS_TABLE():
    try:
        async with aiosqlite.connect(ORDERS_DB) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_id INTEGER NOT NULL,
                    order_id INTEGER NOT NULL,
                    api_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    service_api_id INTEGER NOT NULL,
                    name TEXT,
                    quantity INTEGER NOT NULL,
                    link TEXT NOT NULL,
                    price REAL NOT NULL,
                    status TEXT DEFAULT 'Pending',
                    created_at TEXT
                )
            """)
            
            # Index'lar qo'shish - tezlikni oshiradi
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_orders 
                ON orders(user_id)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_order_status 
                ON orders(status)
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_order_api 
                ON orders(order_id, api_id)
            """)
            
            await db.commit()
    except Exception as e:
        await send_error(e)

# ===========================================
# ➕ Buyurtma qo‘shish
# ===========================================
async def ADD_ORDER(SERVICE_ID, ORDER_ID, API_ID, USER_ID, SERVICE_API_ID, NAME, QTY, LINK, PRICE):
    try:
        async with aiosqlite.connect(ORDERS_DB) as db:
            await db.execute("""
                INSERT INTO orders (service_id, order_id, api_id, user_id, service_api_id, name, quantity, link, price, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (SERVICE_ID, ORDER_ID, API_ID, USER_ID, SERVICE_API_ID, NAME, QTY, LINK, PRICE, TASHKENT_TIME()))
            await db.commit()
            return True
    except Exception as e:
        await send_error(e)
        return False

# ===========================================
# 🔍 Bitta buyurtmani olish
# ===========================================
async def GET_ORDER(ID):
    try:
        async with aiosqlite.connect(ORDERS_DB) as db:
            async with db.execute("SELECT * FROM orders WHERE id = ?", (ID,)) as cursor:
                order = await cursor.fetchone()
                if order:
                    return {
                        "id": order[0],
                        "service_id": order[1],
                        "order_id": order[2],
                        "api_id": order[3],
                        "user_id": order[4],
                        "service_api_id": order[5],
                        "name": order[6],
                        "quantity": order[7],
                        "link": order[8],
                        "price": order[9],
                        "status": order[10],
                        "created_at": order[11]
                    }
    except Exception as e:
        await send_error(e)
# ===============================================
# 📦 order_id va api id orqali idni olish
# ===============================================
async def GET_ORDER_ID(ORDER_ID, API_ID):
    try:
        async with aiosqlite.connect(ORDERS_DB) as db:
            async with db.execute("SELECT id FROM orders WHERE order_id = ? AND api_id = ?", (ORDER_ID, API_ID)) as cursor:
                order = await cursor.fetchone()
                if order:
                    return order[0]
                else:
                    return None
    except Exception as e:
        await send_error(e)
# ===========================================
# 📦 Foydalanuvchining barcha buyurtmalari
# ===========================================

async def GET_USER_ORDERS(USER_ID, SUM_PRICE=False):
    try:
        async with aiosqlite.connect(ORDERS_DB) as db:
            async with db.execute("SELECT * FROM orders WHERE user_id = ?", (USER_ID,)) as cursor:
                orders = await cursor.fetchall()

                if not orders:
                    return [] if not SUM_PRICE else 0

                if SUM_PRICE:
                    total = sum(
                        order[9] for order in orders
                        if order[10] in ("Completed", "Partial")
                    )
                    return total

                # Aks holda barcha buyurtmalarni qaytarish
                return [{
                    "id": order[0],
                    "service_id": order[1],
                    "order_id": order[2],
                    "api_id": order[3],
                    "user_id": order[4],
                    "service_api_id": order[5],
                    "name": order[6],
                    "quantity": order[7],
                    "link": order[8],
                    "price": order[9],
                    "status": order[10],
                    "created_at": order[11]
                } for order in orders]

    except Exception as e:
        await send_error(e)
        return [] if not SUM_PRICE else 0
# ===========================================
# ♻️ Buyurtma holatini yangilash
# ===========================================
async def UPDATE_ORDER_STATUS(ID, STATUS):
    try:
        async with aiosqlite.connect(ORDERS_DB) as db:
            await db.execute("UPDATE orders SET status = ? WHERE id = ?", (STATUS, ID))
            await db.commit()
            return True
    except Exception as e:
        await send_error(e)
        return False

# ===========================================
# 🧩 Faol buyurtmalarni olish
# ===========================================
async def FILTER_ACTIVE_ORDERS():
    try:
        async with aiosqlite.connect(ORDERS_DB) as db:
            async with db.execute("SELECT * FROM orders WHERE status NOT IN ('Completed', 'Canceled', 'Partial')") as cursor:
                orders = await cursor.fetchall()
                return [order[0] for order in orders] if orders else []
    except Exception as e:
        await send_error(e)
        return []

# ===========================================
# 🔄 Buyurtma holatini yangilash
# ===========================================
async def UPDATE_ORDERS_STATUS():
    try:
        ACTIVE_ORDERS = await FILTER_ACTIVE_ORDERS()
        if not ACTIVE_ORDERS:
            return

        for ID in ACTIVE_ORDERS:
            ORDER = await GET_ORDER(ID)
            if not ORDER:
                continue

            # API'dan holatni olish
            STATUS = await GET_STATUS(ORDER.get("api_id"), str(ORDER.get("order_id")))
            if not STATUS or "status" not in STATUS:
                continue

            await UPDATE_ORDER_STATUS(ID, STATUS["status"])

            # ⚠️ Kalitlar xavfsiz tekshiruv
            user_id = ORDER.get("user_id")
            link = ORDER.get("link")
            quantity = ORDER.get("quantity")
            price = ORDER.get("price")

            if not user_id or ID is None:
                print(f"⚠️ order_id yoki user_id topilmadi! ORDER: {ORDER}")
                continue

            if STATUS["status"] == "Canceled":
                await bot.send_message(
                    user_id,
                    MSG11.format(order_id=ID, link=link, quantity=quantity, paid_amount=price), disable_web_page_preview=True
                )
                await ADD_BALL(user_id, price)

            elif STATUS["status"] == "Completed":
                await bot.send_message(
                    user_id,
                    MSG10.format(order_id=ID, link=link, quantity=quantity), disable_web_page_preview=True
                )

    except Exception as e:
        await send_error(e)
