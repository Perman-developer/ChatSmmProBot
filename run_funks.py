import asyncio
from database_funk.users import CREATE_USERS_TABLE
from database_funk.services import CREATE_SERVICES_TABLE
from database_funk.orders import CREATE_ORDERS_TABLE, UPDATE_ORDERS_STATUS
from database_funk.api_funk import SAVE_SERVICES_TO_JSON
from config import _config, services_update_time, status_update_time

async def run():
    # 🔹 Dastlabki yaratish
    await CREATE_USERS_TABLE()
    await CREATE_ORDERS_TABLE()

    # 🔹 API xizmatlarini yuklash
    for i in range(1, len(_config["api"]) + 1):
        await SAVE_SERVICES_TO_JSON(i)

    # 🔹 Taskslarni parallel ishga tushirish
    async def update_services_loop():
        while True:
            await CREATE_SERVICES_TABLE()
            await asyncio.sleep(services_update_time)

    async def update_orders_loop():
        while True:
            await UPDATE_ORDERS_STATUS()
            await asyncio.sleep(status_update_time)

    # 🔹 Ikkala loopni parallel ishga tushurish
    await asyncio.gather(
        update_services_loop(),
        update_orders_loop()
    )

if __name__ == "__main__":
    asyncio.run(run())