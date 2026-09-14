from __future__ import annotations

from typing import Final

# =========================================================
# FACE — Audit action messages
# =========================================================
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
