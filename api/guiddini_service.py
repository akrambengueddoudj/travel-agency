import requests
from django.conf import settings

BASE_URL = 'https://epay.guiddini.dz/api'

def initiate_payment(amount):
    url = f'{BASE_URL}/payment/initiate'
    APP_KEY = settings.GUIDDINI_APP_KEY
    APP_SECRET = settings.GUIDDINI_SECRET_KEY
    print(f"{APP_KEY}  ----  {APP_SECRET}")
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'x-app-key': APP_KEY,
        'x-app-secret': APP_SECRET,
    }
    resp = requests.post(url, json={'amount': str(amount)}, headers=headers)
    resp.raise_for_status()
    return resp.json()

def show_transaction(order_number):
    url = f'{BASE_URL}/payment/show'
    APP_KEY = settings.GUIDDINI_APP_KEY
    APP_SECRET = settings.GUIDDINI_SECRET_KEY
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'x-app-key': APP_KEY,
        'x-app-secret': APP_SECRET,
    }
    resp = requests.get(url, json={'order_number': order_number}, headers=headers)
    resp.raise_for_status()
    return resp.json()['data']['attributes']
