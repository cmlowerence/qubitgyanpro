# qubitgyanpro/services/telegram_service.py

import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

TELEGRAM_API_URL = "https://api.telegram.org"


class TelegramServiceError(Exception):
    pass


def send_message(telegram_id: str, text: str, parse_mode: str = "HTML") -> dict:
    bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)

    if not bot_token:
        logger.error("Telegram bot token missing in settings.")
        raise TelegramServiceError("Telegram service not configured.")

    if not telegram_id or not text:
        raise TelegramServiceError("Invalid telegram_id or message.")

    if parse_mode not in ("HTML", "MarkdownV2"):
        raise TelegramServiceError("Invalid parse_mode.")

    url = f"{TELEGRAM_API_URL}/bot{bot_token}/sendMessage"

    payload = {
        "chat_id": str(telegram_id),
        "text": text,
        "parse_mode": parse_mode
    }

    try:
        response = requests.post(
            url,
            json=payload,
            timeout=(3.0, 5.0)  # connect, read
        )
        response.raise_for_status()

        try:
            data = response.json()
        except ValueError:
            logger.error(f"Invalid JSON response from Telegram for chat_id={telegram_id}")
            raise TelegramServiceError("Invalid response from Telegram.")

        if not data.get("ok"):
            description = data.get("description", "Unknown error")
            logger.error(f"Telegram API error for chat_id={telegram_id}: {description}")
            raise TelegramServiceError("Failed to send message via Telegram.")

        return data

    except requests.exceptions.Timeout:
        logger.error(f"Telegram timeout for chat_id={telegram_id}")
        raise TelegramServiceError("Telegram timeout. Try again later.")

    except requests.exceptions.ConnectionError:
        logger.error(f"Telegram connection error for chat_id={telegram_id}")
        raise TelegramServiceError("Unable to connect to Telegram.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Telegram request failed for chat_id={telegram_id}: {str(e)}")
        raise TelegramServiceError("Telegram request failed.")