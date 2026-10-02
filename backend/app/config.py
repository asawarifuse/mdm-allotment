from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "MDM Allotment"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    DATABASE_URL: str
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    CAPTCHA_ENABLED: bool = False
    RECAPTCHA_SITE_KEY: str = ""
    RECAPTCHA_SECRET_KEY: str = ""

    RATE_LIMIT_LOGIN: str = "5/minute"
    RATE_LIMIT_REGISTER: str = "3/minute"

    MAIN_ADMIN_ID: str
    MAIN_ADMIN_PASSWORD: str
    MAIN_ADMIN_NAME: str

    LOG_LEVEL: str = "INFO"
    SENTRY_DSN: str = ""


settings = Settings()