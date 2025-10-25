import json
import os
import time

CONFIG_PATH = "database/config.json"

_cache = None
_cache_mtime = 0

def get_config() -> dict:
    """
    config.json faylni tezkor va xavfsiz o‘qish funksiyasi.
    - Fayl o‘zgarmasa, cache’dan o‘qiladi (tez ishlaydi)
    - Fayl yangilansa, avtomatik qayta yuklanadi
    """
    global _cache, _cache_mtime

    try:
        mtime = os.path.getmtime(CONFIG_PATH)
    except FileNotFoundError:
        raise FileNotFoundError(f"⚠️ {CONFIG_PATH} topilmadi")

    # agar fayl o‘zgarmagan bo‘lsa
    if _cache is not None and mtime == _cache_mtime:
        return _cache

    # aks holda faylni yangidan o‘qish
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        _cache = json.load(f)
        _cache_mtime = mtime
        return _cache


def update_config(updates: dict):
    """
    config.json faylini yangilash va cache-ni yangilash funksiyasi
    - updates -> yangilanishi kerak bo‘lgan kalit:qiymat juftliklari
    Misol:
        update_config({"currency": {"rate_rub": 160}})
    """
    global _cache, _cache_mtime

    # Avval configni o‘qiymiz (cache bilan)
    config = get_config()

    # Nested update funksiyasi
    def nested_update(d, u):
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                nested_update(d[k], v)
            else:
                d[k] = v

    # Configni yangilaymiz
    nested_update(config, updates)

    # Cache’ni yangilaymiz
    _cache = config

    # JSON faylga yozamiz
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    # Fayl modifikatsiyasini yangilaymiz
    _cache_mtime = os.path.getmtime(CONFIG_PATH)