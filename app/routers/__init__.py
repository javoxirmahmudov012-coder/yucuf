from app.routers.store import router as store_router
from app.routers.api import router as api_router
from app.routers.admin import router as admin_router
from app.routers.payme import router as payme_router
from app.routers.click_pay import router as click_router

__all__ = [
    "store_router",
    "api_router",
    "admin_router",
    "payme_router",
    "click_router"
]
