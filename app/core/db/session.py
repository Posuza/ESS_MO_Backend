"""Database sessions — get_db dependency and get_session context manager."""

from __future__ import annotations

import os
import socket
from contextlib import contextmanager

from fastapi import HTTPException, status
from sqlalchemy.exc import DatabaseError, InterfaceError, OperationalError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db.engine import SessionLocal
from app.core.registries import (
    DATABASE_ERROR_CONNECTION_FAILED,
    DATABASE_ERROR_HOST_BLOCKED,
)


def _is_db_port_open(timeout: float = 0.3) -> bool:
    """Quick check to see if the database is reachable.

    - For SQLite: always returns True (local file, no server)
    - For MySQL:  TCP check against host:port
    """
    if settings.DB_ENGINE.lower() == "sqlite":
        return True
    host = settings.DB_HOST
    port = int(settings.DB_PORT)
    try:
        sock = socket.create_connection((host, port), timeout)
        sock.close()
        return True
    except Exception:
        return False


def _raise_db_error(error_msg: str = ""):
    """Map a DB connection error to the correct message and raise HTTPException."""
    msg_lower = error_msg.lower()
    if "1129" in msg_lower or "blocked" in msg_lower:
        detail = DATABASE_ERROR_HOST_BLOCKED
    else:
        detail = DATABASE_ERROR_CONNECTION_FAILED

    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=detail,
    )


def get_db():
    """FastAPI dependency for database session."""
    if not _is_db_port_open():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=DATABASE_ERROR_CONNECTION_FAILED,
        )

    try:
        db = SessionLocal()
    except (DatabaseError, OperationalError, InterfaceError) as e:
        _raise_db_error(str(e))

    try:
        yield db
    except (DatabaseError, OperationalError, InterfaceError) as e:
        _raise_db_error(str(e))
    finally:
        db.close()


@contextmanager
def get_session() -> Session:
    """Get a SQLAlchemy session with automatic cleanup."""
    if not _is_db_port_open():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=DATABASE_ERROR_CONNECTION_FAILED,
        )

    try:
        session = SessionLocal()
    except (DatabaseError, OperationalError, InterfaceError) as e:
        _raise_db_error(str(e))

    try:
        yield session
    except (DatabaseError, OperationalError, InterfaceError) as e:
        _raise_db_error(str(e))
    finally:
        session.close()
