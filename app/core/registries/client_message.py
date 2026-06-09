from __future__ import annotations

from typing import Final

# =========================================================
# CLIENT — 4xx Client Errors
# =========================================================
CLIENT_ERROR_BAD_REQUEST: Final[str] = (
    "The request was malformed or invalid. Contact FE_DEV: fe-dev@gutsess.com"
)

CLIENT_ERROR_NOT_FOUND: Final[str] = (
    "The requested resource could not be found. Contact FE_DEV: fe-dev@gutsess.com"
)

CLIENT_ERROR_METHOD_NOT_ALLOWED: Final[str] = (
    "HTTP method not supported for this endpoint. Contact BE_DEV: be-dev@gutsess.com"
)

CLIENT_ERROR_CONFLICT: Final[str] = (
    "Resource conflict detected (e.g., duplicate entry). Contact BE_DEV: be-dev@gutsess.com"
)

CLIENT_ERROR_UNPROCESSABLE_ENTITY: Final[str] = (
    "Validation failed for the provided data. Contact BE_DEV: be-dev@gutsess.com"
)

CLIENT_ERROR_TOO_MANY_REQUESTS: Final[str] = (
    "Rate limit exceeded. Please try again later. Contact INFRA_CORE: infra@gutsess.com"
)

CLIENT_ERROR_GONE: Final[str] = (
    "Resource is no longer available at this address. Contact BE_DEV: be-dev@gutsess.com"
)

CLIENT_ERROR_LENGTH_REQUIRED: Final[str] = (
    "Content-Length header is missing. Contact BE_DEV: be-dev@gutsess.com"
)

CLIENT_ERROR_PRECONDITION_FAILED: Final[str] = (
    "Request headers do not meet server preconditions. Contact BE_DEV: be-dev@gutsess.com"
)

CLIENT_ERROR_PAYLOAD_TOO_LARGE: Final[str] = (
    "The request body exceeds size limits. Contact INFRA_CORE: infra@gutsess.com"
)

CLIENT_ERROR_URI_TOO_LONG: Final[str] = (
    "The request URI is too long. Contact FE_DEV: fe-dev@gutsess.com"
)

CLIENT_ERROR_UNSUPPORTED_MEDIA_TYPE: Final[str] = (
    "Unsupported media format provided. Contact BE_DEV: be-dev@gutsess.com"
)

CLIENT_ERROR_EXPECTATION_FAILED: Final[str] = (
    "Server cannot meet Expect header requirements. Contact BE_CORE: be-core@gutsess.com"
)

CLIENT_ERROR_MISDIRECTED_REQUEST: Final[str] = (
    "Request sent to a server unable to produce a response. Contact INFRA_CORE: infra@gutsess.com"
)

CLIENT_ERROR_LOCKED: Final[str] = (
    "The resource is currently locked. Contact BE_DEV: be-dev@gutsess.com"
)

CLIENT_ERROR_FAILED_DEPENDENCY: Final[str] = (
    "Request failed due to failure of a previous request. Contact BE_DEV: be-dev@gutsess.com"
)

CLIENT_ERROR_UPGRADE_REQUIRED: Final[str] = (
    "Please upgrade to a newer protocol. Contact SEC_OPS: sec-ops@gutsess.com"
)

CLIENT_ERROR_UNAVAILABLE_FOR_LEGAL_REASONS: Final[str] = (
    "Resource blocked for legal reasons. Contact LEGAL_OPS: legal@gutsess.com"
)
