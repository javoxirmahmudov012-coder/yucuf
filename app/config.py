import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings:
    PROJECT_NAME: str = "UZRETRO.UZ — Video & Audio Kassetalarni Fleshka va Cloudga O'tkazish Xizmati"
    PROJECT_SLOGAN: str = "VIDEO KASSETA | FLESHKA | CLOUD | PREMIUM XIZMATLAR"

    # SECRET_KEY — ishlab chiqarishda albatta o'zgartiring!
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change_this_secret_key_in_production")

    # Ma'lumotlar bazasi (Vercel yoki Serverless muhitda /tmp ishlatiladi)
    if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
        DB_FILE: Path = Path("/tmp/kassetalar.db")
    else:
        DB_FILE: Path = BASE_DIR / "kassetalar.db"

    DATABASE_URL: str = f"sqlite+aiosqlite:///{DB_FILE.as_posix()}"

    # Yetkazib berish tariflari (so'mda)
    DELIVERY_TASHKENT_PRICE: int = int(os.getenv("DELIVERY_TASHKENT_PRICE", "25000"))
    DELIVERY_REGIONS_PRICE: int  = int(os.getenv("DELIVERY_REGIONS_PRICE",  "40000"))
    DELIVERY_EXPRESS_PRICE: int  = int(os.getenv("DELIVERY_EXPRESS_PRICE",  "45000"))
    FREE_DELIVERY_THRESHOLD: int = int(os.getenv("FREE_DELIVERY_THRESHOLD", "300000"))

    # Payme sozlamalari — .env orqali bering
    PAYME_MERCHANT_ID: str = os.getenv("PAYME_MERCHANT_ID", "")
    PAYME_KEY: str         = os.getenv("PAYME_KEY", "")
    PAYME_TEST_MODE: bool  = os.getenv("PAYME_TEST_MODE", "true").lower() == "true"

    # Click sozlamalari — .env orqali bering
    CLICK_SERVICE_ID:  str = os.getenv("CLICK_SERVICE_ID", "")
    CLICK_MERCHANT_ID: str = os.getenv("CLICK_MERCHANT_ID", "")
    CLICK_SECRET_KEY:  str = os.getenv("CLICK_SECRET_KEY", "")

    # Telegram Bot xabarnomalari — .env orqali bering
    TELEGRAM_BOT_TOKEN:     str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_ADMIN_CHAT_ID: str = os.getenv("TELEGRAM_ADMIN_CHAT_ID", "")

    # Sayt domenini (to'lov return_url uchun)
    SITE_URL: str = os.getenv("SITE_URL", "http://localhost:8000")

    # Admin kirish ma'lumotlari — .env orqali bering
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "change_this_password")

settings = Settings()
