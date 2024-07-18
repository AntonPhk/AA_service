import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.core.config import settings


class EmailSender:
    def __init__(self):
        self._smtp_server = settings.SMTP_SERVER
        self._smtp_port = settings.SMTP_PORT
        self._username = settings.MAIL_USER
        self._password = settings.MAIL_PASSWORD

    async def _send_email(self, to_email, subject, body):
        msg = MIMEMultipart()
        msg["From"] = self._username
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        try:
            server = smtplib.SMTP(self._smtp_server, self._smtp_port)
            server.starttls()
            server.login(self._username, self._password)
            text = msg.as_string()
            server.sendmail(self._username, to_email, text)
            server.quit()
            return True
        except Exception as e:
            print(f"Failed to send email: {e}")

    async def send_accept_registration_email(self, to_email: str, token: str):
        reset_link = (
            f"{settings.SERVICE_URL}/api/auth/confirm_registration?token={token}"
        )
        subject = "Accept registration"
        body = (
            f"Hello, {to_email}. Thank you for choosing our software."
            f"Click link below to confirm your registration:\n\n{reset_link}\n\n"
            f"Best regards."
        )
        return await self._send_email(to_email, subject, body)

    async def send_reset_password_email(self, to_email: str, token: str):
        reset_link = f"{settings.SERVICE_URL}/api/auth/reset_password?token={token}"
        subject = "Reset password"
        body = (
            f"Hello, {to_email}."
            f"Click link below to reset your password:\n\n{reset_link}\n\n"
            f"Best regards."
        )
        return await self._send_email(to_email, subject, body)
