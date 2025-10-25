from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext


user_router = Router()

@user_router.message(F.text == "🤖 Bot yaratish")
async def bot_yaratish(message: Message, state: FSMContext):
   await state.clear()
   await message.answer("😔 Bu bolim hali qoshilmagan")
  