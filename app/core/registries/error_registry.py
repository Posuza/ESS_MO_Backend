"""
ERROR_REGISTRY — structured HTTP error catalogue.

Each entry carries:
  code        — internal numeric error code
  http_status — HTTP status code to return
  message     — human-readable description
  contacts    — numbered dict of responsible contacts, each with:
                  role  : team / role name
                  email : contact email

Usage
-----
from app.core.registries import ERROR_REGISTRY

entry = ERROR_REGISTRY["CLIENT"]["NOT_FOUND"]
raise HTTPException(status_code=entry["http_status"], detail=entry["message"])
# Escalate: entry["contacts"][1]["role"], entry["contacts"][1]["email"]
"""

from __future__ import annotations

ERROR_REGISTRY: dict[str, dict[str, dict]] = {
    "AUTH": {
        "ER_AUTH_1001": {"http_status": 401, "error": "UNAUTHORIZED", "message": "Authentication required. Please log in.", "contacts": [{"team": "SEC_OPS", "email": "sec-ops@gutsess.com"}]},
        "ER_AUTH_1002": {"http_status": 403, "error": "FORBIDDEN", "message": "Access denied. Insufficient permissions.", "contacts": [{"team": "SEC_OPS", "email": "sec-ops@gutsess.com"}]},
        "ER_AUTH_1003": {"http_status": 401, "error": "TOKEN_EXPIRED", "message": "Session expired. Please refresh your token.", "contacts": [{"team": "SEC_OPS", "email": "sec-ops@gutsess.com"}]},
        "ER_AUTH_1004": {"http_status": 407, "error": "PROXY_AUTH_REQUIRED", "message": "Proxy authentication required.", "contacts": [{"team": "INFRA_CORE", "email": "infra@gutsess.com"}]},
        "ER_AUTH_1005": {"http_status": 511, "error": "NETWORK_AUTH_REQUIRED", "message": "Network authentication required to gain access.", "contacts": [{"team": "INFRA_CORE", "email": "infra@gutsess.com"}]},
        "ER_AUTH_1006": {"http_status": 401, "error": "INVALID_CREDENTIALS", "message": "Incorrect employee code or password.", "contacts": [{"team": "SEC_OPS", "email": "sec-ops@gutsess.com"}]},
        "ER_AUTH_1007": {"http_status": 403, "error": "ACCOUNT_INACTIVE", "message": "Account is inactive. Please contact administrator.", "contacts": [{"team": "SEC_OPS", "email": "sec-ops@gutsess.com"}]},
        "ER_AUTH_1008": {"http_status": 403, "error": "ACCOUNT_LOCKED", "message": "Account is locked due to multiple failed login attempts.", "contacts": [{"team": "SEC_OPS", "email": "sec-ops@gutsess.com"}]},
        "ER_AUTH_1009": {"http_status": 404, "error": "EMPLOYEE_NOT_FOUND", "message": "ไม่พบรหัสพนักงานในระบบ กรุณาติดต่อฝ่ายบุคคล", "contacts": [{"team": "HR_OPS", "email": "hr@gutsess.com"}]},
        "ER_AUTH_1010": {"http_status": 403, "error": "ACCOUNT_INACTIVE_FORGOT_PASSWORD", "message": "บัญชีพนักงานไม่ได้ใช้งาน กรุณาติดต่อฝ่ายบุคคล", "contacts": [{"team": "HR_OPS", "email": "hr@gutsess.com"}]},
        "ER_AUTH_1011": {"http_status": 400, "error": "NO_EMAIL_REGISTERED", "message": "ไม่พบอีเมลที่ลงทะเบียนไว้ กรุณาติดต่อฝ่ายบุคคล", "contacts": [{"team": "HR_OPS", "email": "hr@gutsess.com"}]},
    },
    "CLIENT": {
        "ER_CLIENT_2001": {"http_status": 400, "error": "BAD_REQUEST", "message": "The request was malformed or invalid.", "contacts": [{"team": "FE_DEV", "email": "fe-dev@gutsess.com"}]},
        "ER_CLIENT_2002": {"http_status": 404, "error": "NOT_FOUND", "message": "The requested resource could not be found.", "contacts": [{"team": "FE_DEV", "email": "fe-dev@gutsess.com"}]},
        "ER_CLIENT_2003": {"http_status": 405, "error": "METHOD_NOT_ALLOWED", "message": "HTTP method not supported for this endpoint.", "contacts": [{"team": "BE_DEV", "email": "be-dev@gutsess.com"}]},
        "ER_CLIENT_2004": {"http_status": 409, "error": "CONFLICT", "message": "Resource conflict detected (e.g., duplicate entry).", "contacts": [{"team": "BE_DEV", "email": "be-dev@gutsess.com"}]},
        "ER_CLIENT_2005": {"http_status": 422, "error": "UNPROCESSABLE_ENTITY", "message": "Validation failed for the provided data.", "contacts": [{"team": "BE_DEV", "email": "be-dev@gutsess.com"}]},
        "ER_CLIENT_2006": {"http_status": 429, "error": "TOO_MANY_REQUESTS", "message": "Rate limit exceeded. Please try again later.", "contacts": [{"team": "INFRA_CORE", "email": "infra@gutsess.com"}]},
        "ER_CLIENT_2007": {"http_status": 410, "error": "GONE", "message": "Resource is no longer available at this address.", "contacts": [{"team": "BE_DEV", "email": "be-dev@gutsess.com"}]},
        "ER_CLIENT_2008": {"http_status": 411, "error": "LENGTH_REQUIRED", "message": "Content-Length header is missing.", "contacts": [{"team": "BE_DEV", "email": "be-dev@gutsess.com"}]},
        "ER_CLIENT_2009": {"http_status": 412, "error": "PRECONDITION_FAILED", "message": "Request headers do not meet server preconditions.", "contacts": [{"team": "BE_DEV", "email": "be-dev@gutsess.com"}]},
        "ER_CLIENT_2010": {"http_status": 413, "error": "PAYLOAD_TOO_LARGE", "message": "The request body exceeds size limits.", "contacts": [{"team": "INFRA_CORE", "email": "infra@gutsess.com"}]},
        "ER_CLIENT_2011": {"http_status": 414, "error": "URI_TOO_LONG", "message": "The request URI is too long.", "contacts": [{"team": "FE_DEV", "email": "fe-dev@gutsess.com"}]},
        "ER_CLIENT_2012": {"http_status": 415, "error": "UNSUPPORTED_MEDIA_TYPE", "message": "Unsupported media format provided.", "contacts": [{"team": "BE_DEV", "email": "be-dev@gutsess.com"}]},
        "ER_CLIENT_2013": {"http_status": 417, "error": "EXPECTATION_FAILED", "message": "Server cannot meet Expect header requirements.", "contacts": [{"team": "BE_CORE", "email": "be-core@gutsess.com"}]},
        "ER_CLIENT_2014": {"http_status": 421, "error": "MISDIRECTED_REQUEST", "message": "Request sent to a server unable to produce a response.", "contacts": [{"team": "INFRA_CORE", "email": "infra@gutsess.com"}]},
        "ER_CLIENT_2015": {"http_status": 423, "error": "LOCKED", "message": "The resource is currently locked.", "contacts": [{"team": "BE_DEV", "email": "be-dev@gutsess.com"}]},
        "ER_CLIENT_2016": {"http_status": 424, "error": "FAILED_DEPENDENCY", "message": "Request failed due to failure of a previous request.", "contacts": [{"team": "BE_DEV", "email": "be-dev@gutsess.com"}]},
        "ER_CLIENT_2017": {"http_status": 426, "error": "UPGRADE_REQUIRED", "message": "Please upgrade to a newer protocol.", "contacts": [{"team": "SEC_OPS", "email": "sec-ops@gutsess.com"}]},
        "ER_CLIENT_2018": {"http_status": 451, "error": "UNAVAILABLE_FOR_LEGAL_REASONS", "message": "Resource blocked for legal reasons.", "contacts": [{"team": "LEGAL_OPS", "email": "legal@gutsess.com"}]},
    },
    "BACKEND": {
        "ER_BACKEND_3001": {"http_status": 500, "error": "INTERNAL_ERROR", "message": "An unexpected internal server error occurred.", "contacts": [{"team": "BE_CORE", "email": "be-core@gutsess.com"}]},
        "ER_BACKEND_3002": {"http_status": 501, "error": "NOT_IMPLEMENTED", "message": "This feature is not yet implemented.", "contacts": [{"team": "BE_CORE", "email": "be-core@gutsess.com"}]},
        "ER_BACKEND_3003": {"http_status": 502, "error": "BAD_GATEWAY", "message": "Received an invalid response from the upstream server.", "contacts": [{"team": "INFRA_CORE", "email": "infra@gutsess.com"}]},
        "ER_BACKEND_3004": {"http_status": 503, "error": "SERVICE_UNAVAILABLE", "message": "Server is temporarily offline for maintenance.", "contacts": [{"team": "INFRA_CORE", "email": "infra@gutsess.com"}]},
        "ER_BACKEND_3005": {"http_status": 504, "error": "GATEWAY_TIMEOUT", "message": "Upstream server timed out.", "contacts": [{"team": "INFRA_CORE", "email": "infra@gutsess.com"}]},
        "ER_BACKEND_3006": {"http_status": 505, "error": "HTTP_VERSION_NOT_SUPPORTED", "message": "HTTP version used is not supported.", "contacts": [{"team": "INFRA_CORE", "email": "infra@gutsess.com"}]},
        "ER_BACKEND_3007": {"http_status": 506, "error": "VARIANT_ALSO_NEGOTIATES", "message": "Internal configuration error in content negotiation.", "contacts": [{"team": "BE_CORE", "email": "be-core@gutsess.com"}]},
        "ER_BACKEND_3008": {"http_status": 507, "error": "INSUFFICIENT_STORAGE", "message": "Server is out of storage space.", "contacts": [{"team": "INFRA_CORE", "email": "infra@gutsess.com"}]},
        "ER_BACKEND_3009": {"http_status": 508, "error": "LOOP_DETECTED", "message": "Infinite loop detected during processing.", "contacts": [{"team": "BE_CORE", "email": "be-core@gutsess.com"}]},
    },
    "DB": {
        "ER_DB_501": {"http_status": 504, "error": "CONNECT_FAIL", "message": "Database connection timeout.", "contacts": [{"team": "DB_ADMIN", "email": "db-admin@gutsess.com"}]},
        "ER_DB_6060": {"http_status": 500, "error": "QUERY_ERROR", "message": "Database query execution failed.", "contacts": [{"team": "DB_DEV", "email": "db-dev@gutsess.com"}]},
        "ER_DB_6061": {"http_status": 500, "error": "DATA_CORRUPTION", "message": "Data integrity check failed.", "contacts": [{"team": "DB_ADMIN", "email": "db-admin@gutsess.com"}]},
    },
    "PAYMENT": {
        "ER_PAYMENT_7001": {"http_status": 402, "error": "PAYMENT_REQUIRED", "message": "Payment is required to access this resource.", "contacts": [{"team": "BILLING_BE", "email": "billing@gutsess.com"}]},
    },
}
