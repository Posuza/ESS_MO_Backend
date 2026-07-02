from __future__ import annotations

from typing import Final

# =========================================================
# AUTH — Errors
# =========================================================
AUTH_ERROR_UNAUTHORIZED: Final[str] = (
    "จำเป็นต้องยืนยันตัวตน โปรดเข้าสู่ระบบ. Plase contact to GutsEssCenter"
)

AUTH_ERROR_FORBIDDEN: Final[str] = (
    "Access denied. Insufficient permissions. Plase contact to GutsEssCenter"
)

AUTH_ERROR_TOKEN_EXPIRED: Final[str] = (
    "Session expired. Please refresh your token. Plase contact to GutsEssCenter"
)

AUTH_ERROR_PROXY_AUTH_REQUIRED: Final[str] = (
    "Proxy authentication required. Plase contact to GutsEssCenter"
)

AUTH_ERROR_NETWORK_AUTH_REQUIRED: Final[str] = (
    "Network authentication required to gain access. Plase contact to GutsEssCenter"
)

AUTH_ERROR_INVALID_CREDENTIALS: Final[str] = "รหัสผ่านไม่ถูกต้อง"

AUTH_ERROR_INVALID_OLD_PASSWORD: Final[str] = "รหัสผ่านล่าสุดไม่ถูกต้อง"

AUTH_ERROR_ACCOUNT_INACTIVE: Final[str] = (
    "Account is inactive. Please contact administrator. Plase contact to GutsEssCenter"
)

AUTH_ERROR_ACCOUNT_INACTIVE_FORGOT_PASSWORD: Final[str] = (
    "Employee account is inactive. Please contact Human Resources. "
    "Plase contact to GutsEssCenter"
)

AUTH_ERROR_ACCOUNT_LOCKED: Final[str] = (
    "Account is locked due to multiple failed login attempts. "
    "Plase contact to GutsEssCenter"
)

AUTH_ERROR_EMPLOYEE_NOT_FOUND: Final[str] = (
    "ไม่พบรหัสพนักงานในระบบ โปรดติดต่อฝ่ายทรัพยากรบุคคล."
)

AUTH_ERROR_NO_EMAIL_REGISTERED: Final[str] = (
    "ไม่พบอีเมลที่ลงทะเบียนไว้สำหรับรหัสพนักงานนี้ "
    "โปรดติดต่อฝ่ายทรัพยากรบุคคล. "
    "Plase contact to GutsEssCenter"
)


# =========================================================
# AUTH — Audit action messages
#   Usage: audit_logger.log(action=LOGIN_SUCCESS)
# =========================================================
LOGIN_ATTEMPT: Final[str] = "{resource} Attempt to Login"
LOGIN_FAILED: Final[str] = "{resource} Login attempt failed"
LOGIN_FAILED_REASON: Final[str] = "{resource} Login attempt failed - {reason}"
LOGIN_SUCCESS: Final[str] = "{resource} Login successful"
LOGOUT_ATTEMPT: Final[str] = "{resource} Attempt to Logout"
LOGOUT_FAILED: Final[str] = "{resource} Logout failed"
LOGOUT_SUCCESS: Final[str] = "{resource} Logout successful"
FORGOT_PASSWORD_ATTEMPT: Final[str] = "{resource} attempted forgot-password request"
FORGOT_PASSWORD_FAILED: Final[str] = (
    "{resource} Forgot-password request failed - {reason}"
)
FORGOT_PASSWORD_EMAIL_SENT: Final[str] = (
    "{resource} Password reset email sent successfully to {email}"
)
CHANGE_PASSWORD_ATTEMPT: Final[str] = "{resource} attempted to change password"
CHANGE_PASSWORD_SUCCESS: Final[str] = "{resource} changed password successfully"
RESET_PASSWORD_SUCCESS: Final[str] = "Password reset successful"
ACCOUNT_LOCKED: Final[str] = "Account locked after repeated failures"
REGISTER: Final[str] = "{resource} registered successfully (code={employee_code})"


# =========================================================
# AUTH — Dependencies (role & permission checks)
# =========================================================
ACCESS_DENIED_ROLE: Final[str] = "Access denied: insufficient role"
ACCESS_DENIED_PERMISSION: Final[str] = "Access denied: insufficient permissions"
EMPLOYEE_NOT_FOUND: Final[str] = "Employee not found"
ACCOUNT_INACTIVE: Final[str] = "Account is inactive"
