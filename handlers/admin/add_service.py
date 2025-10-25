from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from utils.error import send_error
from database_funk.services import ADD_PLATFORM, ADD_CATEGORY, ADD_SERVICE
from database_funk.api_funk import LOAD_SERVICES_FROM_JSON
from keyboards.admin.inline import ADD_PLATFORM_KEYBOARD, ADD_CATEGORY_KEYBOARD, ADD_SERVICE_KEYBOARD, API_ID_KEYBOARD
from keyboards.admin.reply import BACK_KEYBOARD
from config import _config
from filters.admin import AdminFilter

admin_router = Router()

class AddService(StatesGroup):
    add_platform = State()
    add_category = State()
    service_id = State()
    description = State()
    

# ========================================================================================
# 🔹 Platforma qo'shish
# ========================================================================================
@admin_router.callback_query(F.data == "add_platform")
async def add_platform1(callback: CallbackQuery, state: FSMContext):
    try:
        await state.clear()
        await callback.message.delete()
        kb = await BACK_KEYBOARD()
        await callback.message.answer("Platforma nomini kiriting:", reply_markup=kb)
        await state.set_state(AddService.add_platform)
        await callback.answer()
    except Exception as e:
        await send_error(e)

@admin_router.message(AddService.add_platform)
async def add_platform2(message: Message, state: FSMContext):
    try:
        await ADD_PLATFORM(message.text)
        await message.answer("✅ Platforma muvaffaqiyatli qo'shildi!")
        kb = await ADD_PLATFORM_KEYBOARD()
        await message.answer("Yana qoshasizmi:", reply_markup=kb)
        await state.set_state(AddService.add_platform)
    except Exception as e:
        await send_error(e)


# ========================================================================================
# 🔹 Kategoriya qo'shish
# ========================================================================================
@admin_router.callback_query(F.data.startswith("add_category:"))
async def add_category1(callback: CallbackQuery, state: FSMContext):
    try:
        await state.clear()
        await callback.message.delete()

        platform_id = callback.data.split(":")[1]
        await state.update_data(platform_id=platform_id)
        kb = await BACK_KEYBOARD()

        await callback.message.answer("Kategoriya nomini kiriting:", reply_markup=kb)
        await state.set_state(AddService.add_category)
        await callback.answer()
    except Exception as e:
        await send_error(e)

@admin_router.message(AddService.add_category)
async def add_category2(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        platform_id = data["platform_id"]
        await ADD_CATEGORY(message.text, int(platform_id))
        await message.answer("✅ Kategoriya muvaffaqiyatli qo'shildi!")
        kb = await ADD_CATEGORY_KEYBOARD(int(platform_id))
        await message.answer("Yana qoshasizmi:", reply_markup=kb)
        await state.set_state(AddService.add_category)
    except Exception as e:
        await send_error(e)


# ========================================================================================
# 🔹 Xizmat qo'shish
# ========================================================================================
@admin_router.callback_query(F.data.startswith("add_service:"))
async def add_service1(callback: CallbackQuery, state: FSMContext):
    try:
        await state.clear()
        await callback.message.delete()

        data = callback.data.split(":")
        if len(data) < 3:
            await callback.answer("❌ Callback noto‘g‘ri formatda!", show_alert=True)
            return

        _, platform_id, category_id = data
        await state.update_data(platform_id=platform_id, category_id=category_id)

        kb = await API_ID_KEYBOARD()
        text = "📋 Xizmat APIsini tanlang:\n"
        for key, value in _config["api"].items():
            text += f"{key}. - {value['url']}\n"

        await callback.message.answer(text, reply_markup=kb)
        await callback.answer()
    except Exception as e:
        await send_error(e)

@admin_router.callback_query(F.data.startswith("api_id:"))
async def add_service2(callback: CallbackQuery, state: FSMContext):
     try:
          await callback.message.delete()
          api_id = callback.data.split(":")[1]
          await state.update_data(api_id=api_id)
          kb = await BACK_KEYBOARD()
          await callback.message.answer("Xizmat ID sini kiriting:", reply_markup=kb)
          await state.set_state(AddService.service_id)
          await callback.answer()
     except Exception as e:
          await send_error(e)
         
@admin_router.message(AddService.service_id)
async def add_service3(message: Message, state: FSMContext):
    try:
        service_id = message.text.strip()
        data = await state.get_data()
        api_id = data["api_id"]

        services = await LOAD_SERVICES_FROM_JSON(api_id)
        found = None

        for service in services:
            if int(service["service"]) == int(service_id):
                found = service
                break

        if not found:
            await message.answer("❌ Bunday xizmat mavjud emas!")
            return

        # Agar topilgan bo‘lsa:
        name = found["name"]
        await state.update_data(service_id=service_id, name=name)

        kb = await BACK_KEYBOARD()
        await message.answer("✅ Xizmat haqida ma'lumot kiriting:", reply_markup=kb)
        await state.set_state(AddService.description)

    except Exception as e:
        await send_error(e)


@admin_router.message(AddService.description)
async def add_service4(message: Message, state: FSMContext):
     try:
          data = await state.get_data()
          platform_id = int(data["platform_id"])
          category_id = int(data["category_id"])
          api_id = int(data["api_id"])
          service_id = int(data["service_id"])
          name = data["name"]
          description = message.text
          await ADD_SERVICE(service_id, api_id, platform_id, category_id, name, description=description)
          await message.answer("✅ Xizmat muvaffaqiyatli qo'shildi!")
          kb = await ADD_SERVICE_KEYBOARD(platform_id, category_id)
          await message.answer("Yana qoshasizmi:", reply_markup=kb)
          await state.set_state(AddService.service_id)
         
     except Exception as e:
          await send_error(e)

# ========================
# QO‘SHIMCHA (ADD HANDLERS)
# ========================



# ✅ Xizmat qo‘shish
@admin_router.message(AdminFilter(), F.text.startswith("Adds,"))
async def add_service(message: Message):
    try:
        parts = message.text.split(",", 6)  # 7 ta element kerak
        if len(parts) < 7:
            await message.answer(
                "❌ Noto‘g‘ri format!\n\nTo‘g‘ri format:\n"
                "`Adds,service_id,api_id,platform_id,category_id,name,description`"
            )
            return

        service_id = int(parts[1])
        api_id = int(parts[2])
        platform_id = int(parts[3])
        category_id = int(parts[4])
        name = parts[5].strip()
        description = parts[6].strip()

        await ADD_SERVICE(service_id, api_id, platform_id, category_id, name, description=description)
        await message.answer(f"✅ Xizmat '{name}' muvaffaqiyatli qo‘shildi!")

    except ValueError:
        await message.answer("❌ ID qiymatlari raqam bo‘lishi kerak!")
    except Exception as e:
        await send_error(e)


# ✅ Platforma qo‘shish
@admin_router.message(AdminFilter(), F.text.startswith("Addp,"))
async def add_platform(message: Message):
    try:
        parts = message.text.split(",", 1)
        if len(parts) < 2:
            await message.answer("❌ Format noto‘g‘ri!\nTo‘g‘ri format: `Addp,PlatformName`")
            return

        platform_name = parts[1].strip()
        if not platform_name:
            await message.answer("❌ Platforma nomi bo‘sh bo‘lishi mumkin emas!")
            return

        await ADD_PLATFORM(platform_name)
        await message.answer(f"✅ Platforma '{platform_name}' muvaffaqiyatli qo‘shildi!")

    except Exception as e:
        await send_error(e)


# ✅ Kategoriya qo‘shish
@admin_router.message(AdminFilter(), F.text.startswith("Addc,"))
async def add_category(message: Message):
    try:
        parts = message.text.split(",", 2)
        if len(parts) < 3:
            await message.answer(
                "❌ Noto‘g‘ri format!\n\nTo‘g‘ri format:\n"
                "`Addc,CategoryName,PlatformID`"
            )
            return

        category_name = parts[1].strip()
        platform_id = int(parts[2].strip())

        await ADD_CATEGORY(category_name, platform_id)
        await message.answer(f"✅ Kategoriya '{category_name}' muvaffaqiyatli qo‘shildi!")

    except ValueError:
        await message.answer("❌ Platform ID raqam bo‘lishi kerak!")
    except Exception as e:
        await send_error(e)

