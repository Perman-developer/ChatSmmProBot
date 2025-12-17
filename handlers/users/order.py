from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from keyboards.users.inline import CONFIRM_ORDER
from keyboards.users.reply import back
from database_funk.api_funk import LOAD_SERVICES_FROM_JSON, SEND_ORDER
from database_funk.services import GET_SERVICE
from database_funk.orders import ADD_ORDER, GET_ORDER_ID
from database_funk.users import SUB_BALL, GET_USER
from utils.error import send_error
from utils.kurs_calculator import CALCULATOR
from utils.check_link import CHECK_SOCIAL_LINK
from texts.users import MSG6, MSG7, MSG8, MSG9, MSG30, MSG21
from config import ADMIN_ID
from loader import bot

user_router = Router()

class OrderState(StatesGroup):
    quantity = State()
    link = State()
    confirm = State()



@user_router.callback_query(F.data.startswith("service:"))
async def service_handler(callback: CallbackQuery, state: FSMContext):
    try:
        await state.clear()
        try:
            await callback.message.delete()
        except:
            pass  # Xabarni o‘chira olmasa ham davom etamiz

        id = int(callback.data.split(":")[1])
        service = await GET_SERVICE(id)
        if not service:
            return await callback.answer("Xizmat topilmadi", show_alert=True)

        min_amount = service.get("min")
        max_amount = service.get("max")
        if min_amount is None or max_amount is None:
            api_data = await LOAD_SERVICES_FROM_JSON(service["api_id"], service["service_id"])
            if api_data:
                min_amount = api_data.get("min", 0)
                max_amount = api_data.get("max", 0)

        await state.update_data(min=min_amount, max=max_amount, id=id)
        await callback.message.answer(
            MSG6.format(min=min_amount, max=max_amount),
            reply_markup=back
        )
        await state.set_state(OrderState.quantity)
        await callback.answer()

    except Exception as e:
        await send_error(e)


@user_router.message(OrderState.quantity)
async def quantity_handler(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        quantity = message.text.strip()

        if not quantity.isdigit():
            return await message.answer(MSG21.format(min=data["min"], max=data["max"]))

        quantity = int(quantity)
        if quantity < data["min"] or quantity > data["max"]:
            return await message.answer(MSG21.format(min=data["min"], max=data["max"]))

        await state.update_data(quantity=quantity)
        await message.answer(MSG7)
        await state.set_state(OrderState.link)
    except Exception as e:
        await send_error(e)


@user_router.message(OrderState.link)
async def link_handler(message: Message, state: FSMContext):
    try:
        link = message.text.strip()
        valid = CHECK_SOCIAL_LINK(link)
        if not valid:
            return await message.answer(MSG30, parse_mode="HTML")

        await state.update_data(link=link)
        data = await state.get_data()
        id = data["id"]
        quantity = data["quantity"]
        service = await GET_SERVICE(id)
        if not service:
            return await message.answer("Xizmat topilmadi", parse_mode="HTML")
        name = service["name"]


        rate = service.get("price")
        price = rate
        if rate is None:
            api_data = await LOAD_SERVICES_FROM_JSON(service["api_id"], service["service_id"])

            rate = api_data.get("rate")
            price = CALCULATOR(service["api_id"], float(rate), quantity)
            if rate is None:
                return await message.answer("Xizmat topilmadi", parse_mode="HTML")
        kb = await CONFIRM_ORDER()
        await state.update_data(price=price)
        await message.answer(
            MSG8.format(
                id=id,
                name=name,
                quantity=quantity,
                link=link,
                price=price
            ),
            reply_markup=kb,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        await state.set_state(OrderState.confirm)
    except Exception as e:
        await send_error(e)


@user_router.callback_query(OrderState.confirm, F.data.startswith("confirm_order"))
async def confirm_handler(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        service_id = data["id"]
        service = await GET_SERVICE(service_id)

        if not service:
            await state.clear()
            return await callback.answer("❌ Xizmat topilmadi", show_alert=True)

        quantity = data["quantity"]
        link = data["link"]
        api_id = service["api_id"]
        service_api_id = service["service_id"]
        name = service["name"]
        price = data["price"]
        user_id = callback.from_user.id
        user = await GET_USER(user_id)
        balance = user["balance"]

        if balance < price:
            await state.clear()
            return await callback.message.edit_text("❌ Hisobingizda yetarli mablag' mavjud emas")

        order = await SEND_ORDER(api_id, service_api_id, link, quantity)
        if order.get("order"):
            order_id = order["order"]

            await ADD_ORDER(
                SERVICE_ID=service_id,
                ORDER_ID=order_id,
                API_ID=api_id,
                USER_ID=user_id,
                SERVICE_API_ID=service_api_id,
                NAME=name,
                QTY=quantity,
                LINK=link,
                PRICE=price
            )
            id = await GET_ORDER_ID(order_id, api_id)
            await callback.message.edit_text(MSG9.format(order_id=id))
            await SUB_BALL(user_id, price)
            await state.clear()
        else:
            await callback.answer("❌ Buyurtma berishda xatolik yuz berdi", show_alert=True)

            if "error" in order:
                if order['error'] == "You have active order with this link. Please wait until order being completed.":
                    await callback.message.edit_text(
                        "⚠️ Ushbu havola bo‘yicha sizda allaqachon faol buyurtma mavjud.\n"
                        "⏳ Iltimos, avvalgi buyurtma yakunlanishini kuting."
                    )

                # ✅ Admin uchun to‘liq xabar
                error_message = (
                    f"⚠️ BUYURTMA XATOLIGI\n"
                    f"Xizmat: {name}\n"
                    f"Service ID: {service_id}\n"
                    f"User: {user_id}\n"
                    f"Link: {link}\n"
                    f"Quantity: {quantity}\n"
                    f"Narx: {price}\n"
                    f"API Xato: {order['error']}"
                )
                await bot.send_message(-1003588825972, error_message)

            await state.clear()

    except Exception as e:
        await send_error(e)