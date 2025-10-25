from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

#========================================================================================
from texts.users import MSG20
from config import ADMIN_ID
from loader import bot
from utils.error import send_error
from keyboards.users.reply import MENU
from keyboards.admin.inline import SEND_ANSWER

user_router = Router()

class SupportState(StatesGroup):
    message = State()
  
@user_router.message(F.text == "☎️ Qo'llab-quvvatlash")
async def support(message: Message, state: FSMContext):
   await state.clear()
   await message.answer(MSG20)
   await state.set_state(SupportState.message)


@user_router.message(SupportState.message)
async def support_message(message: Message, state: FSMContext):
   user_id = message.from_user.id
   text = message.text
   if len(text) > 200:
       await message.answer("Murojaat matni 200 belgidan oshmasligi kerak.\n Iltimos, qayta yuboring.")
       return
   kb = await SEND_ANSWER(user_id)
   menu = await MENU(user_id)
   await message.answer("Murojaatingiz qabul qilindi. Admin siz bilan bog'lanadi.", reply_markup=menu)
   await bot.send_message(ADMIN_ID, f"Yangi murojaat:\n\n{text}\n\nFoydalanuvchi: {message.from_user.id}", reply_markup=kb)
   await state.clear()


