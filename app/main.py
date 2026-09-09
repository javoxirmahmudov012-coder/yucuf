from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import logging

from app.config import settings
from app.database import engine, Base, AsyncSessionLocal
from app.services.seed_data import seed_database
from app.routers.store import router as store_router
from app.routers.api import router as api_router
from app.routers.admin import router as admin_router
from app.routers.payme import router as payme_router
from app.routers.click_pay import router as click_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kassetalar_app")

BASE_DIR = Path(__file__).resolve().parent

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Baza jadvallarini yaratish
    logger.info("Ma'lumotlar bazasi jadvallari yaratilmoqda...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # 2. Boshlang'ich kassetalar va ma'lumotlarni to'ldirish
    logger.info("Boshlang'ich kassetalar to'plami tekshirilmoqda...")
    async with AsyncSessionLocal() as session:
        await seed_database(session)
        
    logger.info("✅ Kassetalar onlayn do'koni to'liq tayyor!")
    yield
    # Shutdown
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Retro & Zamonaviy Audio Kassetalar Onlayn Do'koni",
    version="1.0.0",
    lifespan=lifespan
)

# Static fayllarni ulash
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Routerlarni ro'yxatdan o'tkazish
app.include_router(store_router)
app.include_router(api_router)
app.include_router(admin_router)
app.include_router(payme_router)
app.include_router(click_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
