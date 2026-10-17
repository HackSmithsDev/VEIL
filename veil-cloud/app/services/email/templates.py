from html import escape


def render_welcome_email(full_name: str) -> tuple[str, str, str]:
    name = full_name.strip() or "there"
    subject = "Welcome to VEIL Guard"
    text = (
        f"Hi {name},\n\n"
        "Your VEIL Guard account is ready. You can now keep basic program "
        "metadata and feedback together in your workspace.\n\n"
        "Please do not submit source code, passwords, confidential prompts, "
        "or other secrets to VEIL Cloud.\n\n"
        "The VEIL Guard team"
    )
    html = (
        f"<p>Hi {escape(name)},</p>"
        "<p>Your VEIL Guard account is ready. You can now keep basic program "
        "metadata and feedback together in your workspace.</p>"
        "<p>Please do not submit source code, passwords, confidential prompts, "
        "or other secrets to VEIL Cloud.</p>"
        "<p>The VEIL Guard team</p>"
    )
    return subject, text, html


def render_feedback_receipt(full_name: str, category: str) -> tuple[str, str, str]:
    name = full_name.strip() or "there"
    safe_category = category.replace("_", " ")
    subject = "We received your VEIL Guard feedback"
    text = (
        f"Hi {name},\n\n"
        f"We received your {safe_category} feedback. Thanks for helping us "
        "improve VEIL Guard.\n\n"
        "The VEIL Guard team"
    )
    html = (
        f"<p>Hi {escape(name)},</p>"
        f"<p>We received your <strong>{escape(safe_category)}</strong> feedback. "
        "Thanks for helping us improve VEIL Guard.</p>"
        "<p>The VEIL Guard team</p>"
    )
    return subject, text, html


def render_feedback_notification(
    full_name: str,
    email: str,
    category: str,
    message: str,
) -> tuple[str, str, str]:
    safe_name = full_name.strip() or "Unknown user"
    safe_category = category.replace("_", " ")
    subject = f"VEIL Guard feedback: {safe_category}"
    text = (
        f"From: {safe_name} <{email}>\n"
        f"Category: {safe_category}\n\n"
        f"{message}"
    )
    html = (
        "<h2>New VEIL Guard feedback</h2>"
        f"<p><strong>From:</strong> {escape(safe_name)} &lt;{escape(email)}&gt;</p>"
        f"<p><strong>Category:</strong> {escape(safe_category)}</p>"
        f"<pre style=\"white-space:pre-wrap;font:inherit\">{escape(message)}</pre>"
    )
    return subject, text, html
