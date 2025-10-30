from config import kurs_rub, kurs_usd, foiz

def CALCULATOR(api_id, rate, quantity):
    if api_id == 1:
        return round(quantity * kurs_rub * rate * foiz / 1000, 2)
    elif api_id == 4:
        return round(quantity * rate * foiz / 1000, 2)
    else:
        return round(quantity * kurs_usd * rate * foiz / 1000, 2)