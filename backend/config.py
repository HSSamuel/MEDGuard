import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    # App
    APP_NAME: str = "MedGuard"
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    # Added a default fallback key for local development
    SECRET_KEY: str = os.getenv("SECRET_KEY", "a-super-secret-key-for-dev")
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "5000"))

    # Database
    DB_PATH: Path = Path(os.getenv("DB_PATH", BASE_DIR / "medguard.db"))

    # Security (QR signing, etc.)
    QR_SIGNING_SECRET: str = os.getenv(
        "QR_SIGNING_SECRET", "sign-me-in-prod")

    # CORS
    CORS_ORIGINS: list = os.getenv(
        "CORS_ORIGINS", "*").split(",")

    # Paths for frontend
    TEMPLATES_DIR: Path = BASE_DIR / "frontend" / "templates"
    STATIC_DIR: Path = BASE_DIR / "frontend" / "static"

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Twilio (for SMS functionality)
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
    TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
    
    # Comprehensive Database of NAFDAC-registered drugs is through the EMDEX API (api.emdex.org).
    EMDEX_API_KEY = os.getenv("EMDEX_API_KEY", "your_default_key_for_dev")


class ProdConfig(Config):
    DEBUG = False
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "https://your-domain.com").split(",")
    # In production, SECRET_KEY should always be set as an environment variable
    SECRET_KEY = os.getenv("SECRET_KEY")


def get_config():
    env = os.getenv("ENV", "dev").lower()
    if env in ("prod", "production"):
        return ProdConfig()
    return Config()