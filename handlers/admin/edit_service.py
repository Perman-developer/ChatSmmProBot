from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from keyboards.admin.reply import BACK_KEYBOARD
from keyboards.admin.inline import UPDATE_SERVICE_KEYBOARD
from keyboards.users.reply import MENU
from database_funk.services import (
    UPDATE_SERVICES, DELETE_SERVICE, GET_SERVICE,
    UPDATE_PLATFORM, DELETE_PLATFORM,
    UPDATE_CATEGORY, DELETE_CATEGORY
)
from filters.admin_filter import AdminFilter
from utils.error import send_error
from texts.admin import MSG1

admin_router = Router()

# ======================== SERVICE HANDLERS ========================
class EditServiceState(StatesGroup):
    name = State()
    price = State()
    min = State()
    max = State()
    description = State()

async def text(id: int):
    service = await GET_SERVICE(id)
    return MSG1.format(
        name=service["name"],
        price=service["price"],
        min=service["min"],
        max=service["max"],
        api_id=service["api_id"],
        description=service["description"],
        id=service["id"]
    )

@admin_router.callback_query(F.data.startswith("edit_service:"))
async def edit_service(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
        id = int(callback.data.split(":")[1])
        kb = await UPDATE_SERVICE_KEYBOARD(id)
        msg = await text(id)
        await callback.message.answer(msg, reply_markup=kb)
        await callback.answer()
    except Exception as e:
        await send_error(e)

@admin_router.callback_query(F.data.startswith("edit:"))
async def edit_service1(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
        id = int(callback.data.split(":")[2])
        kb = await BACK_KEYBOARD()
        key = callback.data.split(":")[1]
        if key == "name":
            await callback.message.answer("Yangi nomni kiriting:", reply_markup=kb)
            await state.set_state(EditServiceState.name)
        elif key == "price":
            await callback.message.answer("Yangi narxni kiriting:", reply_markup=kb)
            await state.set_state(EditServiceState.price)
        elif key == "min":
            await callback.message.answer("Yangi minimalni kiriting:", reply_markup=kb)
            await state.set_state(EditServiceState.min)
        elif key == "max":
            await callback.message.answer("Yangi maksimalni kiriting:", reply_markup=kb)
            await state.set_state(EditServiceState.max)
        elif key == "description":
            await callback.message.answer("Yangi tavsifni kiriting:", reply_markup=kb)
            await state.set_state(EditServiceState.description)
        await callback.answer()
        await state.update_data(id=id)
    except Exception as e:
        await send_error(e)

@admin_router.message(EditServiceState.name)
async def edit_service2(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        id = data["id"]
        await UPDATE_SERVICES(id, name=message.text)
        await message.answer("✅ Nom muvaffaqiyatli o'zgartirildi!")
        kb = await UPDATE_SERVICE_KEYBOARD(id)
        msg = await text(id)
        await message.answer(msg, reply_markup=kb)
        await state.clear()
    except Exception as e:
        await send_error(e)

@admin_router.message(EditServiceState.price)
async def edit_service3(message: Message, state: FSMContext):
    try:
        try:
            price = float(message.text.strip())
        except ValueError:
            await message.answer("❌ Narxni to'g'ri kiriting!")
            return
        data = await state.get_data()
        id = data["id"]
        if price == 0: price = None
        await UPDATE_SERVICES(id, price=price)
        await message.answer("✅ Narx muvaffaqiyatli o'zgartirildi!")
        kb = await UPDATE_SERVICE_KEYBOARD(id)
        msg = await text(id)
        await message.answer(msg, reply_markup=kb)
        await state.clear()
    except Exception as e:
        await send_error(e)

@admin_router.message(EditServiceState.min)
async def edit_service4(message: Message, state: FSMContext):
    try:
        try:
            min_val = int(message.text.strip())
        except ValueError:
            await message.answer("❌ Minimalni to'g'ri kiriting!")
            return
        data = await state.get_data()
        id = data["id"]
        if min_val == 0: min_val = None
        await UPDATE_SERVICES(id, min=min_val)
        await message.answer("✅ Minimal muvaffaqiyatli o'zgartirildi!")
        kb = await UPDATE_SERVICE_KEYBOARD(id)
        msg = await text(id)
        await message.answer(msg, reply_markup=kb)
        await state.clear()
    except Exception as e:
        await send_error(e)

@admin_router.message(EditServiceState.max)
async def edit_service5(message: Message, state: FSMContext):
    try:
        try:
            max_val = int(message.text.strip())
        except ValueError:
            await message.answer("❌ Maksimalni to'g'ri kiriting!")
            return
        data = await state.get_data()
        id = data["id"]
        if max_val == 0: max_val = None
        await UPDATE_SERVICES(id, max=max_val)
        await message.answer("✅ Maksimal muvaffaqiyatli o'zgartirildi!")
        kb = await UPDATE_SERVICE_KEYBOARD(id)
        msg = await text(id)
        await message.answer(msg, reply_markup=kb)
        await state.clear()
    except Exception as e:
        await send_error(e)

@admin_router.message(EditServiceState.description)
async def edit_service6(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        id = data["id"]
        await UPDATE_SERVICES(id, description=message.text)
        await message.answer("✅ Tavsif muvaffaqiyatli o'zgartirildi!")
        kb = await UPDATE_SERVICE_KEYBOARD(id)
        msg = await text(id)
        await message.answer(msg, reply_markup=kb)
        await state.clear()
    except Exception as e:
        await send_error(e)

@admin_router.callback_query(F.data.startswith("delete_service:"))
async def delete_service(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
        id = int(callback.data.split(":")[1])
        await DELETE_SERVICE(id)
        await callback.message.answer("✅ Xizmat muvaffaqiyatli o'chirildi!")
        await callback.answer()
    except Exception as e:
        await send_error(e)

# ======================== PLATFORM HANDLERS ========================
class EditPlatformState(StatesGroup):
    name = State()

@admin_router.callback_query(F.data.startswith("edit_platform:"))
async def edit_platform(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
        await callback.message.delete()
        platform_id = int(callback.data.split(":")[1])
        await state.update_data(platform_id=platform_id)
        kb = await BACK_KEYBOARD()
        await callback.message.answer("Yangi platforma nomini kiriting:", reply_markup=kb)
        await state.set_state(EditPlatformState.name)
    except Exception as e:
        await send_error(e)

@admin_router.message(EditPlatformState.name)
async def edit_platform_name(message: Message, state: FSMContext):
    try:
        id = message.from_user.id
        name = message.text.strip()
        data = await state.get_data()
        platform_id = data["platform_id"]
        await UPDATE_PLATFORM(platform_id, name)
        kb = await MENU(AdminFilter(id))
        await message.answer(f"✅ {name} - muvaffaqiyatli yangilandi!", reply_markup=kb)
        await state.clear()
    except Exception as e:
        await send_error(e)

@admin_router.callback_query(F.data.startswith("delete_platform:"))
async def delete_platform(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.answer()
        id = callback.from_user.id
        await callback.message.delete()
        platform_id = int(callback.data.split(":")[1])
        await DELETE_PLATFORM(platform_id)
        kb = await MENU(AdminFilter(id))
        await callback.message.answer("✅ Platforma muvaffaqiyatli o'chirildi!", reply_markup=kb)
        await state.clear()
    except Exception as e:
        await send_error(e)

# ======================== CATEGORY HANDLERS ========================
class EditCategoryState(StatesGroup):
    name = State()

@admin_router.callback_query(F.data.startswith("edit_category:"))
async def edit_category(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
        category_id = int(callback.data.split(":")[1])
        await state.update_data(category_id=category_id)
        kb = await BACK_KEYBOARD()
        await callback.message.answer("Yangi kategoriya nomini kiriting:", reply_markup=kb)
        await state.set_state(EditCategoryState.name)
        await callback.answer()
    except Exception as e:
        await send_error(e)

@admin_router.message(EditCategoryState.name)
async def edit_category_name(message: Message, state: FSMContext):
    try:
        id = message.from_user.id
        name = message.text.strip()
        data = await state.get_data()
        category_id = data["category_id"]
        await UPDATE_CATEGORY(category_id, name)
        kb = await MENU(id)
        await message.answer(f"Kategoriya nomini o'zgartirildi: {name}", reply_markup=kb)
        await state.clear()
    except Exception as e:
        await send_error(e)

@admin_router.callback_query(F.data.startswith("delete_category:"))
async def delete_category(callback: CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
        await callback.answer()
        id = callback.from_user.id
        category_id = int(callback.data.split(":")[1])
        await DELETE_CATEGORY(category_id)
        kb = await MENU(id)
        await callback.message.answer("Kategoriya o'chirildi", reply_markup=kb)
        await state.clear()
    except Exception as e:
        await send_error(e)