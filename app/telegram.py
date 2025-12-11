import requests

def send_telegram_message(message):
    bot_token = "8435317212:AAGJYyLfUieqo_qJkhQINloVIHrdoXqPIPg"
    chat_id = "8400523725"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": message})
