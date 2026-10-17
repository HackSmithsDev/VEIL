import logging
import smtplib
import ssl
from email.message import EmailMessage
from email.utils import formataddr

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailDeliveryError(RuntimeError):
    pass


def build_message(
    recipient: str,
    subject: str,
    text_body: str,
    html_body: str,
) -> EmailMessage:
    if not settings.email_enabled or settings.smtp_from_email is None:
        raise EmailDeliveryError("SMTP email delivery is not configured")

    message = EmailMessage()
    message["From"] = formataddr(
        (settings.smtp_from_name, str(settings.smtp_from_email))
    )
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(text_body)
    message.add_alternative(html_body, subtype="html")
    return message


def send_message(message: EmailMessage) -> None:
    if not settings.email_enabled or settings.smtp_host is None:
        raise EmailDeliveryError("SMTP email delivery is not configured")

    context = ssl.create_default_context()
    try:
        if settings.smtp_ssl_tls:
            smtp_client = smtplib.SMTP_SSL(
                settings.smtp_host,
                settings.smtp_port,
                timeout=settings.smtp_timeout_seconds,
                context=context,
            )
        else:
            smtp_client = smtplib.SMTP(
                settings.smtp_host,
                settings.smtp_port,
                timeout=settings.smtp_timeout_seconds,
            )
        with smtp_client as smtp:
            if settings.smtp_starttls and not settings.smtp_ssl_tls:
                smtp.starttls(context=context)
            if settings.smtp_username and settings.smtp_password:
                smtp.login(
                    settings.smtp_username,
                    settings.smtp_password.get_secret_value(),
                )
            smtp.send_message(message)
    except (OSError, smtplib.SMTPException) as error:
        logger.error("SMTP delivery failed (%s)", type(error).__name__)
        raise EmailDeliveryError("SMTP email delivery failed") from error
