from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton

async def BACK_KEYBOARD():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="⬅️ Orqaga"))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


async def ADMIN_KEYBOARD():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="⚙️ Asosiy sozlamalar"))
    builder.add(KeyboardButton(text="📊 Statistika"))
    builder.add(KeyboardButton(text="📨 Xabar yuborish"))
    builder.add(KeyboardButton(text="🔐 Majbur obuna kanallar"))
    builder.add(KeyboardButton(text="💳 To'lov tizimlar"))
    builder.add(KeyboardButton(text="🔑 API"))
    builder.add(KeyboardButton(text="🧑‍💻 Foydalanuvchini boshqarish"))
    builder.add(KeyboardButton(text="📈 Xizmatlar"))
    builder.add(KeyboardButton(text="📊 Buyurtmalar"))
    builder.add(KeyboardButton(text="⬅️ Orqaga"))
    builder.adjust(1, 2, 1, 2, 1, 2)
    return builder.as_markup(resize_keyboard=True)