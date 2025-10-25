import re


#============================================================================================
# 🔗 Linkni tekshirish
#============================================================================================
def CHECK_SOCIAL_LINK(link: str) -> bool:
    link = link.lower().strip()
    patterns = [
        r'^(https?://)?(t\.me|telegram\.me)/.+',
        r'^(https?://)?(www\.)?instagram\.com/.+',
        r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+',
        r'^(https?://)?(www\.)?tiktok\.com/.+'
    ]
    return any(re.match(pattern, link) for pattern in patterns)
#============================================================================================