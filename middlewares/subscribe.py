from config import KANAL_ID
from loader import bot
from utils.error import send_error


async def check_subscribe(user_id):
   try:
       member = await bot.get_chat_member(KANAL_ID, user_id)
       if member.status in ["member", "administrator", "creator"]:
           return True
       else:
           return False
   except Exception as e:
       await send_error(e)