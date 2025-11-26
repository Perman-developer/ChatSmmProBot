from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import _config

# ========================================================
# 🔹 XIZMATLAR PLATFORM QOSHIS
# ========================================================
async def ADD_PLATFORM_KEYBOARD():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="➕ Qo'shish", callback_data="add_platform"))
    builder.adjust(1)
    return builder.as_markup()

# ========================================================
# 🔹 XIZMATLAR KATEGORIYA QOSHIS
# ========================================================
async def ADD_CATEGORY_KEYBOARD(platform_id):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="➕ Qo'shish", callback_data=f"add_category:{platform_id}"))
    builder.adjust(1)
    return builder.as_markup()

#=========================================================
# 🔹 XIZMATLAR QOSHISH
# ========================================================
async def ADD_SERVICE_KEYBOARD(platform_id, category_id):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="➕ Qo'shish", callback_data=f"add_service:{platform_id}:{category_id}"))
    builder.adjust(1)
    return builder.as_markup()



# API ID KEYBOARD
async def API_ID_KEYBOARD():
    builder = InlineKeyboardBuilder()
    for key, value in _config["api"].items():
        builder.add(InlineKeyboardButton(text=key, callback_data=f"api_id:{key}"))
    builder.adjust(2)
    return builder.as_markup()
# ========================================================
# 🔹 PAYMENT SOROV
# ========================================================

async def ACCEPT_PAY(user_id, amount):
   builder = InlineKeyboardBuilder()
   builder.add(InlineKeyboardButton(text="✅", callback_data=f"accept:{user_id}:{amount}"))
   builder.add(InlineKeyboardButton(text="❌", callback_data=f"decline:{user_id}:{amount}"))
   builder.adjust(2)
   return builder.as_markup()

# ========================================================
# 🔹 USERGA SOROVIGA JAVOB BERISH
# ========================================================
async def SEND_ANSWER(user_id):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✏️Javob berish", callback_data=f"reply:{user_id}"))
    builder.adjust(1)
    return builder.as_markup()

#=====================///////
# Update service
async def UPDATE_SERVICE_KEYBOARD(id):
     builder = InlineKeyboardBuilder()
     builder.add(InlineKeyboardButton(text="✏️ Narx", callback_data=f"edit:price:{id}"))
     builder.add(InlineKeyboardButton(text="✏️ Min", callback_data=f"edit:min:{id}"))
     builder.add(InlineKeyboardButton(text="✏️ Max", callback_data=f"edit:max:{id}"))
     builder.add(InlineKeyboardButton(text="✏️ Description", callback_data=f"edit:description:{id}"))
     builder.add(InlineKeyboardButton(text="✏️ Name", callback_data=f"edit:name:{id}"))
     builder.add(InlineKeyboardButton(text="⬅️Orqaga", callback_data=f"c:{id}"))
     builder.adjust(2)
     return builder.as_markup()


#