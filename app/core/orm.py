"""SQLAlchemy engine/session setup for ORM-based modules."""
from __future__ import annotations

from contextlib import contextmanager
from urllib.parse import quote_plus

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.core.config import settings


def _build_database_url() -> str:
    engine = settings.DB_ENGINE.lower().strip()
    if engine == "sqlite":
        return f"sqlite:///{settings.SQLITE_PATH}"

    user = quote_plus(settings.DB_USER)
    password = quote_plus(settings.DB_PASSWORD)
    host = settings.DB_HOST
    port = settings.DB_PORT
    db_name = settings.DB_NAME
    return f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{db_name}"


DATABASE_URL = _build_database_url()
IS_SQLITE = settings.DB_ENGINE.lower().strip() == "sqlite"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=not IS_SQLITE,
    future=True,
    connect_args={"check_same_thread": False} if IS_SQLITE else {},
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
Base = declarative_base()


def get_db():
    """FastAPI dependency for database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_session() -> Session:
    """Get a SQLAlchemy session with automatic cleanup."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
