import requests

TOKEN = "8794081951:AAHriFzY5yj68sacN_JD4iuoZ4h8H3Su6TYI"
CHAT_ID = "6661035382"

def enviar(msg):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass
