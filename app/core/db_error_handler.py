"""
Database Error Handler Middleware

Catches database errors globally and converts them to proper HTTP responses
using ERROR_REGISTRY. This prevents database errors from crashing the backend.
"""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import (
    DatabaseError,
    DataError,
    DBAPIError,
    IntegrityError,
    InterfaceError,
    OperationalError,
    SQLAlchemyError,
)
from sqlalchemy.exc import TimeoutError as SQLTimeoutError
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.audit_logger import audit
from app.core.registries.error_registry import ERROR_REGISTRY


class DatabaseErrorMiddleware(BaseHTTPMiddleware):
    """
    Middleware to catch database errors and convert to proper HTTP responses.

    This prevents database errors from crashing the backend and provides
    consistent error responses to the frontend.
    """

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response

        except (OperationalError, InterfaceError, DBAPIError) as e:
            # Database connection errors, timeouts
            error_msg = str(e).lower()

            # Check if it's a timeout
            if "timeout" in error_msg or "timed out" in error_msg:
                entry = ERROR_REGISTRY["DB"]["ER_DB_501"]

                # Audit log the error
                try:
                    audit.error(
                        "DB",
                        "ER_DB_501",
                        request=request,
                        user_name="SYSTEM",
                        detail="Database timeout during request",
                    )
                except:
                    pass

                return JSONResponse(
                    status_code=entry["http_status"],
                    content={
                        "detail": {
                            "error": entry["error"],
                            "message": entry["message"],
                            "contacts": entry["contacts"],
                        }
                    },
                )

            # Generic connection error
            entry = ERROR_REGISTRY["DB"]["ER_DB_501"]

            # Audit log the error
            try:
                audit.error(
                    "DB",
                    "ER_DB_501",
                    request=request,
                    user_name="SYSTEM",
                    detail="Database connection failed",
                )
            except:
                pass

            return JSONResponse(
                status_code=entry["http_status"],
                content={
                    "detail": {
                        "error": entry["error"],
                        "message": entry["message"],
                        "contacts": entry["contacts"],
                    }
                },
            )

        except IntegrityError as e:
            # Constraint violations (unique, foreign key, etc.)
            error_msg = str(e).lower()

            # Check if it's a duplicate entry
            if "duplicate" in error_msg or "unique" in error_msg:
                entry = ERROR_REGISTRY["CLIENT"]["ER_CLIENT_2004"]

                # Audit log the error
                try:
                    audit.error(
                        "CLIENT",
                        "ER_CLIENT_2004",
                        request=request,
                        user_name="SYSTEM",
                        detail="Duplicate entry detected",
                    )
                except:
                    pass

                return JSONResponse(
                    status_code=entry["http_status"],
                    content={
                        "detail": {"error": entry["error"], "message": entry["message"]}
                    },
                )

            # Other integrity errors (foreign key, etc.)
            entry = ERROR_REGISTRY["DB"]["ER_DB_6061"]

            # Audit log the error
            try:
                audit.error(
                    "DB",
                    "ER_DB_6061",
                    request=request,
                    user_name="SYSTEM",
                    detail="Data integrity violation",
                )
            except:
                pass

            return JSONResponse(
                status_code=entry["http_status"],
                content={
                    "detail": {
                        "error": entry["error"],
                        "message": entry["message"],
                        "contacts": entry["contacts"],
                    }
                },
            )

        except (DatabaseError, DataError) as e:
            # Query errors, data type errors
            entry = ERROR_REGISTRY["DB"]["ER_DB_6060"]

            # Audit log the error
            try:
                audit.error(
                    "DB",
                    "ER_DB_6060",
                    request=request,
                    user_name="SYSTEM",
                    detail="Database query execution failed",
                )
            except:
                pass

            return JSONResponse(
                status_code=entry["http_status"],
                content={
                    "detail": {
                        "error": entry["error"],
                        "message": entry["message"],
                        "contacts": entry["contacts"],
                    }
                },
            )

        except SQLTimeoutError as e:
            # Explicit timeout errors
            entry = ERROR_REGISTRY["DB"]["ER_DB_501"]

            # Audit log the error
            try:
                audit.error(
                    "DB",
                    "ER_DB_501",
                    request=request,
                    user_name="SYSTEM",
                    detail="Database operation timeout",
                )
            except:
                pass

            return JSONResponse(
                status_code=entry["http_status"],
                content={
                    "detail": {
                        "error": entry["error"],
                        "message": entry["message"],
                        "contacts": entry["contacts"],
                    }
                },
            )

        except HTTPException:
            # Re-raise HTTP exceptions (already handled)
            raise

        except Exception as e:
            # Catch any other unexpected errors
            entry = ERROR_REGISTRY["BACKEND"]["ER_BACKEND_3001"]

            # Audit log the error
            try:
                audit.error(
                    "BACKEND",
                    "ER_BACKEND_3001",
                    request=request,
                    user_name="SYSTEM",
                    detail=f"Unexpected error: {str(e)[:100]}",
                )
            except:
                pass

            return JSONResponse(
                status_code=entry["http_status"],
                content={
                    "detail": {
                        "error": entry["error"],
                        "message": entry["message"],
                        "contacts": entry["contacts"],
                    }
                },
            )
