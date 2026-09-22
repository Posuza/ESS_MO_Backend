from __future__ import annotations

from typing import Final

# =========================================================
# FACE — Audit action messages
# =========================================================
FACE_LOGIN_LOOKUP_ATTEMPT: Final[str] = (
    "Face login profile lookup attempt: employee_code={employee_code}"
)
FACE_LOGIN_LOOKUP_SUCCESS: Final[str] = (
    "Face login profile lookup success: employee_code={employee_code}, "
    "has_face_profile={has_face_profile}"
)
FACE_LOGIN_LOOKUP_FAILED: Final[str] = (
    "Face login profile lookup failed: employee_code={employee_code}, reason={reason}"
)
FACE_LOGIN_SCAN_ATTEMPT: Final[str] = (
    "Face login scan verification attempt: employee_code={employee_code}"
)
FACE_LOGIN_SCAN_SUCCESS: Final[str] = (
    "Face login scan verification success: employee_code={employee_code}, "
    "score={score}, threshold={threshold}"
)
FACE_LOGIN_SCAN_NOT_MATCH: Final[str] = (
    "Face login scan verification not matched: employee_code={employee_code}, "
    "score={score}, threshold={threshold}"
)
FACE_LOGIN_SCAN_FAILED: Final[str] = (
    "Face login scan verification failed: employee_code={employee_code}, reason={reason}"
)
FACE_LOGIN_SESSION_ATTEMPT: Final[str] = (
    "Face login session attempt: employee_code={employee_code}"
)
FACE_LOGIN_SESSION_SUCCESS: Final[str] = (
    "Face login session success: employee_code={employee_code}"
)
FACE_LOGIN_SESSION_FAILED: Final[str] = (
    "Face login session failed: employee_code={employee_code}, reason={reason}"
)
FORGOT_PASSWORD_FACE_SCAN_ATTEMPT: Final[str] = (
    "Forgot-password face scan attempt: employee_code={employee_code}"
)
FORGOT_PASSWORD_FACE_SCAN_SUCCESS: Final[str] = (
    "Forgot-password face scan success: employee_code={employee_code}, "
    "score={score}, threshold={threshold}"
)
FORGOT_PASSWORD_FACE_SCAN_NOT_MATCH: Final[str] = (
    "Forgot-password face scan not matched: employee_code={employee_code}, "
    "score={score}, threshold={threshold}"
)
FORGOT_PASSWORD_FACE_SCAN_FAILED: Final[str] = (
    "Forgot-password face scan failed: employee_code={employee_code}, reason={reason}"
)
FACE_VERIFY_ATTEMPT: Final[str] = (
    "Face verification attempt: employee_code={employee_code}"
)

FACE_VERIFY_SUCCESS: Final[str] = (
    "Face verification success: employee_code={employee_code}, "
    "score={score}, threshold={threshold}"
)

FACE_VERIFY_FAILED: Final[str] = (
    "Face verification failed: employee_code={employee_code}, reason={reason}"
)

FACE_VERIFY_NOT_MATCH: Final[str] = (
    "Face verification not matched: employee_code={employee_code}, "
    "score={score}, threshold={threshold}"
)

FACE_REGISTER_ATTEMPT: Final[str] = (
    "Face registration attempt: employee_code={employee_code}, actor={actor}"
)

FACE_REGISTER_SUCCESS: Final[str] = (
    "Face registration success: employee_code={employee_code}, actor={actor}, "
    "image_path={image_path}"
)

FACE_REGISTER_FAILED: Final[str] = (
    "Face registration failed: employee_code={employee_code}, actor={actor}, "
    "reason={reason}"
)
