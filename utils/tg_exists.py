from aiogram import Bot

# HOZIRCHA ISHLATILMAYAPDI

async def tg_exists(bot: Bot, link: str) -> bool:
    """
    Telegram obyekti (kanal, guruh, bot yoki foydalanuvchi) mavjudligini tekshiradi.
    True -> mavjud
    False -> mavjud emas yoki bot kira olmaydi
    """
    try:
        if "t.me/" in link:
            username = link.split("t.me/")[1].split("/")[0]
        elif "telegram.me/" in link:
            username = link.split("telegram.me/")[1].split("/")[0]
        else:
            username = link.lstrip("@")

        username = username.strip().split("/")[0]
        chat = await bot.get_chat(username)
        return bool(chat)

    except Exception:
        return False