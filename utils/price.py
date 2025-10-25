from config import foiz, kurs

def calculate_price(rate, api_id):
   if api_id == 1:
      price = rate * kurs * foiz
   else:
      price = rate * foiz 