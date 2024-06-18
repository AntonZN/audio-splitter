from aioapns import APNs, NotificationRequest

from core.config import get_settings
from loguru import logger

settings = get_settings()


async def _send_to_apns(device_token: str, message):
    client_cert = settings.APNS_CERT

    if not client_cert:
        logger.debug("APNS CERT NOT SET")
        return

    apns = APNs(client_cert)

    request = NotificationRequest(
        device_token=device_token, message=message
    )

    await apns.send_notification(request)


async def processing_completed(device_token: str):
    message = {
        "aps": {
            "alert": "Обработка завершена",
            "badge": "1",
            "sound": "default",
        }
    }
    try:
        await _send_to_apns(device_token, message)
    except:
        pass
