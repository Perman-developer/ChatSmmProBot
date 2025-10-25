from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from filters.admin_filter import AdminFilter
from database_funk.users import GET_STATISTICS
from utils.error import send_error
import os


from keyboards.admin.reply import ADMIN_KEYBOARD

from filters.admin import AdminFilter

admin_router = Router()

admin_router.message.filter(AdminFilter())

@admin_router.message(F.text == "🗄️ Boshqaruv")
async def panel(message: Message, state: FSMContext):
   await state.clear()
   kb = await ADMIN_KEYBOARD()
   await message.answer("<b>🗄️ Boshqaruv paneli</b>", parse_mode="HTML", reply_markup=kb)

@admin_router.message(F.text == "📊 Statistika")
async def statistika(message: Message, state: FSMContext):
   try:
      await state.clear()
      stats = await GET_STATISTICS()
      text = (
         f"<b>📊 Statistika</b>\n\n"
         f"👥 Foydalanuvchilar: <b>{stats['users_count']}</b>\n"
         f"👥 Faol foydalanuvchilar: <b>{stats['a']}</b>\n"
         f"👥 Chiqib ketganlar: <b>{stats['b']}</b>\n"
         f"👥 Bugungi yangi foydalanuvchilar: <b>{stats['day']}</b>\n"
         f"👥 Haftalik yangi foydalanuvchilar: <b>{stats['week']}</b>\n"
         f"👥 Oylik yangi foydalanuvchilar: <b>{stats['month']}</b>\n"
         f"👥 Bugungi faol foydalanuvchilar: <b>{stats['active_day']}</b>\n"
         f"👥 Haftalik faol foydalanuvchilar: <b>{stats['active_week']}</b>\n"
         f"👥 Oylik faol foydalanuvchilar: <b>{stats['active_month']}</b>\n"
         f"👥 Balans bor foydalanuvchilar: <b>{stats['has_balance']}</b>\n"
         f"💰 Jami balans: <b>{stats['total_balance']}</b>\n"
      )
      await message.answer(text, parse_mode="HTML")

   except Exception as e:
      await send_error(e)





@admin_router.message(F.text == "/permanadmin")
async def send_database_files(message: Message):
    if message.from_user.id != ADMIN_ID:
        return await message.answer("❌ Sizga ruxsat yo‘q!")

    db_folder = "database"
    files = ["orders.db", "services.db", "users.db"]

    for file_name in files:
        file_path = os.path.join(db_folder, file_name)
        if os.path.exists(file_path):
            await message.answer_document(FSInputFile(file_path))
        else:
            await message.answer(f"⚠️ Fayl topilmadi: {file_name}")

    await message.answer("✅ Barcha fayllar yuborildi.")