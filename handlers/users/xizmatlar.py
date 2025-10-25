from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from filters.admin_filter import AdminFilter

#========================================================================================
from database_funk.services import GET_SERVICE
from database_funk.api_funk import LOAD_SERVICES_FROM_JSON
from keyboards.users.inline import PLATFORM_KEYBOARD, CATEGORY_KEYBOARD, SERVICES_KEYBOARD, SERVICE_KEYBOARD
from texts.users import (
    MSG2, MSG3, MSG4, MSG5
)

from utils.error import send_error
from utils.kurs_calculator import CALCULATOR
#========================================================================================

user_router = Router()


# 🗂 Xizmatlar bo‘limi
@user_router.message(F.text == "🗂 Xizmatlar")
async def xizmatlar(message: Message):
    try:
        user_id = message.from_user.id
        kb = await PLATFORM_KEYBOARD(AdminFilter(user_id))
        await message.answer(MSG2, reply_markup=kb)
    except Exception as e:
        await send_error(e)


# 🔹 Kategoriya tanlanganda
@user_router.callback_query(F.data.startswith("a:"))
async def category_callback(callback: CallbackQuery):
    try:
        try:
            await callback.answer()
        except:
            pass

        user_id = callback.from_user.id
        platform = callback.data.split(":")[1]
        kb = await CATEGORY_KEYBOARD(platform, AdminFilter(user_id))
        await callback.message.edit_text(MSG3, reply_markup=kb)
    except Exception as e:
        await send_error(e)


# 🔹 Bo‘lim tanlanganda
@user_router.callback_query(F.data.startswith("b:"))
async def bolim_callback(callback: CallbackQuery, state: FSMContext):
    try:
        try:
            await callback.answer()
        except:
            pass

        user_id = callback.from_user.id
        platform, category = callback.data.split(":")[1:]
        kb = await SERVICES_KEYBOARD(platform, category, AdminFilter(user_id))
        await callback.message.edit_text(MSG4, reply_markup=kb)
    except Exception as e:
        await send_error(e)


#========================================================================================
# 🔹 Xizmat tanlanganda
@user_router.callback_query(F.data.startswith("c:"))
async def service_callback(callback: CallbackQuery, state: FSMContext):
    try:
        try:
            await callback.answer()
        except:
            pass

        user_id = callback.from_user.id
        id = callback.data.split(":")[1]
        service = await GET_SERVICE(int(id))
        if not service:
            await callback.answer("❌ Bunday xizmat topilmadi", show_alert=True)
            return

        service_id = service.get("service_id")
        api_id = service.get("api_id")
        service_api = await LOAD_SERVICES_FROM_JSON(api_id, int(service_id))
        if not service_api or service_api.get("service") != service_id:
            await callback.answer("❌ Bunday xizmat topilmadi", show_alert=True)
            return

        name = service.get("name", "-")
        description = service.get("description", "-")

        min_val = service.get("min")
        max_val = service.get("max")
        rate_val = service.get("price")
        price = rate_val

        if min_val is None or max_val is None:
            min_val = service_api.get("min")
            max_val = service_api.get("max")

        if rate_val is None:
            rate_val = float(service_api.get("rate"))
            price = CALCULATOR(api_id, rate_val, 1000)

        try:
            min_val = int(min_val)
        except (TypeError, ValueError):
            min_val = None

        try:
            max_val = int(max_val)
        except (TypeError, ValueError):
            max_val = None

        try:
            rate_val = float(rate_val)
        except (TypeError, ValueError):
            rate_val = 0.0

        text = MSG5.format(
            service_id=id,
            service_name=name,
            description=description,
            min=min_val,
            max=max_val,
            price=round(price, 2)
        )
        kb = await SERVICE_KEYBOARD(service.get("platform_id"), service.get("category_id"), id, AdminFilter(user_id))
        await callback.message.edit_text(text, reply_markup=kb)
    except Exception as e:
        await send_error(e)
# 🔙 Orqaga
@user_router.callback_query(F.data.startswith("back:"))
async def back_callback(callback: CallbackQuery, state: FSMContext):
    try:
        id = callback.from_user.id
        try:
            await callback.answer()
        except:
            pass

        user_id = callback.from_user.id
        data = callback.data.split(":")
        if data[1] == "menu":
            kb = await PLATFORM_KEYBOARD(AdminFilter(id))
            await callback.message.edit_text(MSG2, reply_markup=kb)
            await state.clear()
        elif len(data) == 2:
            kb = await CATEGORY_KEYBOARD(data[1], AdminFilter(user_id))
            await callback.message.edit_text(MSG3, reply_markup=kb)
            await state.clear()
        elif len(data) == 3:
            kb = await SERVICES_KEYBOARD(data[1], data[2], AdminFilter(user_id))
            await callback.message.edit_text(MSG4, reply_markup=kb)
            await state.clear()
    except Exception as e:
        await send_error(e)