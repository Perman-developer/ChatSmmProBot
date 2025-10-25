from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

#========================================================================================
from texts.users import MSG12
from database_funk.users import GET_USER
from database_funk.orders import GET_USER_ORDERS
from utils.error import send_error
from utils.time import TASHKENT_TIME
#========================================================================================


user_router = Router()


@user_router.message(F.text == "👤Mening hisobim")
async def my_balance(message: Message, state: FSMContext):
    try:
        await state.clear()
        user_id = message.from_user.id
        user_info = await GET_USER(user_id)
        
        # Agar user_info None bo‘lsa, foydalanuvchi topilmadi
        if not user_info:
            await message.answer("Sizning hisobingiz topilmadi. Iltimos, /start orqali ro‘yxatdan o‘ting.")
            return

        orders = await GET_USER_ORDERS(user_id)
        spent_balance = await GET_USER_ORDERS(user_id, SUM_PRICE=True)
        
        if orders is None:
            orders = []
            spent_balance = 0.0
        orders_count = len(orders)
        print(2)
        referrals_count = user_info.get("referrals_count", 0)  # Xavfsiz murojaat
        balance = user_info.get("balance", 0.0)  # Xavfsiz murojaat
        
        spent_balance = round(spent_balance, 2)
        current_time = TASHKENT_TIME()
        print(3)
        await message.answer(
            MSG12.format(
                user_id=user_id,
                balance=balance,
                spent_balance=spent_balance,
                orders_count=orders_count,
                referrals_count=referrals_count,
                current_time=current_time
            )
        )
        await state.clear()
    except Exception as e:
        await send_error(e)  # `message` parametrini qo‘shish
