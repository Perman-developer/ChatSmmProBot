from datetime import datetime, timedelta


# 🕓 Toshkent vaqti funksiyasi
def TASHKENT_TIME():
    return (datetime.utcnow() + timedelta(hours=5)).strftime("%Y-%m-%d %H:%M:%S")
