from fastapi import APIRouter

from .auth import router as auth_router
from .mo_daily_transactions import router as mo_daily_transactions_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(
    mo_daily_transactions_router,
    prefix="/mo-daily-transactions",
    tags=["mo_daily_transactions"],
)
