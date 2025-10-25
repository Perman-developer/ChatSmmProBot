import aiosqlite
from config import SERVICES_DB
# TAYYOR
# ========================================================================================
# Ma'lumotlar bazasini yaratish
# Bu funksiya platforms, categories va services jadvallarini yaratadi.
# Har bir jadvalda kerakli maydonlar va FOREIGN KEY munosabatlari aniqlanadi.
async def CREATE_SERVICES_TABLE():
    async with aiosqlite.connect(SERVICES_DB) as db:
        # Platformlar jadvali: platformalarni saqlash uchun (masalan, Instagram, YouTube)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS platforms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)

        # Kategoriyalar jadvali: platformaga bog'liq kategoriyalarni saqlash uchun
        await db.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                platform_id INTEGER
            )
        """)

        # Xizmatlar jadvali: xizmatlar haqida ma'lumotlarni saqlash uchun
        await db.execute("""
            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_id INTEGER NOT NULL,
                api_id INTEGER,
                platform_id INTEGER,
                category_id INTEGER,
                name TEXT NOT NULL,
                price REAL,
                min INTEGER,
                max INTEGER,
                description TEXT
            )
        """)
        await db.commit()

# ========================================================================================
# Platforma qo'shish
# Yangi platforma nomini platforms jadvaliga qo'shadi.
async def ADD_PLATFORM(name: str):
    async with aiosqlite.connect(SERVICES_DB) as db:
        await db.execute("INSERT OR IGNORE INTO platforms (name) VALUES (?)", (name,))
        await db.commit()

# ========================================================================================
# Kategoriya qo'shish
# Yangi kategoriya nomini categories jadvaliga qo'shadi.
async def ADD_CATEGORY(name: str, platform_id: int):
    async with aiosqlite.connect(SERVICES_DB) as db:
        await db.execute("INSERT OR IGNORE INTO categories (name, platform_id) VALUES (?, ?)", (name, platform_id))
        await db.commit()

# ========================================================================================
# Xizmat qo'shish
# Xizmat ma'lumotlarini (service_id, api_id, platform_id, category_id, nom, narx va boshqalar) services jadvaliga qo'shadi.
async def ADD_SERVICE(service_id: int, api_id: int, platform_id, category_id, name: str, price: float = None, min: int = None, max: int = None, description: str = None):
    async with aiosqlite.connect(SERVICES_DB) as db:
        await db.execute(
            """
            INSERT INTO services (service_id, api_id, platform_id, category_id, name, price, min, max, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (service_id, api_id, platform_id, category_id, name, price, min, max, description)
        )
        await db.commit()

# ========================================================================================
# Barcha platformalarni olish
# platforms jadvalidan barcha platformalarni ro'yxat sifatida qaytaradi.
async def GET_PLATFORMS():
    async with aiosqlite.connect(SERVICES_DB) as db:
        async with db.execute("SELECT * FROM platforms") as cursor:
            platforms = await cursor.fetchall()
            return [{"id": row[0], "name": row[1]} for row in platforms]

# ========================================================================================
# Kategoriyalarni platforma ID orqali olish
# Berilgan platform_id ga mos kategoriyalarni ro'yxat sifatida qaytaradi.
async def GET_CATEGORIES(platform_id: int):
    async with aiosqlite.connect(SERVICES_DB) as db:
        async with db.execute("SELECT * FROM categories WHERE platform_id = ?", (platform_id,)) as cursor:
            categories = await cursor.fetchall()
            return [{"id": row[0], "name": row[1]} for row in categories]

# ========================================================================================
# Xizmatlarni platforma va kategoriya ID orqali olish
# Berilgan platform_id va category_id ga mos xizmatlarni ro'yxat sifatida qaytaradi.
async def GET_SERVICES(platform_id: int, category_id: int):
    async with aiosqlite.connect(SERVICES_DB) as db:
        async with db.execute("SELECT id, service_id, api_id, name, price FROM services WHERE platform_id = ? AND category_id = ?", (platform_id, category_id)) as cursor:
            services = await cursor.fetchall()
            return [{"id": row[0], "service_id": row[1], "api_id": row[2], "name": row[3], "price": row[4]} for row in services]

# ========================================================================================
# Xizmatni ID orqali olish
# Berilgan ID ga mos xizmat ma'lumotlarini lug'at sifatida qaytaradi, agar topilmasa None qaytaradi.
async def GET_SERVICE(id: int):
    async with aiosqlite.connect(SERVICES_DB) as db:
        async with db.execute("SELECT * FROM services WHERE id = ?", (id,)) as cursor:
            service = await cursor.fetchone()
            if service:
                return {
                    "id": service[0],
                    "service_id": service[1],
                    "api_id": service[2],
                    "platform_id": service[3],
                    "category_id": service[4],
                    "name": service[5],
                    "price": service[6],
                    "min": service[7],
                    "max": service[8],
                    "description": service[9]
                }
            else:
                return None

# ========================================================================================
# Xizmatni ID orqali o'chirish
# Berilgan ID ga mos xizmatni services jadvalidan o'chiradi va True qaytaradi.
async def DELETE_SERVICE(id: int):
    async with aiosqlite.connect(SERVICES_DB) as db:
        await db.execute("DELETE FROM services WHERE id = ?", (id,))
        await db.commit()
        return True
#==========================================================================================
# Platformni ID orqali o'chirish
# Berilgan ID ga mos platformni platforms jadvalidan o'chiradi va True qaytaradi.
async def DELETE_PLATFORM(id: int):
    async with aiosqlite.connect(SERVICES_DB) as db:
        await db.execute("DELETE FROM platforms WHERE id = ?", (id,))
        await db.execute("DELETE FROM categories WHERE platform_id = ?", (id,))
        await db.execute("DELETE FROM services WHERE platform_id = ?", (id,))
        await db.commit()

#==========================================================================================
# Kategoriyani ID orqali o'chirish
# Berilgan ID ga mos kategoriyani categories jadvalidan o'chiradi va True qaytaradi.
async def DELETE_CATEGORY(id: int):
    async with aiosqlite.connect(SERVICES_DB) as db:
        await db.execute("DELETE FROM categories WHERE id = ?", (id,))
        await db.execute("DELETE FROM services WHERE category_id = ?", (id,))
        await db.commit()
# ========================================================================================
# Xizmatni yangilash
# Berilgan ID ga mos xizmatning ma'lumotlarini yangilaydi. Faqat kwargs orqali berilgan maydonlar o'zgartiriladi.
async def UPDATE_SERVICES(id: int, **kwargs):
    async with aiosqlite.connect(SERVICES_DB) as db:
        query = "UPDATE services SET "
        values = []
        for key, value in kwargs.items():
            query += f"{key} = ?, "
            values.append(value)
        query = query.rstrip(", ")
        query += " WHERE id = ?"
        values.append(id)
        await db.execute(query, values)
        await db.commit()


# ========================================================================================
# Platform update 
# Berilgan id orqali name ni  yangilaydi
async def UPDATE_PLATFORM(id: int, name: str):
     async with aiosqlite.connect(SERVICES_DB) as db:
          await db.execute("UPDATE platforms SET name = ? WHERE id = ?", (name, id))
          await db.commit()
          return True


# ========================================================================================
# Category update
# Berilgan id orqali name ni  yangilaydi
async def UPDATE_CATEGORY(id: int, name: str):
     async with aiosqlite.connect(SERVICES_DB) as db:
          await db.execute("UPDATE categories SET name = ? WHERE id = ?", (name, id))
          await db.commit()

# ========================================================================================