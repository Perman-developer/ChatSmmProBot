from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

#========================================================================================
from keyboards.users.inline import PAYMENT_KEYBOARD, CONFIRM_PAYMENT
from keyboards.admin.inline import ACCEPT_PAY
from texts.users import MSG15, MSG16, MSG17, MSG18, MSG19
from utils.error import send_error
from loader import bot
from database.pay_methods import pay_methods
from config import KARTA, FIO, ADMIN_ID, min_pay, max_pay
#========================================================================================

user_router = Router()

#========================================================================================
@user_router.message(F.text == "💰Hisob toʻldirish")
async def send_pay(message: Message, state: FSMContext):
   try:
      await state.clear()
      kb = await PAYMENT_KEYBOARD()
      await message.answer(MSG15, reply_markup=kb)
   except Exception as e:
      await send_error(e)

#========================================================================================
@user_router.callback_query(F.data.startswith("pay:"))
async def pay_callback(callback: CallbackQuery, state: FSMContext):
   try:
      await callback.message.delete()
      pay_method = callback.data.split(":")[1]
      await state.update_data(pay_method=pay_method)
      kb = await CONFIRM_PAYMENT()
      await callback.message.answer(
         MSG16.format(
            karta=KARTA,
            FIO=FIO,
            min_pay=min_pay,
            max_pay=max_pay
         ),
         reply_markup=kb
      )
   except Exception as e:
      await send_error(e)
   finally:
      await callback.answer()

#========================================================================================
# Hisob toldirishga anketa toldirish  
#========================================================================================
class PayForm(StatesGroup):
   amount = State()
   photo = State()

#========================================================================================
@user_router.callback_query(F.data == "confirm_payment")
async def confirm_pay(callback: CallbackQuery, state: FSMContext):
   try:
      await callback.message.delete()
      await callback.message.answer(MSG17)
      await state.set_state(PayForm.amount)
   except Exception as e:
      await send_error(e)
   finally:
      await callback.answer()

#========================================================================================
@user_router.message(PayForm.amount)
async def process_amount(message: Message, state: FSMContext):
   try:
      amount = message.text
      try:
         amount = int(amount)
      except ValueError:
         await message.answer("⚠️ Summa raqamda bo'lishi kerak!")
         
      if amount < min_pay or amount > max_pay:
         await message.answer(f"⚠️ Summa {min_pay} dan {max_pay} gacha bo'lishi kerak!")
         return

      await state.update_data(amount=amount)
      await message.answer(MSG18)
      await state.set_state(PayForm.photo)
   except Exception as e:
      await send_error(e)

#========================================================================================
@user_router.message(PayForm.photo, F.photo)
async def process_photo(message: Message, state: FSMContext):
   try:
      user_id = message.from_user.id
      photo = message.photo[-1].file_id
      data = await state.get_data()
      amount = data.get("amount")
      pay_method = data.get("pay_method")
      pay_name = pay_methods[pay_method]
      kb = await ACCEPT_PAY(user_id, amount)

      await bot.send_photo(
         ADMIN_ID,
         photo,
         caption=f"🆔️: {user_id}\n💰 Summa: {amount}\n💳 To'lov turi: {pay_name}", reply_markup=kb
      )

      await message.answer(MSG19)
      await state.clear()
   except Exception as e:
      await send_error(e)