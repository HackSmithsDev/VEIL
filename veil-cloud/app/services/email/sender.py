import logging
from email.message import EmailMessage

from app.core.config import settings
from app.services.email.client import EmailDeliveryError, build_message, send_message
from app.services.email.templates import (
    render_feedback_notification,
    render_feedback_receipt,
    render_welcome_email,
)

logger = logging.getLogger(__name__)


def deliver_email(message: EmailMessage, purpose: str) -> None:
    if not settings.email_enabled:
        logger.warning(
            "Skipped %s email because SMTP is not configured",
            purpose,
        )
        return
    try:
        send_message(message)
    except EmailDeliveryError:
        logger.error("Failed to deliver %s email", purpose)


def send_welcome_email(recipient: str, full_name: str) -> None:
    if not settings.email_enabled:
        logger.warning("Skipped welcome email because SMTP is not configured")
        return
    subject, text, html = render_welcome_email(full_name)
    message = build_message(recipient, subject, text, html)
    deliver_email(message, "welcome")


def send_feedback_emails(
    user_email: str,
    full_name: str,
    category: str,
    feedback_message: str,
) -> None:
    if not settings.email_enabled:
        logger.warning("Skipped feedback emails because SMTP is not configured")
        return
    subject, text, html = render_feedback_receipt(full_name, category)
    deliver_email(
        build_message(user_email, subject, text, html),
        "feedback receipt",
    )

    recipient = settings.feedback_notification_email
    if recipient is None:
        logger.info("Feedback notification email is not configured")
        return

    subject, text, html = render_feedback_notification(
        full_name,
        user_email,
        category,
        feedback_message,
    )
    deliver_email(
        build_message(str(recipient), subject, text, html),
        "feedback notification",
    )
