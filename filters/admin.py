# filters/admin_filter.py
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery

from config import ADMIN_IDS
class AdminFilter(BaseFilter):
    """
    Foydalanuvchi admin bo'lsa True qaytaradi.
    """
    async def __call__(self, message: Message | CallbackQuery) -> bool:
        return message.from_user.id in ADMIN_IDS