from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

#========================================================================================
from texts.users import MSG1
from keyboards.users.reply import MENU
from keyboards.users.inline import SUBSCRIBE_KEYBOARD
from database_funk.users import ADD_USER, GET_USER, ADD_REF_BAL
from utils.error import send_error
from loader import bot
from config import ref_bonus, KANAL
from middlewares.subscribe import check_subscribe
from filters.admin_filter import AdminFilter
#========================================================================================

user_router = Router()

#========================================================================================
# 📎 /start orqali referal linkni qabul qilish
#========================================================================================

@user_router.message(CommandStart(deep_link=True))
async def bot_start_ref(message: Message, state: FSMContext):
    try:
        await state.clear()
        args = message.text.split(maxsplit=1)
        ref_id = args[1] if len(args) > 1 else None
        user_id = message.from_user.id

        # Kanal obuna tekshirish
        if not await check_subscribe(user_id):
            url = f"https://t.me/{KANAL}"
            kb = await SUBSCRIBE_KEYBOARD(url, ref_id)
            await message.answer("❌ KANALGA OBUNA BO'LING", reply_markup=kb)
            return

        if ref_id and ref_id.isdigit():
            ref_id = int(ref_id)

            # O‘zi o‘zini referal qila olmasin
            if ref_id != user_id:
                user_info = await GET_USER(user_id)
                ref_info = await GET_USER(ref_id)

                # Agar foydalanuvchi birinchi marta kirayotgan bo‘lsa
                if not user_info:
                    await ADD_USER(user_id)

                    # Agar referent mavjud bo‘lsa — unga bonus berish
                    if ref_info:
                        await ADD_REF_BAL(ref_id, ref_bonus)
                        try:
                            await bot.send_message(
                                ref_id,
                                f"🎁 Sizning referal havolangiz orqali yangi foydalanuvchi qo‘shildi!\n"
                                f"💵 Bonus: <b>{ref_bonus:,}</b> so‘m",
                                parse_mode="HTML"
                            )
                        except Exception as e:
                            await send_error(e)

        # Foydalanuvchiga xush kelibsiz xabari
        menu = await MENU(AdminFilter(user_id))
        await message.answer(MSG1, reply_markup=menu)
        await ADD_USER(user_id)

    except Exception as e:
        await send_error(e)

#========================================================================================
# 🚀 Oddiy /start komandasi (referalsiz)
#========================================================================================
@user_router.message(CommandStart())
@user_router.message(F.text == "⬅️ Orqaga")
async def bot_start(message: Message, state: FSMContext):
    try:
        await state.clear()
        user_id = message.from_user.id

        # Kanal obuna tekshirish
        if not await check_subscribe(user_id):
            url = f"https://t.me/{KANAL}"
            kb = await SUBSCRIBE_KEYBOARD(url)
            await message.answer("❌ KANALGA OBUNA BO'LING", reply_markup=kb)
            return

        await ADD_USER(user_id)
        menu = await MENU(AdminFilter(user_id))
        await message.answer(MSG1, reply_markup=menu)

    except Exception as e:
        await send_error(e)

#========================================================================================
# 🔁 "Obuna bo‘ldim" tugmasi callback handleri
#========================================================================================
@user_router.callback_query(F.data.startswith("subscribe:"))
async def subscribe_callback(callback: CallbackQuery):
    try:
        await callback.message.delete()
        if len(callback.data.split(":")) == 2:
            ref_id = callback.data.split(":")[1]
        else:
            ref_id = None
        user_id = callback.from_user.id

        # Kanal obuna tekshirish
        if not await check_subscribe(user_id):
            url = f"https://t.me/{KANAL}"
            kb = await SUBSCRIBE_KEYBOARD(url)
            await callback.message.answer("❌ KANALGA OBUNA BO'LING", reply_markup=kb)
            return

        # Referal bonus jarayoni
        if ref_id and ref_id.isdigit():
            ref_id = int(ref_id)

            if ref_id != user_id:
                user_info = await GET_USER(user_id)
                ref_info = await GET_USER(ref_id)

                if not user_info:
                    await ADD_USER(user_id)

                    if ref_info:
                        await ADD_REF_BAL(ref_id, ref_bonus)
                        try:
                            await bot.send_message(
                                ref_id,
                                f"🎁 Sizning referal havolangiz orqali yangi foydalanuvchi qo‘shildi!\n"
                                f"💵 Bonus: <b>{ref_bonus:,}</b> so‘m",
                                parse_mode="HTML"
                            )
                        except Exception as e:
                            await send_error(e)

        # Xush kelibsiz xabar
        menu = await MENU(AdminFilter(user_id))
        await callback.message.answer(MSG1, reply_markup=menu)
        await ADD_USER(user_id)

    except Exception as e:
        await send_error(e)