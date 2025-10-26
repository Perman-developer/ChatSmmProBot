import asyncio
import logging
from loader import bot, dp
#=======================================================================================
from run_funks import run
from handlers.users import start, xizmatlar, order, buyurtmalarim, my_balance, send_pay, referal, support, bot_yaratish 
from handlers.admin import add_service, edit_service, statistika, accept_pay

#========================================================================================
# Logging sozlamalari
logging.basicConfig(level=logging.INFO)

#========================================================================================
# Middlewarelarni qo‘shish


# Routerlarni qo‘shish
dp.include_router(start.user_router)
dp.include_router(xizmatlar.user_router)
dp.include_router(buyurtmalarim.user_router)
dp.include_router(my_balance.user_router)
dp.include_router(referal.user_router)
dp.include_router(bot_yaratish.user_router)

dp.include_router(order.user_router)
dp.include_router(send_pay.user_router)
dp.include_router(support.user_router)

#========================================
dp.include_router(add_service.admin_router)
dp.include_router(edit_service.admin_router)
dp.include_router(statistika.admin_router)
dp.include_router(accept_pay.admin_router)

#========================================================================================
# Asosiy funksiya
async def main():
    try:
        # Ma'lumotlar bazasini yaratish
        asyncio.create_task(run())
        # Botni polling rejimida ishga tushirish
        await dp.start_polling(bot, polling_timeout=20)
    finally:
        # Bot sessiyasini to‘g‘ri yopish
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi!")