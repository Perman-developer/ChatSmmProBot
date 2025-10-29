from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
#============================================================================================
from texts.users import MSG13
from loader import bot


user_router = Router()

@user_router.message(F.text == "👥Referral")
async def referal(message: Message, state: FSMContext):
   await state.clear()
  
   user_id = message.from_user.id
   bot_data = await bot.get_me()
   bot_name = bot_data.username
   reflink = f"https://t.me/{bot_name}?start={user_id}"
   await message.answer(MSG13.format(reflink=reflink), disable_web_page_preview=True)
   
   
