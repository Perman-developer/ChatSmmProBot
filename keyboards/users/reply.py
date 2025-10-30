from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton


async def MENU(ADMIN=False):
    builder = ReplyKeyboardBuilder()
    
    builder.add(KeyboardButton(text="🗂 Xizmatlar"))
    builder.add(KeyboardButton(text="👤Mening hisobim"))
    builder.add(KeyboardButton(text="🔍 Buyurtmalarim"))
    builder.add(KeyboardButton(text="💰Hisob toʻldirish"))
    builder.add(KeyboardButton(text="💸 Pul ishlash"))
    builder.add(KeyboardButton(text="🤖 Bot yaratish"))
    builder.add(KeyboardButton(text="☎️ Qo'llab-quvvatlash"))
    if ADMIN:
        builder.add(KeyboardButton(text="🗄️ Boshqaruv"))
    builder.adjust(1, 2)  # 1 qator va 2 ta tugma
    
    return builder.as_markup(resize_keyboard=True)
  # Har bir qatorda 2 ta tugma



back_builder = ReplyKeyboardBuilder()
back_builder.add(KeyboardButton(text="⬅️ Orqaga"))
back_builder.adjust(1)
back = back_builder.as_markup(resize_keyboard=True)
