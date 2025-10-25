import traceback
import sys
from config import ADMIN_ID
from loader import bot

# ⚠️ Xatolikni admin ga batafsil yuborish
async def send_error(error: Exception):
    # To‘liq tracebackni olish
    exc_type, exc_value, exc_traceback = sys.exc_info()
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))

    # Xabarni qisqartirish (Telegram limitdan oshmasligi uchun)
    if len(tb) > 3800:
        tb = tb[-3800:]

    text = (
        "⚠️ <b>Xatolik yuz berdi!</b>\n\n"
        f"<b>Xatolik turi:</b> <code>{exc_type.__name__}</code>\n"
        f"<b>Xabar:</b> <code>{error}</code>\n\n"
        f"<b>Traceback:</b>\n<code>{tb}</code>"
    )

    try:
        await bot.send_message(ADMIN_ID, text)
    except Exception as e:
        print("❌ Xatolikni yuborishda muammo:", e)