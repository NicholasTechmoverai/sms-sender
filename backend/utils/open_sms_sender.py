import requests
import json
from fastapi import HTTPException
from core.logger import setup_logger
from core.settings import settings

logger = setup_logger(__name__)

# OpenSMS API token
API_TOKEN = settings.OPENSMS_API_TOKEN


async def send_sms(recipient, message,sender_id="OPENSMS", type="plain", schedule_time=None):
    """
    Send an SMS via OpenSMS API
    :param recipient: str, phone number(s) in international format, comma-separated for multiple
    :param sender_id: str, max 11 characters (alphanumeric or phone number)
    :param message: str, text of the message
    :param schedule_time: str, optional, RFC3339 format e.g. "2026-03-11 18:30"
    """
    API_URL = "https://opensms.co.ke/api/v3/sms/send"

    payload = {
        "recipient": recipient,
        "sender_id": sender_id,
        "type": type,
        "message": message,
    }

    if schedule_time:
        payload["schedule_time"] = schedule_time

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        logger.info(f"SMS request sent for {recipient} and message: {message}")

        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=f"Failed to send SMS: {e}")



async def get_sms_balance(api_key: str = API_TOKEN):
    API_URL = "https://opensms.co.ke/api/v3/balance"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.get(API_URL, headers=headers, timeout=10)
        response.raise_for_status()

        data = response.json()
        return data.get("data")  # returns sms unit details

    except requests.exceptions.RequestException as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=f"Failed to fetch SMS balance: {e}")