from aiogram import Bot
from aiogram.exceptions import TelegramForbiddenError, TelegramBadRequest
import aiosqlite
from config import USERS_DB
from database_funk.users import BAN_USER, UNBAN_USER


# 🔁 Barcha foydalanuvchilarni tekshirish va bloklangan statusini yangilash
async def UPDATE_BLOCK_STATUS_ALL(bot: Bot):
    async with aiosqlite.connect(USERS_DB) as db:
        cursor = await db.execute("SELECT user_id FROM users")
        users = await cursor.fetchall()

        for user in users:
            user_id = user[0]

            try:
                # Bot foydalanuvchiga yozadi (ping)
                await bot.send_chat_action(user_id, "typing")

                # ✅ Agar muammo bo‘lmasa — foydalanuvchi faol
                await UNBAN_USER(user_id)

            except (TelegramForbiddenError, TelegramBadRequest):
                # 🚫 Agar bloklagan bo‘lsa
                await BAN_USER(user_id)

            except Exception:
                # Har ehtimolga qarshi xatolarni yutamiz
                pass