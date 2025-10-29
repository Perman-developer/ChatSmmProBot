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
# referal link orqali /start
#========================================================================================
@user_router.message(CommandStart(deep_link=True))
async def bot_start_ref(message: Message, state: FSMContext):
    try:
        await state.clear()
        args = message.text.split(maxsplit=1)
        ref_id = args[1] if len(args) > 1 else None
        user_id = message.from_user.id

        # ---------- obuna tekshiruvi ----------
        if not await check_subscribe(user_id):
            url = f"https://t.me/{KANAL}"
            kb = await SUBSCRIBE_KEYBOARD(url, ref_id)
            await message.answer("KANALGA OBUNA BO‘LING", reply_markup=kb)
            return

        # ---------- foydalanuvchi bazaga qo‘shilishi ----------
        user_info = await GET_USER(user_id)
        if not user_info:                     # yangi foydalanuvchi
            await ADD_USER(user_id)

        # ---------- referal jarayoni ----------
        if ref_id and ref_id.isdigit():
            ref_id = int(ref_id)
            if ref_id != user_id:            # o‘ziga o‘zi referal bo‘lmasin
                ref_info = await GET_USER(ref_id)

                # bonus faqat yangi foydalanuvchi uchun
                if not user_info and ref_info:
                    await ADD_REF_BAL(ref_id, ref_bonus)
                    try:
                        await bot.send_message(
                            ref_id,
                            f"Sizning referal havolangiz orqali yangi foydalanuvchi qo‘shildi!\n"
                            f"Bonus: <b>{ref_bonus:,}</b> so‘m",
                            parse_mode="HTML"
                        )
                    except Exception as e:
                        await send_error(e)

        # ---------- xush kelibsiz xabar ----------
        menu = await MENU(AdminFilter(user_id))
        await message.answer(MSG1, reply_markup=menu)

    except Exception as e:
        await send_error(e)


#========================================================================================
# oddiy /start yoki “Orqaga”
#========================================================================================
@user_router.message(CommandStart())
@user_router.message(F.text == "Orqaga")
async def bot_start(message: Message, state: FSMContext):
    try:
        await state.clear()
        user_id = message.from_user.id

        # ---------- obuna ----------
        if not await check_subscribe(user_id):
            url = f"https://t.me/{KANAL}"
            kb = await SUBSCRIBE_KEYBOARD(url)
            await message.answer("KANALGA OBUNA BO‘LING", reply_markup=kb)
            return

        # ---------- bazaga qo‘shish ----------
        if not await GET_USER(user_id):
            await ADD_USER(user_id)

        menu = await MENU(AdminFilter(user_id))
        await message.answer(MSG1, reply_markup=menu)

    except Exception as e:
        await send_error(e)


#========================================================================================
# “Obuna bo‘ldim” tugmasi
#========================================================================================
@user_router.callback_query(F.data.startswith("subscribe:"))
async def subscribe_callback(callback: CallbackQuery):
    try:
        await callback.message.delete()
        parts = callback.data.split(":")
        ref_id = parts[1] if len(parts) == 2 else None
        user_id = callback.from_user.id

        # ---------- obuna ----------
        if not await check_subscribe(user_id):
            url = f"https://t.me/{KANAL}"
            kb = await SUBSCRIBE_KEYBOARD(url, ref_id)
            await callback.message.answer("KANALGA OBUNA BO‘LING", reply_markup=kb)
            return

        # ---------- bazaga qo‘shish ----------
        user_info = await GET_USER(user_id)
        if not user_info:
            await ADD_USER(user_id)

        # ---------- referal ----------
        if ref_id and ref_id.isdigit():
            ref_id = int(ref_id)
            if ref_id != user_id:
                ref_info = await GET_USER(ref_id)

                # bonus faqat yangi foydalanuvchi uchun
                if not user_info and ref_info:
                    await ADD_REF_BAL(ref_id, ref_bonus)
                    try:
                        await bot.send_message(
                            ref_id,
                            f"Sizning referal havolangiz orqali yangi foydalanuvchi qo‘shildi!\n"
                            f"Bonus: <b>{ref_bonus:,}</b> so‘m",
                            parse_mode="HTML"
                        )
                    except Exception as e:
                        await send_error(e)

        menu = await MENU(AdminFilter(user_id))
        await callback.message.answer(MSG1, reply_markup=menu)

    except Exception as e:
        await send_error(e)