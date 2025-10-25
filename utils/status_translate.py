
def translate_status(status: str) -> str:
    """
    Topsmm.uz statusini o'zbek tiliga aylantiradi
    """
    status_map = {
        "Completed": "✅ Bajarildi",
        "In progress": "🔄 Jarayonda",
        "Processing": "🔄 Jarayonda",
        "Pending": "⏳ Kutilmoqda",
        "Canceled": "❌ Bekor qilindi",
        "Partial": "⚠️ Qisman bajarildi",
        "Refunded": "💰 Qaytarildi",
        "Hold": "⏸ To‘xtatilgan"
    }
    return status_map.get(status.strip(), status)