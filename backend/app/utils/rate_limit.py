from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import settings

limiter = Limiter(key_func=get_remote_address)
LOGIN_LIMIT = settings.RATE_LIMIT_LOGIN
REGISTER_LIMIT = settings.RATE_LIMIT_REGISTER