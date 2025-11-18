# ========================================================
# 📦 IMPORTLAR
# ========================================================

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database_funk.services import GET_PLATFORMS, GET_CATEGORIES, GET_SERVICES
from database_funk.orders import GET_USER_ORDERS
from database_funk.api_funk import LOAD_SERVICES_FROM_JSON
from database.pay_methods import pay_methods

from utils.kurs_calculator import CALCULATOR
from utils.status_translate import translate_status


# ========================================================
# 🔹 PLATFORM TANLASH TUGMALARI
# ========================================================

async def PLATFORM_KEYBOARD(ADMIN: bool = False):
    platforms = await GET_PLATFORMS()
    builder = InlineKeyboardBuilder()

    for platform in platforms:
        builder.add(
            InlineKeyboardButton(
                text=platform["name"],
                callback_data=f"a:{platform['id']}"
            )
        )

    if ADMIN:
        builder.add(
            InlineKeyboardButton(text="➕ Qo'shish", callback_data="add_platform")
        )

    builder.adjust(1, 2)
    return builder.as_markup()


# ========================================================
# 🔹 KATEGORIYA TANLASH TUGMALARI
# ========================================================

async def CATEGORY_KEYBOARD(platform_id: int, ADMIN: bool = False):
    categories = await GET_CATEGORIES(platform_id)
    builder = InlineKeyboardBuilder()

    for category in categories:
        builder.add(
            InlineKeyboardButton(
                text=category["name"],
                callback_data=f"b:{platform_id}:{category['id']}"
            )
        )

    builder.adjust(1)

    if ADMIN:
        builder.row(
            InlineKeyboardButton(text="➕ Qo'shish", callback_data=f"add_category:{platform_id}"),
            InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"edit_platform:{platform_id}")
        ).row(
            InlineKeyboardButton(text="❌ O'chirish", callback_data=f"delete_platform:{platform_id}")
        )

    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back:menu"))
    return builder.as_markup()


# ========================================================
# 🔹 XIZMATLAR RO‘YXATI TUGMALARI
# ========================================================

async def SERVICES_KEYBOARD(platform_id: int, category_id: int, ADMIN: bool = False):
    services = await GET_SERVICES(platform_id, category_id)
    builder = InlineKeyboardBuilder()

    for service in services:
        api_id = service.get("api_id")
        service_id = service.get("service_id")

        # Narxni olish
        rate = service.get("price")
        if rate is not None:
            price = float(rate)
        else:
            service_api = await LOAD_SERVICES_FROM_JSON(api_id, service_id)
            # service_api None bo'lsa, rate = 0
            rate = service_api.get("rate") if service_api else 0
            price = CALCULATOR(api_id, float(rate), 1000)

        # Tugma matni
        text = f"{service.get('name', 'No Name')[:30]} — {price} so'm"
        builder.add(
            InlineKeyboardButton(text=text, callback_data=f"c:{service.get('id', 0)}")
        )

    builder.adjust(1)

    if ADMIN:
        builder.row(
            InlineKeyboardButton(
                text="➕ Qo'shish", callback_data=f"add_service:{platform_id}:{category_id}"
            ),
            InlineKeyboardButton(
                text="✏️ Tahrirlash", callback_data=f"edit_category:{category_id}"
            )
        ).row(
            InlineKeyboardButton(
                text="❌ O'chirish", callback_data=f"delete_category:{category_id}"
            )
        )

    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"back:{platform_id}"))
    return builder.as_markup()
# ========================================================
# 🔹 XIZMAT TANLASH TUGMALARI
# ========================================================

async def SERVICE_KEYBOARD(platform_id: int, category_id: int, id: int, ADMIN: bool = False):
    builder = InlineKeyboardBuilder()

    builder.add(
        InlineKeyboardButton(text="✅ Buyurtma berish", callback_data=f"service:{id}")
    )

    if ADMIN:
        builder.row(
            InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"edit_service:{id}"),
            InlineKeyboardButton(text="❌ O'chirish", callback_data=f"delete_service:{id}")
        )

    builder.row(
        InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"back:{platform_id}:{category_id}")
    )
    return builder.as_markup()


# ========================================================
# 🔹 BUYURTMANI TASDIQLASH
# ========================================================

async def CONFIRM_ORDER():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="✅ Yuborish", callback_data="confirm_order")
    )
    builder.adjust(1)
    return builder.as_markup()


# ========================================================
# 💰 TO‘LOV USULLARI
# ========================================================

async def PAYMENT_KEYBOARD():
    builder = InlineKeyboardBuilder()
    for key, value in pay_methods.items():
        builder.add(
            InlineKeyboardButton(text=value, callback_data=f"pay:{key}")
        )
    builder.adjust(2)
    return builder.as_markup()


# ========================================================
# 💳 TO‘LOV TASDIQLASH
# ========================================================

async def CONFIRM_PAYMENT():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="✅ To'lov qildim", callback_data="confirm_payment"),
        InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_payment")
    )
    builder.adjust(1)
    return builder.as_markup()


# ========================================================
# 📢 KANALGA OBUNA
# ========================================================

async def SUBSCRIBE_KEYBOARD(url: str, ref_id: int = None):
    builder = InlineKeyboardBuilder()
    callback = f"subscribe:{ref_id}" if ref_id else "subscribe:"
    builder.add(
        InlineKeyboardButton(text="📢 Kanal", url=url),
        InlineKeyboardButton(text="✅ Obuna bo'ldim", callback_data=callback)
    )
    builder.adjust(1)
    return builder.as_markup()


# ========================================================
# 🔹 BUYURTMALAR NI OLISH
# ========================================================

PER_PAGE = 6  # Har sahifada nechta buyurtma

async def ORDERS_KEYBOARD(user_id: int, page: int = 1):
    orders = await GET_USER_ORDERS(user_id)
    if not orders:
        return None

    # 🔹 Buyurtmalarni teskari tartibda chiqaramiz
    orders = orders[::-1]

    builder = InlineKeyboardBuilder()
    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    total_pages = (len(orders) + PER_PAGE - 1) // PER_PAGE

    # Faqat kerakli bo‘lagini olish
    for order in orders[start:end]:
        status = translate_status(order['status'])
        text = f"🆔️ {order['id']} - {status}"
        builder.add(
            InlineKeyboardButton(text=text, callback_data=f"order:{order['id']}")
        )

    builder.adjust(1)

    # Navigatsiya tugmalari (Oldingi / Keyingi)
    nav_buttons = []
    if page > 1:
        nav_buttons.append(
            InlineKeyboardButton(text="⬅️ Oldingi", callback_data=f"page:{page-1}")
        )
    if page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton(text="➡️ Keyingi", callback_data=f"page:{page+1}")
        )

    if nav_buttons:
        builder.row(*nav_buttons)

    return builder.as_markup()

# ========================================================
# 🔹 BUYURTMALARIM DAN ORTGA
# ========================================================

async def BACK_TO_ORDERS(id, refill=False, cancel=False):
    builder = InlineKeyboardBuilder()

    if refill and cancel:
        builder.add(
            InlineKeyboardButton(text="➕️ Qayta to'ldirish", callback_data=f"refill:{id}"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"cancel:{id}")
        )
    elif refill:
        builder.add(
            InlineKeyboardButton(text="➕️ Qayta to'ldirish", callback_data=f"refill:{id}")
        )
    elif cancel:
        builder.add(
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"cancel:{id}")
        )

    builder.add(
        InlineKeyboardButton(text="⬅️ Orqaga", callback_data="ordersback")
    )
    builder.adjust(2, 1)
    return builder.as_markup()



