import httpx

from app.config import settings

RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"


async def verify_captcha(token: str | None) -> bool:
    if not settings.CAPTCHA_ENABLED:
        return True
    if not token:
        return False
    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.post(
            RECAPTCHA_VERIFY_URL,
            data={"secret": settings.RECAPTCHA_SECRET_KEY, "response": token},
        )
    return resp.json().get("success", False)