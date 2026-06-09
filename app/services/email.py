import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

_logger = logging.getLogger(__name__)

SMTP_TIMEOUT = 10  # seconds


def _build_message(
    to_email: str,
    email_from: str,
    subject: str,
    text_body: str,
    html_body: str,
) -> MIMEMultipart:
    """Build a multipart email message with plain text and HTML alternatives."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = email_from
    msg["To"] = to_email
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))
    return msg


def _send_email(
    to_email: str,
    subject: str,
    text_body: str,
    html_body: str,
) -> bool:
    """Low-level SMTP send. Returns True on success, False on failure."""
    smtp_host = settings.SMTP_HOST
    smtp_port = settings.SMTP_PORT
    smtp_user = settings.SMTP_USER
    smtp_pass = settings.SMTP_PASS
    email_from = settings.EMAIL_FROM or smtp_user

    if not smtp_host or not smtp_port:
        _logger.error(
            "SMTP not configured (SMTP_HOST=%s, SMTP_PORT=%s)", smtp_host, smtp_port
        )
        return False

    msg = _build_message(to_email, email_from, subject, text_body, html_body)

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=SMTP_TIMEOUT) as server:
            server.ehlo()
            server.starttls()
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
            server.sendmail(email_from, to_email, msg.as_string())
        return True
    except smtplib.SMTPAuthenticationError:
        _logger.error("SMTP authentication failed for user=%s", smtp_user)
    except smtplib.SMTPConnectError:
        _logger.error("SMTP connection refused %s:%s", smtp_host, smtp_port)
    except smtplib.SMTPException as exc:
        _logger.error("SMTP error: %s", exc)
    except TimeoutError:
        _logger.error(
            "SMTP timeout after %ss connecting to %s:%s",
            SMTP_TIMEOUT,
            smtp_host,
            smtp_port,
        )
    except OSError as exc:
        _logger.error("SMTP network error: %s", exc)
    return False


def send_plain_password_email(
    to_email: str, employee_name: str, password: str, employee_id: str | None = None
) -> bool:
    """
    Send plain password via email (legacy/insecure method).

    WARNING: This is insecure. Only use for backwards compatibility.

    Returns True if the email was sent successfully, False otherwise.
    """
    emp_id_text = f"รหัสพนักงาน: {employee_id}\n\n" if employee_id else ""
    emp_id_html = (
        f"<p><strong>รหัสพนักงาน:</strong> {employee_id}</p>" if employee_id else ""
    )

    subject = "รหัสผ่านบัญชีของคุณ"
    text_body = (
        f"เรียน {employee_name},\n\n"
        f"ตามคำขอ นี่คือรหัสผ่านบัญชีของคุณ:\n\n"
        f"{password}\n\n"
        f"{emp_id_text}"
        f"หากคุณไม่ได้ร้องขอ โปรดติดต่อผู้ดูแลระบบ\n\n"
        f"ด้วยความนับถือ,\nทีม GUTSESS\n"
    )
    html_body = f"""<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.6;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
      <h2 style="color: #333;">รหัสผ่านบัญชีของคุณ</h2>
      <p>เรียน <strong>{employee_name}</strong>,</p>
      {emp_id_html}
      <p>ตามคำขอ นี่คือรหัสผ่านบัญชีของคุณ:</p>
      <p style="font-size:42px;color:#0047b3;font-weight:700;">{password}</p>
      <p>หากคุณไม่ได้ร้องขอ โปรดติดต่อผู้ดูแลระบบ</p>
      <p>ด้วยความนับถือ,<br/><strong>ทีม GUTSESS</strong></p>
    </div>
  </body>
</html>"""

    success = _send_email(to_email, subject, text_body, html_body)
    if success:
        _logger.info("Forgot-password email sent to %s", to_email)
    else:
        _logger.warning("Forgot-password email FAILED for %s", to_email)
    return success


def send_change_password_notification_email(
    to_email: str, employee_name: str, new_password: str, employee_id: str | None = None
) -> bool:
    """
    Send an email notifying the employee that their password has been changed,
    with the new password included.

    Returns True if the email was sent successfully, False otherwise.
    """
    emp_id_text = f"รหัสพนักงาน: {employee_id}\n\n" if employee_id else ""
    emp_id_html = (
        f"<p><strong>รหัสพนักงาน:</strong> {employee_id}</p>" if employee_id else ""
    )

    subject = "แจ้งเปลี่ยนรหัสผ่าน"
    text_body = (
        f"เรียน {employee_name},\n\n"
        f"รหัสผ่านของคุณถูกเปลี่ยนแปลงเรียบร้อยแล้ว\n\n"
        f"รหัสผ่านใหม่ของคุณคือ:\n\n"
        f"{new_password}\n\n"
        f"{emp_id_text}"
        f"กรุณาเข้าสู่ระบบด้วยรหัสผ่านใหม่นี้\n\n"
        f"ด้วยความนับถือ,\nทีม GUTSESS\n"
    )
    html_body = f"""<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.6;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
      <h2 style="color: #333;">แจ้งเปลี่ยนรหัสผ่าน</h2>
      <p>เรียน <strong>{employee_name}</strong>,</p>
      {emp_id_html}
      <p>รหัสผ่านของคุณถูกเปลี่ยนแปลงเรียบร้อยแล้ว</p>
      <p>รหัสผ่านใหม่ของคุณคือ:</p>
      <p style="font-size:42px;color:#0047b3;font-weight:700;">{new_password}</p>
      <p>กรุณาเข้าสู่ระบบด้วยรหัสผ่านใหม่นี้</p>
      <p>ด้วยความนับถือ,<br/><strong>ทีม GUTSESS</strong></p>
    </div>
  </body>
</html>"""

    success = _send_email(to_email, subject, text_body, html_body)
    if success:
        _logger.info("Change-password notification sent to %s", to_email)
    else:
        _logger.warning("Change-password notification FAILED for %s", to_email)
    return success
