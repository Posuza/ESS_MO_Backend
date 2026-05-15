from __future__ import annotations

from contextlib import contextmanager
from urllib.parse import quote_plus

from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.exc import DatabaseError, InterfaceError, OperationalError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import settings
from app.core.registries.error_registry import ERROR_REGISTRY


def _build_database_url() -> str:
    """Build a MySQL database URL from settings.

    This project uses MySQL (mysql-connector) exclusively.
    """
    user = quote_plus(settings.DB_USER)
    password = quote_plus(settings.DB_PASSWORD)
    host = settings.DB_HOST
    port = settings.DB_PORT
    db_name = settings.DB_NAME
    return f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db_name}"


DATABASE_URL = _build_database_url()

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
    connect_args={"connect_timeout": 3},
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
Base = declarative_base()


import socket
import os

def _is_db_port_open(timeout: float = 0.3) -> bool:
    """Quick TCP check to see if the DB host:port is reachable."""
    host = settings.DB_HOST
    port = int(settings.DB_PORT)
    try:
        sock = socket.create_connection((host, port), timeout)
        sock.close()
        return True
    except Exception:
        return False


def _raise_db_error(error_msg: str = ""):
    """Map a DB connection error to the correct registry entry and raise HTTPException."""
    msg_lower = error_msg.lower()
    if "1129" in msg_lower or "blocked" in msg_lower:
        entry = ERROR_REGISTRY["DB"]["ER_DB_502"]
    else:
        entry = ERROR_REGISTRY["DB"]["ER_DB_501"]

    raise HTTPException(
        status_code=entry["http_status"],
        detail={
            "error": entry["error"],
            "message": entry["message"],
            "contacts": entry.get("contacts", []),
        },
    )


def get_db():
    """FastAPI dependency for database session."""
    if not _is_db_port_open():
        entry = ERROR_REGISTRY["DB"]["ER_DB_501"]
        raise HTTPException(
            status_code=entry["http_status"],
            detail={
                "error": entry["error"],
                "message": entry["message"],
                "contacts": entry.get("contacts", []),
            },
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
        entry = ERROR_REGISTRY["DB"]["ER_DB_501"]
        raise HTTPException(
            status_code=entry["http_status"],
            detail={
                "error": entry["error"],
                "message": entry["message"],
                "contacts": entry.get("contacts", []),
            },
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

