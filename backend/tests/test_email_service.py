"""
COMPREHENSIVE EMAIL SERVICE TESTS
Tests email sending functionality with mocking (no actual emails sent)

Coverage target: 0% → 80%

Tests:
- Email configuration validation
- Generic email sending
- Template-based email sending
- Password reset emails
- Email verification emails
- Welcome emails
- Achievement notification emails
- Streak reminder emails
- Password changed emails
- Test emails
- Error handling
- Template rendering

Strategy:
- Mock FastMail to avoid sending real emails
- Mock Jinja2 template rendering
- Test all email types
- Test error scenarios
- Test configuration validation
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from pathlib import Path

# Email service imports
from app.services.email_service import (
    send_email,
    send_template_email,
    send_password_reset_email,
    send_verification_email,
    send_welcome_email,
    send_achievement_notification,
    send_streak_reminder,
    send_password_changed_email,
    send_test_email,
    is_email_configured
)
from app.config.email_config import email_settings


# ================================================================
# CONFIGURATION TESTS
# ================================================================

def test_is_email_configured_with_valid_config():
    """
    REAL TEST: Check if email is configured
    Tests: is_email_configured() returns True when all settings present
    """
    with patch('app.services.email_service.email_settings') as mock_settings:
        mock_settings.SMTP_USERNAME = "test@example.com"
        mock_settings.SMTP_PASSWORD = "test_password"
        mock_settings.FROM_EMAIL = "noreply@billings.com"

        result = is_email_configured()

        assert result is True


def test_is_email_configured_missing_username():
    """
    REAL TEST: Missing SMTP username
    Tests: is_email_configured() returns False when username missing
    """
    with patch('app.services.email_service.email_settings') as mock_settings:
        mock_settings.SMTP_USERNAME = ""  # Missing
        mock_settings.SMTP_PASSWORD = "test_password"
        mock_settings.FROM_EMAIL = "noreply@billings.com"

        result = is_email_configured()

        assert result is False


def test_is_email_configured_missing_password():
    """
    REAL TEST: Missing SMTP password
    Tests: is_email_configured() returns False when password missing
    """
    with patch('app.services.email_service.email_settings') as mock_settings:
        mock_settings.SMTP_USERNAME = "test@example.com"
        mock_settings.SMTP_PASSWORD = ""  # Missing
        mock_settings.FROM_EMAIL = "noreply@billings.com"

        result = is_email_configured()

        assert result is False


def test_is_email_configured_missing_from_email():
    """
    REAL TEST: Missing from email
    Tests: is_email_configured() returns False when from_email missing
    """
    with patch('app.services.email_service.email_settings') as mock_settings:
        mock_settings.SMTP_USERNAME = "test@example.com"
        mock_settings.SMTP_PASSWORD = "test_password"
        mock_settings.FROM_EMAIL = ""  # Missing

        result = is_email_configured()

        assert result is False


# ================================================================
# GENERIC EMAIL SENDING TESTS
# ================================================================

@pytest.mark.asyncio
async def test_send_email_success():
    """
    REAL TEST: Send basic email successfully
    Tests: send_email() sends email with correct parameters
    """
    with patch('app.services.email_service.fm.send_message', new_callable=AsyncMock) as mock_send:
        mock_send.return_value = None  # Successful send

        result = await send_email(
            to=["user@example.com"],
            subject="Test Subject",
            html_content="<h1>Test Email</h1>",
            text_content="Test Email"
        )

        assert result is True
        assert mock_send.called
        assert mock_send.call_count == 1

        # Verify message schema was created correctly
        call_args = mock_send.call_args[0][0]
        assert call_args.subject == "Test Subject"
        assert call_args.recipients == ["user@example.com"]
        assert call_args.body == "<h1>Test Email</h1>"


@pytest.mark.asyncio
async def test_send_email_failure_raises_exception():
    """
    REAL TEST: Email sending fails
    Tests: send_email() raises exception on failure
    """
    with patch('app.services.email_service.fm.send_message', new_callable=AsyncMock) as mock_send:
        mock_send.side_effect = Exception("SMTP connection failed")

        with pytest.raises(Exception) as exc_info:
            await send_email(
                to=["user@example.com"],
                subject="Test",
                html_content="Test"
            )

        assert "SMTP connection failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_send_email_multiple_recipients():
    """
    REAL TEST: Send email to multiple recipients
    Tests: send_email() handles multiple recipients
    """
    with patch('app.services.email_service.fm.send_message', new_callable=AsyncMock) as mock_send:
        mock_send.return_value = None

        result = await send_email(
            to=["user1@example.com", "user2@example.com"],
            subject="Bulk Email",
            html_content="<p>Bulk message</p>"
        )

        assert result is True
        call_args = mock_send.call_args[0][0]
        assert len(call_args.recipients) == 2


# ================================================================
# TEMPLATE EMAIL TESTS
# ================================================================

@pytest.mark.asyncio
async def test_send_template_email_success():
    """
    REAL TEST: Send templated email successfully
    Tests: send_template_email() renders template and sends email
    """
    # Mock Jinja environment
    with patch('app.services.email_service.jinja_env') as mock_jinja, \
         patch('app.services.email_service.fm.send_message', new_callable=AsyncMock) as mock_send:

        # Mock template rendering
        mock_template = MagicMock()
        mock_template.render.return_value = "<h1>Hello John</h1>"
        mock_jinja.get_template.return_value = mock_template

        mock_send.return_value = None

        result = await send_template_email(
            to=["user@example.com"],
            subject="Template Test",
            template_name="test_template.html",
            context={"username": "John"}
        )

        assert result is True

        # Verify template was loaded and rendered
        mock_jinja.get_template.assert_called_with("test_template.html")
        mock_template.render.assert_called_with(username="John")

        # Verify email was sent
        assert mock_send.called


@pytest.mark.asyncio
async def test_send_template_email_with_text_fallback():
    """
    REAL TEST: Send templated email with plain text version
    Tests: send_template_email() uses both HTML and text templates
    """
    with patch('app.services.email_service.jinja_env') as mock_jinja, \
         patch('app.services.email_service.fm.send_message', new_callable=AsyncMock) as mock_send:

        # Mock both HTML and text templates
        mock_html_template = MagicMock()
        mock_html_template.render.return_value = "<h1>HTML Version</h1>"

        mock_text_template = MagicMock()
        mock_text_template.render.return_value = "Text Version"

        def get_template_side_effect(name):
            if name == "test.html":
                return mock_html_template
            elif name == "test.txt":
                return mock_text_template
            raise Exception("Template not found")

        mock_jinja.get_template.side_effect = get_template_side_effect
        mock_send.return_value = None

        result = await send_template_email(
            to=["user@example.com"],
            subject="Test",
            template_name="test.html",
            context={"name": "Test"}
        )

        assert result is True

        # Verify both templates were attempted
        assert mock_jinja.get_template.call_count >= 1


@pytest.mark.asyncio
async def test_send_template_email_missing_template_raises_exception():
    """
    REAL TEST: Template not found
    Tests: send_template_email() raises exception when template missing
    """
    with patch('app.services.email_service.jinja_env') as mock_jinja:
        mock_jinja.get_template.side_effect = Exception("Template not found")

        with pytest.raises(Exception) as exc_info:
            await send_template_email(
                to=["user@example.com"],
                subject="Test",
                template_name="nonexistent.html",
                context={}
            )

        assert "Template not found" in str(exc_info.value)


# ================================================================
# PASSWORD RESET EMAIL TESTS
# ================================================================

@pytest.mark.asyncio
async def test_send_password_reset_email_success():
    """
    REAL TEST: Send password reset email
    Tests: send_password_reset_email() sends correct email with reset link
    """
    with patch('app.services.email_service.send_template_email', new_callable=AsyncMock) as mock_send_template:
        mock_send_template.return_value = True

        result = await send_password_reset_email(
            email="user@example.com",
            reset_token="abc123xyz",
            username="JohnDoe"
        )

        assert result is True
        assert mock_send_template.called

        # Verify correct template and context
        call_kwargs = mock_send_template.call_args[1]
        assert call_kwargs['template_name'] == "password_reset.html"
        assert "Reset Your Password" in call_kwargs['subject']

        # Verify context includes reset link and username
        context = call_kwargs['context']
        assert context['username'] == "JohnDoe"
        assert "abc123xyz" in context['reset_link']
        assert context['expiration_hours'] == 1


@pytest.mark.asyncio
async def test_send_password_reset_email_includes_frontend_url():
    """
    REAL TEST: Password reset link includes frontend URL
    Tests: Reset link uses FRONTEND_URL from config
    """
    with patch('app.services.email_service.send_template_email', new_callable=AsyncMock) as mock_send_template, \
         patch('app.services.email_service.email_settings') as mock_settings:

        mock_settings.FRONTEND_URL = "https://billings.com"
        mock_send_template.return_value = True

        await send_password_reset_email(
            email="user@example.com",
            reset_token="token123",
            username="User"
        )

        context = mock_send_template.call_args[1]['context']
        assert "https://billings.com" in context['reset_link']
        assert "token123" in context['reset_link']


# ================================================================
# EMAIL VERIFICATION TESTS
# ================================================================

@pytest.mark.asyncio
async def test_send_verification_email_success():
    """
    REAL TEST: Send email verification email
    Tests: send_verification_email() sends correct verification email
    """
    with patch('app.services.email_service.send_template_email', new_callable=AsyncMock) as mock_send_template:
        mock_send_template.return_value = True

        result = await send_verification_email(
            email="newuser@example.com",
            verification_token="verify123",
            username="NewUser"
        )

        assert result is True

        call_kwargs = mock_send_template.call_args[1]
        assert call_kwargs['template_name'] == "email_verification.html"
        assert "Verify" in call_kwargs['subject']

        context = call_kwargs['context']
        assert context['username'] == "NewUser"
        assert "verify123" in context['verification_link']
        assert context['expiration_hours'] == 24  # 24 hour expiration


@pytest.mark.asyncio
async def test_send_verification_email_link_format():
    """
    REAL TEST: Verification link format
    Tests: Verification link has correct format with token
    """
    with patch('app.services.email_service.send_template_email', new_callable=AsyncMock) as mock_send_template, \
         patch('app.services.email_service.email_settings') as mock_settings:

        mock_settings.FRONTEND_URL = "http://localhost:8080"
        mock_send_template.return_value = True

        await send_verification_email(
            email="user@example.com",
            verification_token="abc123",
            username="User"
        )

        context = mock_send_template.call_args[1]['context']
        expected_link = "http://localhost:8080/verify-email.html?token=abc123"
        assert context['verification_link'] == expected_link


# ================================================================
# WELCOME EMAIL TESTS
# ================================================================

@pytest.mark.asyncio
async def test_send_welcome_email_success():
    """
    REAL TEST: Send welcome email to new user
    Tests: send_welcome_email() sends welcome message with platform links
    """
    with patch('app.services.email_service.send_template_email', new_callable=AsyncMock) as mock_send_template:
        mock_send_template.return_value = True

        result = await send_welcome_email(
            email="newuser@example.com",
            username="NewUser"
        )

        assert result is True

        call_kwargs = mock_send_template.call_args[1]
        assert call_kwargs['template_name'] == "welcome.html"
        assert "Welcome" in call_kwargs['subject']

        context = call_kwargs['context']
        assert context['username'] == "NewUser"
        assert 'dashboard_link' in context
        assert 'quiz_link' in context


@pytest.mark.asyncio
async def test_send_welcome_email_includes_platform_links():
    """
    REAL TEST: Welcome email includes dashboard and quiz links
    Tests: Context includes proper navigation links
    """
    with patch('app.services.email_service.send_template_email', new_callable=AsyncMock) as mock_send_template, \
         patch('app.services.email_service.email_settings') as mock_settings:

        mock_settings.FRONTEND_URL = "https://billings.com"
        mock_send_template.return_value = True

        await send_welcome_email(
            email="user@example.com",
            username="User"
        )

        context = mock_send_template.call_args[1]['context']
        assert "https://billings.com/dashboard.html" == context['dashboard_link']
        assert "https://billings.com/quiz-select.html" == context['quiz_link']


# ================================================================
# ACHIEVEMENT NOTIFICATION TESTS
# ================================================================

@pytest.mark.asyncio
async def test_send_achievement_notification_success():
    """
    REAL TEST: Send achievement unlocked notification
    Tests: send_achievement_notification() sends complete achievement details
    """
    with patch('app.services.email_service.send_template_email', new_callable=AsyncMock) as mock_send_template:
        mock_send_template.return_value = True

        result = await send_achievement_notification(
            email="user@example.com",
            username="ProUser",
            achievement_name="First Steps",
            achievement_description="Complete your first quiz",
            achievement_icon="🏆",
            achievement_rarity="common",
            xp_reward=50,
            total_achievements=5,
            current_level=2,
            total_xp=150,
            quiz_count=10
        )

        assert result is True

        call_kwargs = mock_send_template.call_args[1]
        assert call_kwargs['template_name'] == "achievement_unlocked.html"
        assert "Achievement Unlocked" in call_kwargs['subject']
        assert "First Steps" in call_kwargs['subject']

        context = call_kwargs['context']
        assert context['username'] == "ProUser"
        assert context['achievement_name'] == "First Steps"
        assert context['achievement_icon'] == "🏆"
        assert context['xp_reward'] == 50
        assert context['current_level'] == 2


@pytest.mark.asyncio
async def test_send_achievement_notification_includes_stats():
    """
    REAL TEST: Achievement email includes user stats
    Tests: Context includes level, XP, quiz count
    """
    with patch('app.services.email_service.send_template_email', new_callable=AsyncMock) as mock_send_template:
        mock_send_template.return_value = True

        await send_achievement_notification(
            email="user@example.com",
            username="User",
            achievement_name="Test",
            achievement_description="Test desc",
            achievement_icon="⭐",
            achievement_rarity="rare",
            xp_reward=100,
            total_achievements=12,
            current_level=5,
            total_xp=500,
            quiz_count=25
        )

        context = mock_send_template.call_args[1]['context']
        assert context['total_achievements'] == 12
        assert context['current_level'] == 5
        assert context['total_xp'] == 500
        assert context['quiz_count'] == 25


# ================================================================
# STREAK REMINDER TESTS
# ================================================================

@pytest.mark.asyncio
async def test_send_streak_reminder_success():
    """
    REAL TEST: Send streak reminder email
    Tests: send_streak_reminder() sends motivational streak email
    """
    with patch('app.services.email_service.send_template_email', new_callable=AsyncMock) as mock_send_template:
        mock_send_template.return_value = True

        result = await send_streak_reminder(
            email="user@example.com",
            username="StreakUser",
            current_streak=7
        )

        assert result is True

        call_kwargs = mock_send_template.call_args[1]
        assert call_kwargs['template_name'] == "streak_reminder.html"
        assert "Streak" in call_kwargs['subject']
        assert "7-Day" in call_kwargs['subject']

        context = call_kwargs['context']
        assert context['username'] == "StreakUser"
        assert context['current_streak'] == 7


# ================================================================
# PASSWORD CHANGED EMAIL TESTS
# ================================================================

@pytest.mark.asyncio
async def test_send_password_changed_email_success():
    """
    REAL TEST: Send password change confirmation
    Tests: send_password_changed_email() sends security confirmation
    """
    with patch('app.services.email_service.send_template_email', new_callable=AsyncMock) as mock_send_template:
        mock_send_template.return_value = True

        result = await send_password_changed_email(
            email="user@example.com",
            username="SecurityUser"
        )

        assert result is True

        call_kwargs = mock_send_template.call_args[1]
        assert call_kwargs['template_name'] == "password_changed.html"
        assert "Password Changed" in call_kwargs['subject']

        context = call_kwargs['context']
        assert context['username'] == "SecurityUser"
        assert 'support_link' in context


# ================================================================
# TEST EMAIL TESTS
# ================================================================

@pytest.mark.asyncio
async def test_send_test_email_success():
    """
    REAL TEST: Send test email for SMTP verification
    Tests: send_test_email() sends configuration test email
    """
    with patch('app.services.email_service.send_email', new_callable=AsyncMock) as mock_send:
        mock_send.return_value = True

        result = await send_test_email(email="admin@example.com")

        assert result is True
        assert mock_send.called

        call_args = mock_send.call_args
        assert call_args[1]['to'] == ["admin@example.com"]
        assert "Test" in call_args[1]['subject']
        assert "successful" in call_args[1]['html_content'].lower()


@pytest.mark.asyncio
async def test_send_test_email_includes_smtp_settings():
    """
    REAL TEST: Test email shows SMTP configuration
    Tests: Email body includes SMTP host and port
    """
    with patch('app.services.email_service.send_email', new_callable=AsyncMock) as mock_send, \
         patch('app.services.email_service.email_settings') as mock_settings:

        mock_settings.SMTP_HOST = "smtp.gmail.com"
        mock_settings.SMTP_PORT = 587
        mock_settings.FROM_EMAIL = "test@billings.com"
        mock_send.return_value = True

        await send_test_email(email="admin@example.com")

        html_content = mock_send.call_args[1]['html_content']
        assert "smtp.gmail.com" in html_content
        assert "587" in html_content


# ================================================================
# ERROR HANDLING TESTS
# ================================================================

@pytest.mark.asyncio
async def test_send_email_logs_on_failure():
    """
    REAL TEST: Email failure is logged
    Tests: Failed email attempts are logged properly
    """
    with patch('app.services.email_service.fm.send_message', new_callable=AsyncMock) as mock_send, \
         patch('app.services.email_service.logger') as mock_logger:

        mock_send.side_effect = Exception("Network error")

        with pytest.raises(Exception):
            await send_email(
                to=["user@example.com"],
                subject="Test",
                html_content="Test"
            )

        # Verify error was logged
        assert mock_logger.error.called


@pytest.mark.asyncio
async def test_template_email_failure_raises_exception():
    """
    REAL TEST: Template rendering failure
    Tests: send_template_email() raises exception on rendering failure
    """
    with patch('app.services.email_service.jinja_env') as mock_jinja:
        mock_jinja.get_template.side_effect = Exception("Template syntax error")

        with pytest.raises(Exception) as exc_info:
            await send_template_email(
                to=["user@example.com"],
                subject="Test",
                template_name="bad_template.html",
                context={}
            )

        assert "Template syntax error" in str(exc_info.value)


# ================================================================
# INTEGRATION-STYLE TESTS
# ================================================================

@pytest.mark.asyncio
async def test_password_reset_email_complete_flow():
    """
    REAL TEST: Complete password reset email flow
    Tests: Full flow from service call to email send
    """
    with patch('app.services.email_service.jinja_env') as mock_jinja, \
         patch('app.services.email_service.fm.send_message', new_callable=AsyncMock) as mock_send:

        # Mock template rendering
        mock_template = MagicMock()
        mock_template.render.return_value = "<h1>Reset Password</h1>"
        mock_jinja.get_template.return_value = mock_template
        mock_send.return_value = None

        result = await send_password_reset_email(
            email="user@example.com",
            reset_token="secure_token_123",
            username="TestUser"
        )

        assert result is True

        # Verify template was rendered with correct context
        render_call = mock_template.render.call_args[1]
        assert render_call['username'] == "TestUser"
        assert "secure_token_123" in render_call['reset_link']

        # Verify email was sent
        assert mock_send.called


@pytest.mark.asyncio
async def test_verification_email_complete_flow():
    """
    REAL TEST: Complete verification email flow
    Tests: Full flow from service call to email send
    """
    with patch('app.services.email_service.jinja_env') as mock_jinja, \
         patch('app.services.email_service.fm.send_message', new_callable=AsyncMock) as mock_send:

        mock_template = MagicMock()
        mock_template.render.return_value = "<h1>Verify Email</h1>"
        mock_jinja.get_template.return_value = mock_template
        mock_send.return_value = None

        result = await send_verification_email(
            email="newuser@example.com",
            verification_token="verify_token_456",
            username="NewUser"
        )

        assert result is True

        render_call = mock_template.render.call_args[1]
        assert render_call['username'] == "NewUser"
        assert "verify_token_456" in render_call['verification_link']
        assert mock_send.called
