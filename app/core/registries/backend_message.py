from __future__ import annotations

from typing import Final

# =========================================================
# BACKEND — 5xx Server Errors
# =========================================================
BACKEND_ERROR_INTERNAL: Final[str] = (
    "An unexpected internal server error occurred. Contact BE_CORE: be-core@gutsess.com"
)

BACKEND_ERROR_NOT_IMPLEMENTED: Final[str] = (
    "This feature is not yet implemented. Contact BE_CORE: be-core@gutsess.com"
)

BACKEND_ERROR_BAD_GATEWAY: Final[str] = (
    "Received an invalid response from the upstream server. Contact INFRA_CORE: infra@gutsess.com"
)

BACKEND_ERROR_SERVICE_UNAVAILABLE: Final[str] = (
    "Server is temporarily offline for maintenance. Contact INFRA_CORE: infra@gutsess.com"
)

BACKEND_ERROR_GATEWAY_TIMEOUT: Final[str] = (
    "Upstream server timed out. Contact INFRA_CORE: infra@gutsess.com"
)

BACKEND_ERROR_HTTP_VERSION_NOT_SUPPORTED: Final[str] = (
    "HTTP version used is not supported. Contact INFRA_CORE: infra@gutsess.com"
)

BACKEND_ERROR_VARIANT_ALSO_NEGOTIATES: Final[str] = (
    "Internal configuration error in content negotiation. Contact BE_CORE: be-core@gutsess.com"
)

BACKEND_ERROR_INSUFFICIENT_STORAGE: Final[str] = (
    "Server is out of storage space. Contact INFRA_CORE: infra@gutsess.com"
)

BACKEND_ERROR_LOOP_DETECTED: Final[str] = (
    "Infinite loop detected during processing. Contact BE_CORE: be-core@gutsess.com"
)
