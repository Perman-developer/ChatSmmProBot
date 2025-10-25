from utils.config_loader import get_config

# --- Configni o‘qish ---
_config = get_config()

# --- Bot ---
API_TOKEN = _config["bot"]["token"]
ADMIN_IDS = _config["bot"]["admin_id"]
ADMIN_ID = ADMIN_IDS[0]

KANAL = _config["bot"]["channel"]["username"]
KANAL_ID = _config["bot"]["channel"]["id"]

# --- To‘lov ---
KARTA = _config["payment"]["card"]
FIO = _config["payment"]["owner"]
min_pay = _config["payment"]["min"]
max_pay = _config["payment"]["max"]

# --- Valyuta / foizlar ---
kurs_rub= _config["currency"]["rate_rub"]
kurs_usd = _config["currency"]["rate_usd"]
# rubl kursi
foiz = _config["currency"]["percent"]       # foiz, misol: 1.2 = 120%

# --- Referral bonus ---
ref_bonus = _config["referral"]["bonus"]

# --- Topsmm API ---
def API_URL(api_id: str):
  url = _config["api"][api_id]["url"]
  key = _config["api"][api_id]["key"]
  return {"url": url, "key": key}


# --- Database fayllari ---
USERS_DB = _config["database"]["users"]
SERVICES_DB = _config["database"]["services"]
ORDERS_DB = _config["database"]["orders"]


# --- Timerlar ---
status_update_time = _config["timers"]["status_update"]      # sekundda
services_update_time = _config["timers"]["services_update"]  # sekundda