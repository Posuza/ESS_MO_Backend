"""
Email Service — centralized email sending functionality.

Handles all email operations including password reset, notifications, etc.
"""
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings


def send_reset_email(to_email: str, employee_name: str, reset_token: str) -> None:
    """
    Send password reset email with token link.
    
    Args:
        to_email: Recipient email address
        employee_name: Name of the employee
        reset_token: JWT token for password reset
    """
    smtp_host = settings.SMTP_HOST
    smtp_port = settings.SMTP_PORT
    smtp_user = settings.SMTP_USER
    smtp_pass = settings.SMTP_PASS
    email_from = settings.EMAIL_FROM or smtp_user
    frontend_url = settings.FRONTEND_URL

    reset_link = f"{frontend_url}/reset-password?token={reset_token}"
    subject = "Password Reset Request"

    text_body = (
        f"Dear {employee_name},\n\n"
        f"A password reset was requested for your account.\n"
        f"Use the link below to reset your password "
        f"(valid for {settings.RESET_EXPIRE_MINUTES} minutes):\n\n"
        f"{reset_link}\n\n"
        f"If you did not request this, please ignore this email.\n\n"
        f"Best regards,\nGUTSESS Team"
    )

    html_body = f"""<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.6;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
      <h2 style="color: #333;">Password Reset Request</h2>
      <p>Dear <strong>{employee_name}</strong>,</p>
      <p>A password reset was requested for your account.</p>
      <p>
        Click the button below to reset your password
        <em>(valid for {settings.RESET_EXPIRE_MINUTES} minutes)</em>:
      </p>
      <p>
        <a href="{reset_link}"
           style="background-color:#4CAF50;color:white;padding:12px 24px;
                  text-decoration:none;border-radius:4px;display:inline-block;">
          Reset Password
        </a>
      </p>
      <p>
        Or copy this link into your browser:<br/>
        <small>{reset_link}</small>
      </p>
      <p>If you did not request this, please ignore this email.</p>
      <p>Best regards,<br/><strong>GUTSESS Team</strong></p>
    </div>
  </body>
</html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = email_from
    msg["To"] = to_email
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        server.starttls()
        if smtp_user and smtp_pass:
            server.login(smtp_user, smtp_pass)
        server.sendmail(email_from, to_email, msg.as_string())


def send_plain_password_email(to_email: str, employee_name: str, password: str, employee_id: str | None = None) -> None:
    """
    Send plain password via email (legacy/insecure method).
    
    WARNING: This is insecure. Only use for backwards compatibility.
    
    Args:
        to_email: Recipient email address
        employee_name: Name of the employee
        password: Plain text password
    """
    smtp_host = settings.SMTP_HOST
    smtp_port = settings.SMTP_PORT
    smtp_user = settings.SMTP_USER
    smtp_pass = settings.SMTP_PASS
    email_from = settings.EMAIL_FROM or smtp_user

    subject = "Your account password"

    # Pre-compute optional blocks (no backslashes inside f-string expressions)
    emp_id_text = f"Employee ID: {employee_id}\n\n" if employee_id else ""
    emp_id_html = f"<p><strong>Employee ID:</strong> {employee_id}</p>" if employee_id else ""

    text_body = (
        f"Dear {employee_name},\n\n"
        f"As requested, here is your current account password:\n\n"
        f"{password}\n\n"
        f"{emp_id_text}"
        f"If you did not request this, please contact your system administrator.\n\n"
        f"Best regards,\nGUTSESS Team\n"
        f"Sent from: {email_from}"
    )

    html_body = f"""<html>
  <body style="font-family: Arial, sans-serif; line-height: 1.6;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
      <h2 style="color: #333;">Your account password</h2>
      <p>Dear <strong>{employee_name}</strong>,</p>
      {emp_id_html}
      <p>As requested, here is your current account password:</p>
      <p style="font-size:42px;color:#0047b3;font-weight:700;">{password}</p>
      <p>If you did not request this, please contact your system administrator.</p>
      <p>Best regards,<br/><strong>GUTSESS Team</strong></p>
      <p style="font-size:12px; color:#666;">Email:{email_from}</p>
    </div>
  </body>
</html>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = email_from
    msg["To"] = to_email
    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        server.starttls()
        if smtp_user and smtp_pass:
            server.login(smtp_user, smtp_pass)
        server.sendmail(email_from, to_email, msg.as_string())
