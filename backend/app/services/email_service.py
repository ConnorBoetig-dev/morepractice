"""
Email Service

Enterprise-grade email sending service with template rendering.
Handles all email types: password reset, verification, notifications, etc.

Features:
- Template-based emails (HTML + plain text fallback)
- Async email sending (non-blocking)
- Error handling and logging
- Support for multiple email providers (Gmail, SendGrid, AWS SES)
"""

from fastapi_mail import FastMail, MessageSchema, MessageType
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

from app.config.email_config import email_conf, email_settings

# Configure logging
logger = logging.getLogger(__name__)

# Initialize FastMail with configuration
fm = FastMail(email_conf)

# Initialize Jinja2 for template rendering
template_dir = Path(__file__).parent.parent / "templates" / "emails"
jinja_env = Environment(
    loader=FileSystemLoader(str(template_dir)),
    autoescape=select_autoescape(['html', 'xml'])
)


async def send_email(
    to: List[str],
    subject: str,
    html_content: str,
    text_content: Optional[str] = None
) -> bool:
    """
    Send an email (generic function)

    Args:
        to: List of recipient email addresses
        subject: Email subject line
        html_content: HTML email body
        text_content: Plain text fallback (optional)

    Returns:
        bool: True if email sent successfully, False otherwise

    Raises:
        Exception: If email sending fails
    """
    try:
        message = MessageSchema(
            subject=subject,
            recipients=to,
            body=html_content,
            subtype=MessageType.html
        )

        await fm.send_message(message)
        logger.info(f"✓ Email sent successfully to {to[0]}: {subject}")
        return True

    except Exception as e:
        logger.error(f"✗ Failed to send email to {to[0]}: {str(e)}")
        raise e


async def send_template_email(
    to: List[str],
    subject: str,
    template_name: str,
    context: Dict[str, Any]
) -> bool:
    """
    Send an email using a Jinja2 template

    Args:
        to: List of recipient email addresses
        subject: Email subject line
        template_name: Template filename (e.g., "password_reset.html")
        context: Template variables (dict)

    Returns:
        bool: True if email sent successfully

    Example:
        await send_template_email(
            to=["user@example.com"],
            subject="Reset Your Password",
            template_name="password_reset.html",
            context={"reset_link": "https://...", "username": "John"}
        )
    """
    try:
        # Render HTML template
        html_template = jinja_env.get_template(template_name)
        html_content = html_template.render(**context)

        # Try to find plain text version
        text_template_name = template_name.replace('.html', '.txt')
        try:
            text_template = jinja_env.get_template(text_template_name)
            text_content = text_template.render(**context)
        except:
            text_content = None  # No plain text version

        return await send_email(to, subject, html_content, text_content)

    except Exception as e:
        logger.error(f"✗ Failed to render/send template email: {str(e)}")
        raise e


async def send_password_reset_email(email: str, reset_token: str, username: str) -> bool:
    """
    Send password reset email

    Args:
        email: Recipient email address
        reset_token: Password reset token
        username: User's username

    Returns:
        bool: True if email sent successfully

    Email includes:
        - Reset link with token
        - Expiration time (1 hour)
        - Security warnings
    """
    reset_link = f"{email_settings.FRONTEND_URL}/reset-password.html?token={reset_token}"

    context = {
        "username": username,
        "reset_link": reset_link,
        "expiration_hours": 1,
        "support_email": email_settings.FROM_EMAIL
    }

    return await send_template_email(
        to=[email],
        subject="Reset Your Password - Billings Quiz Platform",
        template_name="password_reset.html",
        context=context
    )


async def send_verification_email(email: str, verification_token: str, username: str) -> bool:
    """
    Send email verification email

    Args:
        email: Recipient email address
        verification_token: Email verification token
        username: User's username

    Returns:
        bool: True if email sent successfully

    Email includes:
        - Verification link with token
        - Expiration time (24 hours)
        - Benefits of verification
    """
    verification_link = f"{email_settings.FRONTEND_URL}/verify-email.html?token={verification_token}"

    context = {
        "username": username,
        "verification_link": verification_link,
        "expiration_hours": 24,
        "support_email": email_settings.FROM_EMAIL
    }

    return await send_template_email(
        to=[email],
        subject="Welcome - Please Verify Your Email Address",
        template_name="email_verification.html",
        context=context
    )


async def send_welcome_email(email: str, username: str) -> bool:
    """
    Send welcome email to new users

    Args:
        email: Recipient email address
        username: User's username

    Returns:
        bool: True if email sent successfully

    Email includes:
        - Welcome message
        - Getting started tips
        - Link to first quiz
        - Platform features overview
    """
    dashboard_link = f"{email_settings.FRONTEND_URL}/dashboard.html"
    quiz_link = f"{email_settings.FRONTEND_URL}/quiz-select.html"

    context = {
        "username": username,
        "dashboard_link": dashboard_link,
        "quiz_link": quiz_link,
        "support_email": email_settings.FROM_EMAIL
    }

    return await send_template_email(
        to=[email],
        subject="Welcome to Billings Quiz Platform! 🎉",
        template_name="welcome.html",
        context=context
    )


async def send_achievement_notification(
    email: str,
    username: str,
    achievement_name: str,
    achievement_description: str,
    achievement_icon: str,
    achievement_rarity: str,
    xp_reward: int,
    total_achievements: int = 0,
    current_level: int = 1,
    total_xp: int = 0,
    quiz_count: int = 0
) -> bool:
    """
    Send achievement unlock notification

    Args:
        email: Recipient email address
        username: User's username
        achievement_name: Achievement name
        achievement_description: Achievement description
        achievement_icon: Achievement icon (emoji)
        achievement_rarity: Achievement rarity (common, rare, epic, legendary)
        xp_reward: XP earned from achievement
        total_achievements: Total achievements unlocked
        current_level: User's current level
        total_xp: User's total XP
        quiz_count: Total quizzes completed

    Returns:
        bool: True if email sent successfully

    Email includes:
        - Achievement details with icon and rarity
        - XP reward
        - User stats (level, total XP, quiz count)
        - Links to dashboard and achievements page
        - Encouragement message
    """
    dashboard_url = f"{email_settings.FRONTEND_URL}/dashboard.html"
    achievements_url = f"{email_settings.FRONTEND_URL}/achievements.html"
    quiz_url = f"{email_settings.FRONTEND_URL}/quiz-select.html"

    context = {
        "username": username,
        "achievement_name": achievement_name,
        "achievement_description": achievement_description,
        "achievement_icon": achievement_icon,
        "achievement_rarity": achievement_rarity,
        "xp_reward": xp_reward,
        "total_achievements": total_achievements,
        "current_level": current_level,
        "total_xp": total_xp,
        "quiz_count": quiz_count,
        "dashboard_url": dashboard_url,
        "achievements_url": achievements_url,
        "quiz_url": quiz_url
    }

    return await send_template_email(
        to=[email],
        subject=f"🏆 Achievement Unlocked: {achievement_name}!",
        template_name="achievement_unlocked.html",
        context=context
    )


async def send_streak_reminder(
    email: str,
    username: str,
    current_streak: int
) -> bool:
    """
    Send streak reminder email

    Args:
        email: Recipient email address
        username: User's username
        current_streak: Current streak count

    Returns:
        bool: True if email sent successfully

    Email includes:
        - Current streak count
        - Motivational message
        - Link to start quiz
        - Streak benefits
    """
    quiz_link = f"{email_settings.FRONTEND_URL}/quiz-select.html"

    context = {
        "username": username,
        "current_streak": current_streak,
        "quiz_link": quiz_link
    }

    return await send_template_email(
        to=[email],
        subject=f"🔥 Don't Break Your {current_streak}-Day Streak!",
        template_name="streak_reminder.html",
        context=context
    )


async def send_password_changed_email(email: str, username: str) -> bool:
    """
    Send password change confirmation email

    Args:
        email: Recipient email address
        username: User's username

    Returns:
        bool: True if email sent successfully

    Email includes:
        - Confirmation that password was changed
        - Security warning if not authorized
        - Link to support
    """
    support_link = f"{email_settings.FRONTEND_URL}/support.html"

    context = {
        "username": username,
        "support_link": support_link,
        "support_email": email_settings.FROM_EMAIL
    }

    return await send_template_email(
        to=[email],
        subject="Password Changed - Billings Quiz Platform",
        template_name="password_changed.html",
        context=context
    )


async def send_test_email(email: str) -> bool:
    """
    Send a test email to verify SMTP configuration

    Args:
        email: Recipient email address

    Returns:
        bool: True if email sent successfully

    Used for:
        - Testing email configuration
        - Verifying SMTP credentials
        - Checking email delivery
    """
    html_content = """
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>✓ Email Configuration Test Successful!</h2>
            <p>If you're reading this, your email configuration is working correctly.</p>
            <p><strong>SMTP Settings:</strong></p>
            <ul>
                <li>Host: {host}</li>
                <li>Port: {port}</li>
                <li>From: {from_email}</li>
            </ul>
            <p>You can now send emails from your Billings Quiz Platform.</p>
        </body>
    </html>
    """.format(
        host=email_settings.SMTP_HOST,
        port=email_settings.SMTP_PORT,
        from_email=email_settings.FROM_EMAIL
    )

    return await send_email(
        to=[email],
        subject="Email Configuration Test - Billings",
        html_content=html_content
    )


# Email service health check
def is_email_configured() -> bool:
    """
    Check if email service is properly configured

    Returns:
        bool: True if all required settings are present

    Checks:
        - SMTP credentials
        - From email address
        - Frontend URL
    """
    try:
        if not email_settings.SMTP_USERNAME:
            logger.warning("SMTP_USERNAME not configured")
            return False

        if not email_settings.SMTP_PASSWORD:
            logger.warning("SMTP_PASSWORD not configured")
            return False

        if not email_settings.FROM_EMAIL:
            logger.warning("FROM_EMAIL not configured")
            return False

        logger.info("✓ Email service is properly configured")
        return True

    except Exception as e:
        logger.error(f"✗ Email configuration check failed: {str(e)}")
        return False
