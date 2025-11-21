"""
Email Configuration

Centralized email settings for SMTP and FastAPI-Mail.
Loads configuration from environment variables.

Supported Email Providers:
- Gmail (smtp.gmail.com:587) - Requires app password
- SendGrid (smtp.sendgrid.net:587) - Requires API key
- AWS SES (email-smtp.us-east-1.amazonaws.com:587) - Requires IAM credentials
- Custom SMTP server

Environment Variables Required:
- SMTP_HOST: SMTP server hostname
- SMTP_PORT: SMTP server port (usually 587 for TLS)
- SMTP_USERNAME: SMTP authentication username
- SMTP_PASSWORD: SMTP authentication password or app password
- FROM_EMAIL: Email address to send from
- FROM_NAME: Display name for from address (optional)
- FRONTEND_URL: Frontend URL for email links (e.g., http://localhost:8080)
"""

import os
from pathlib import Path
from typing import Dict, Any
from fastapi_mail import ConnectionConfig
from pydantic_settings import BaseSettings

# Get absolute path to templates directory
# Works whether running from backend/ or tests/
TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "emails"


class EmailSettings(BaseSettings):
    """
    Email configuration loaded from environment variables
    """

    # SMTP Settings
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")

    # Sender Information
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "noreply@billings.com")
    FROM_NAME: str = os.getenv("FROM_NAME", "Billings Quiz Platform")

    # Frontend URL (for links in emails)
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:8080")

    # Email Settings
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    class Config:
        env_file = "../.env"  # Load from root directory
        case_sensitive = True
        extra = "ignore"  # Ignore extra environment variables


# Load settings
email_settings = EmailSettings()


# FastAPI-Mail connection configuration
email_conf = ConnectionConfig(
    MAIL_USERNAME=email_settings.SMTP_USERNAME,
    MAIL_PASSWORD=email_settings.SMTP_PASSWORD,
    MAIL_FROM=email_settings.FROM_EMAIL,
    MAIL_PORT=email_settings.SMTP_PORT,
    MAIL_SERVER=email_settings.SMTP_HOST,
    MAIL_FROM_NAME=email_settings.FROM_NAME,
    MAIL_STARTTLS=True,  # Use TLS
    MAIL_SSL_TLS=False,  # Don't use SSL (we use STARTTLS)
    USE_CREDENTIALS=email_settings.USE_CREDENTIALS,
    VALIDATE_CERTS=email_settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=str(TEMPLATE_DIR)  # Absolute path to email templates
)


def get_email_config() -> Dict[str, Any]:
    """
    Get email configuration as dictionary

    Returns:
        dict: Email configuration settings
    """
    return {
        "smtp_host": email_settings.SMTP_HOST,
        "smtp_port": email_settings.SMTP_PORT,
        "from_email": email_settings.FROM_EMAIL,
        "from_name": email_settings.FROM_NAME,
        "frontend_url": email_settings.FRONTEND_URL
    }


def verify_email_config() -> bool:
    """
    Verify that required email configuration is present

    Returns:
        bool: True if configuration is valid

    Raises:
        ValueError: If required configuration is missing
    """
    if not email_settings.SMTP_USERNAME:
        raise ValueError("SMTP_USERNAME not configured")

    if not email_settings.SMTP_PASSWORD:
        raise ValueError("SMTP_PASSWORD not configured")

    if not email_settings.FROM_EMAIL:
        raise ValueError("FROM_EMAIL not configured")

    return True


# Example configurations for common providers
PROVIDER_CONFIGS = {
    "gmail": {
        "SMTP_HOST": "smtp.gmail.com",
        "SMTP_PORT": 587,
        "instructions": "Use app password from Google Account settings"
    },
    "sendgrid": {
        "SMTP_HOST": "smtp.sendgrid.net",
        "SMTP_PORT": 587,
        "SMTP_USERNAME": "apikey",
        "instructions": "SMTP_PASSWORD should be your SendGrid API key"
    },
    "aws_ses": {
        "SMTP_HOST": "email-smtp.us-east-1.amazonaws.com",
        "SMTP_PORT": 587,
        "instructions": "Use IAM user SMTP credentials from AWS SES"
    }
}
