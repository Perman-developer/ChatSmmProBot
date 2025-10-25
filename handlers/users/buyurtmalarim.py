from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database_funk.orders import GET_USER_ORDERS, GET_ORDER
from keyboards.users.inline import ORDERS_KEYBOARD, BACK_TO_ORDERS
from database_funk.api_funk import LOAD_SERVICES_FROM_JSON, GET_REFILL, GET_CANCEL
from utils.error import send_error
from utils.status_translate import translate_status


from texts.users import MSG29


user_router = Router()

@user_router.message(F.text == "🔍 Buyurtmalarim")
async def buyurtmalarim(message: Message, state: FSMContext):
   await state.clear()
   user_id = message.from_user.id
   orders = await GET_USER_ORDERS(user_id)
   if not orders:
       await message.answer("<b>❗️ Sizda buyurtmalar mavjud emas.</b>", parse_mode="HTML")
       return
   kb = await ORDERS_KEYBOARD(user_id)
   await message.answer("<b>📊 Buyurtmalaringiz royxati  ....   </b>", parse_mode="HTML", reply_markup=kb)



@user_router.callback_query(F.data.startswith("ordersback"))
async def ordersback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = callback.from_user.id
    orders = await GET_USER_ORDERS(user_id)
    if not orders:
        await callback.message.answer("<b>❗️ Sizda buyurtmalar mavjud emas.</b>", parse_mode="HTML")
        return
    kb = await ORDERS_KEYBOARD(user_id)
    await callback.message.edit_text("<b>📊 Buyurtmalar:  .....    </b>", parse_mode="HTML", reply_markup=kb)

 #========================================================
# 🔹 BUYURTMALARIM SAHIFALASH
#========================================================
@user_router.callback_query(F.data.startswith("page:"))
async def paginate_orders(callback: CallbackQuery):
    try:
        page = int(callback.data.split(":")[1])
        kb = await ORDERS_KEYBOARD(callback.from_user.id, page)
        await callback.message.edit_reply_markup(reply_markup=kb)
        await callback.answer()
    except Exception as e:
        await send_error(e)
    finally:
        await callback.answer()


@user_router.callback_query(F.data.startswith("order:"))
async def order_callback(callback: CallbackQuery, state: FSMContext):
     try:
          id = callback.data.split(":")[1]
          order = await GET_ORDER(id)
          if not order:
               await callback.answer("Buyurtma topilmadi", show_alert=True)
               return
          text = MSG29.format(
               order_id=order["id"],
               id=order["service_id"],
               service_name=order["name"],
               link=order["link"],
               quantity=order["quantity"],
               price=order["price"],
               created_at=order["created_at"],
               status=translate_status(order["status"])
          )
          api_id = order["api_id"]
          service_id = order["service_api_id"]
          service = await LOAD_SERVICES_FROM_JSON(api_id, service_id)
          if service:
               refill = service.get("refill")
               cancel = service.get("cancel")
          else:
               refill = 0
               cancel = 0 
          kb = await BACK_TO_ORDERS(id, refill=refill, cancel=cancel)
          await callback.message.edit_text(text, reply_markup=kb, disable_web_page_preview=True)
          await callback.answer()
          await state.clear()
     except Exception as e:
          await send_error(e)

#refill
@user_router.callback_query(F.data.startswith("refill:"))
async def refill_callback(callback: CallbackQuery, state: FSMContext):
      try:
           id = callback.data.split(":")[1]
           order = await GET_ORDER(id)
           if not order:
                await callback.answer("Buyurtma topilmadi", show_alert=True)
                return
           api_id = order["api_id"]
           order_id = order["order_id"]
           refill = await GET_REFILL(api_id, order_id)
           if refill.get("refill"):
                await callback.message.edit_text("Buyurtma qayta to'ldirildi")
           else:
                await callback.answer("Buyurtma qayta to'ldirilishi mumkin emas")
           await callback.answer()
      except Exception as e:
           await send_error(e)

#cancel
@user_router.callback_query(F.data.startswith("cancel:"))
async def cancel_callback(callback: CallbackQuery, state: FSMContext):
      try:
           id = callback.data.split(":")[1]
           order = await GET_ORDER(id)
           if not order:
                await callback.answer("Buyurtma topilmadi", show_alert=True)
                return
           api_id = order["api_id"]
           order_id = order["order_id"]
           cancel = await GET_CANCEL(api_id, order_id)
           if cancel.get("cancel"):
                await callback.message.edit_text("Buyurtma bekor qilindi")
           else:
                await callback.message.edit_text("Buyurtma bekor qilinishi mumkin emas")
           await callback.answer()
      except Exception as e:
            await send_error(e)

