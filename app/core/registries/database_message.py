from __future__ import annotations

from typing import Final

# =========================================================
# DB — Connection
# =========================================================
DATABASE_ERROR_CONNECTION_FAILED: Final[str] = (
    "Database connection timeout. Contact: db-dev@gutsess.com"
)

DATABASE_ERROR_HOST_BLOCKED: Final[str] = (
    "Database host is temporarily blocked due to connection errors. please contact your database administrator."
)


# =========================================================
# DB — Query
# =========================================================
DATABASE_ERROR_QUERY_ERROR: Final[str] = (
    "Database query execution failed. Contact: db-dev@gutsess.com"
)


# =========================================================
# DB — Data integrity
# =========================================================
DATABASE_ERROR_DATA_CORRUPTION: Final[str] = (
    "Data integrity check failed. Contact: db-dev@gutsess.com"
)
