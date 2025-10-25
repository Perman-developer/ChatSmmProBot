from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from database_funk.users import ADD_BALL
from utils.error import send_error
from loader import bot

admin_router = Router()

@admin_router.callback_query(F.data.startswith("accept:"))
async def accept_pay(callback: CallbackQuery):
   try:
      user_id = int(callback.data.split(":")[1])
      amount = float(callback.data.split(":")[2])
      await ADD_BALL(user_id, amount)
      await bot.send_message(user_id, f"Sizning hisobingizga {amount} so'm qo'shildi")
      await callback.message.edit_text("To'lov qabul qilindi")
      await callback.answer()
   except Exception as e:
      await send_error(e)

class ReplyMsg(StatesGroup):
    msg = State()


@admin_router.callback_query(F.data.startswith("reply:"))
async def reply_pay(callback: CallbackQuery, state: FSMContext):
   try:
      user_id = int(callback.data.split(":")[1])
      await callback.message.answer("Xabarni kiriting")
      await state.set_state(ReplyMsg.msg)
      await state.update_data(user_id=user_id)
      await callback.answer()
   except Exception as e:
     await send_error(e)



@admin_router.message(ReplyMsg.msg)
async def reply_msg(message: Message, state: FSMContext):
   try:
      data = await state.get_data()
      user_id = data["user_id"]
      msg = message.text
      await bot.send_message(user_id, msg)
      await message.answer("Xabar yuborildi")
      await state.clear()
   except Exception as e:
      await send_error(e)