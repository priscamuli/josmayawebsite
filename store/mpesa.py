# store/mpesa.py
import requests
import base64
import datetime
from django.conf import settings

def get_access_token():
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    api_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"

    response = requests.get(api_URL, auth=(consumer_key, consumer_secret))
    return response.json()['access_token']

def lipa_na_mpesa(phone_number, amount):
    access_token = get_access_token()
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode((settings.MPESA_SHORTCODE + settings.MPESA_PASSKEY + timestamp).encode()).decode()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "BusinessShortCode": settings.MPESA_SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": settings.MPESA_SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.CALLBACK_URL,
        "AccountReference": "Ecommerce",
        "TransactionDesc": "Payment for goods"
    }

    response = requests.post(
        "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers=headers
    )

    return response.json()






CONSUMER_KEY = 'n5AjAa0aDxCwSTHATKgdhLQmwZH595G86afXdIfPUgqAim8T'
CONSUMER_SECRET = '0mqqkXWk9ff3E5EGa5gzcBg1bTQGPFfGZwATv5JGzG3XUIYPli61RKGfGt8IGqsZ'
BUSINESS_SHORTCODE = '174379'  # Example test paybill
PASSKEY = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'