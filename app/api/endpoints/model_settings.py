from __future__ import annotations

from fastapi import APIRouter

from app.core.model_settings import get_frontend_model_settings

router = APIRouter()


@router.get("/frontend")
def frontend_model_settings(mode: str | None = None):
    return get_frontend_model_settings(mode)
