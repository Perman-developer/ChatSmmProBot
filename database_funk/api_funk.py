import aiohttp
from config import API_URL
import json
from pathlib import Path
import aiofiles

from utils.error import send_error
# TAYYOR
# ==========================================================
# ASOSIY FUNKSIYA: Topsmm API so'rovi yuborish
# ==========================================================

async def SMM_REQUESTS(api_id, action, **kwargs):
    """
    Topsmm yoki boshqa API’ga GET so'rov yuboradi va JSON natija qaytaradi.
    """
    try:
        url = API_URL(str(api_id))["url"]
        API_KEY = API_URL(str(api_id))["key"]

        params = {"key": API_KEY, "action": action}
        params.update(kwargs)

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    try:
                        # ✅ Avval JSON o‘qishga urinamiz
                        return await response.json()
                    except aiohttp.ContentTypeError:
                        # 🔄 JSON emas, lekin matn qaytgan holat
                        text = await response.text()
                        try:
                            # Ba’zan server JSON qaytaradi, lekin Content-Type noto‘g‘ri bo‘ladi
                            return json.loads(text)
                        except json.JSONDecodeError:
                            print(f"⚠️ {action.upper()} javobi JSON emas:\n{text[:300]}")
                            return {"error": "Invalid JSON response", "raw": text[:200]}
                else:
                    print(f"{action.upper()} Xato: {response.status}")
                    return {"error": f"HTTP {response.status}"}
    except Exception as e:
        await send_error(e)
        return {"error": str(e)}


# ==========================================================
# QISQA FUNKSIYALAR: qulay wrapperlar
# ==========================================================
async def GET_SERVICES(api_id):
    """Barcha xizmatlar ro'yxatini olish"""
    return await SMM_REQUESTS(api_id, "services")

async def SEND_ORDER(api_id, service, link, quantity):
    """Buyurtma yaratish"""
    return await SMM_REQUESTS(api_id, "add", service=service, link=link, quantity=quantity)

async def GET_STATUS(api_id, order_id):
    """Buyurtma holatini olish"""
    return await SMM_REQUESTS(api_id, "status", order=order_id)

async def GET_BALANCE(api_id):
    """Hisob balansini olish"""
    return await SMM_REQUESTS(api_id, "balance")

async def GET_REFILL(api_id, order_id):
    """Buyurtma refill qilish"""
    return await SMM_REQUESTS(api_id, "refill", order=order_id)

async def GET_CANCEL(api_id, order_id):
    """Buyurtmani bekor qilish"""
    return await SMM_REQUESTS(api_id, "cancel", order=order_id)


def JSON_FILE(api_id):
    """API identifikatori bo‘yicha JSON fayl nomini qaytaradi"""
    return Path(f"database/services_{api_id}.json")


# ==========================================================
# SERVICES JSON UPDATE (listni to'liq saqlash)
# ==========================================================
async def SAVE_SERVICES_TO_JSON(api_id):
    """
    Topsmm API-dan xizmatlar ro'yxatini olib, services.json faylini yangilash
    - Listni to'liq saqlaydi, merge qilinmaydi
    """
    try:
        # 1️⃣ Topsmm-dan yangi servicelarni olish
        NEW_SERVICES = await GET_SERVICES(api_id)
        if not NEW_SERVICES:
            print("❌ Xizmatlar olinmadi")
            return

        FILE = JSON_FILE(api_id)

        # 2️⃣ JSON faylga async yozish
        async with aiofiles.open(FILE, "w", encoding="utf-8") as f:
            await f.write(json.dumps(NEW_SERVICES, ensure_ascii=False, indent=4))

        print(f"✅ {len(NEW_SERVICES)} ta service services_{api_id}.json ga saqlandi")

    except Exception as e:
        await send_error(e)


# ==========================================================
# SERVICES JSON O‘QISH (to‘liq yoki bitta xizmat)
# ==========================================================
async def LOAD_SERVICES_FROM_JSON(api_id: int, service_id: int = None):
    """
    services_{api_id}.json fayldan xizmat(lar)ni o‘qib qaytaradi
    - Agar service_id berilmasa → butun ro‘yxatni qaytaradi
    - Agar service_id berilsa → faqat shu xizmatni (yoki None) qaytaradi
    """
    FILE = JSON_FILE(api_id)

    try:
        if not FILE.exists():
            print(f"⚠️ Fayl topilmadi: {FILE}")
            return None if service_id else []

        # Faylni async o‘qish
        async with aiofiles.open(FILE, "r", encoding="utf-8") as f:
            content = await f.read()

        # JSONni Python obyektga o‘tkazish
        data = json.loads(content)

        # 🔹 Agar service_id so‘ralgan bo‘lsa, faqat bittasini qidiramiz
        if service_id is not None:
            service_id = int(service_id)
            for service in data:
                if int(service.get("service", 0)) == service_id:
                    return service
            # Topilmasa
            return None

        # 🔹 Aks holda, butun ro‘yxatni qaytaramiz
        return data

    except json.JSONDecodeError:
        print(f"❌ JSON fayl buzilgan: {FILE}")
        return None if service_id else []

    except Exception as e:
        await send_error(e)
        return None if service_id else []
