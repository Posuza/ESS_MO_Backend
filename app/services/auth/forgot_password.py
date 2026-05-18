from app.core.orm import get_session
from app.models.employee import Employee
from app.services.email import send_plain_password_email
from fastapi import BackgroundTasks
from sqlalchemy import select


def send_reset_for_employee_code(
    employee_code: str,
    background_tasks: BackgroundTasks,
    send_plain_password: bool = False,
) -> dict:
    """Lookup employee by employee_code and enqueue an email with the plain password.
    Returns dict with status info: {
        "found": bool,
        "email_sent": bool,
        "reason": str (if not sent),
        "employee_name": str (if found),
        "email": str (if found)
    }
    """
    with get_session() as session:
        row = session.execute(
            select(Employee).where(Employee.employee_code == employee_code)
        ).scalar_one_or_none()

        if not row:
            return {
                "found": False,
                "email_sent": False,
                "reason": "Employee not found",
                "employee_name": None,
                "email": None,
            }

        # Check if employee is active
        if not row.is_active:
            return {
                "found": True,
                "email_sent": False,
                "reason": "Employee account is inactive",
                "employee_name": f"{row.first_name} {row.last_name}".strip()
                or row.employee_code,
                "email": row.email,
            }

        # Check if employee has email
        if not row.email:
            return {
                "found": True,
                "email_sent": False,
                "reason": "Employee has no email registered",
                "employee_name": f"{row.first_name} {row.last_name}".strip()
                or row.employee_code,
                "email": None,
            }

        name = f"{row.first_name} {row.last_name}".strip() or row.employee_code

        # We only support sending the plain password email in this deployment.
        background_tasks.add_task(
            send_plain_password_email, row.email, name, row.password, row.employee_code
        )

        return {
            "found": True,
            "email_sent": True,
            "reason": None,
            "employee_name": name,
            "email": row.email,
        }
