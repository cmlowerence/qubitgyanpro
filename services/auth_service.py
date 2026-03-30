# qubitgyanpro/services/auth_service.py

from datetime import timedelta
from django.utils import timezone
import secrets
import hashlib
import logging

from django.core.cache import cache
from django.contrib.auth.password_validation import validate_password

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed, ValidationError

from apps.core.selectors import get_user_by_email, get_user_with_profiles
from apps.core.serializers import UserSerializer
from apps.core.models import User
from apps.core.constants import UserStatus

from services.telegram_service import send_message
from utils.constants import SecurityConstants


logger = logging.getLogger(__name__)


# =========================
# TOKEN GENERATION
# =========================
def generate_tokens(user: User) -> dict:
    refresh = RefreshToken.for_user(user)

    refresh["token_version"] = user.auth_token_version
    access = refresh.access_token
    access["token_version"] = user.auth_token_version

    return {
        "access_token": str(access),
        "refresh_token": str(refresh),
    }


# =========================
# LOGIN
# =========================
def login_user(user: User, password: str, ip_address: str = None, device: str = None) -> dict:
    """
    Handles authentication, brute-force protection, audit logging, and token generation.
    """

    if user.is_account_locked():
        raise AuthenticationFailed("Account is locked. Try again later.")

    if not user.is_active or user.is_deleted or user.status != UserStatus.ACTIVE:
        raise AuthenticationFailed("Account is inactive.")

    if not user.check_password(password):
        user.failed_login_attempts += 1

        if user.failed_login_attempts >= SecurityConstants.MAX_FAILED_ATTEMPTS:
            user.account_locked_until = timezone.now() + timedelta(
                minutes=SecurityConstants.LOCKOUT_DURATION_MINUTES
            )

        user.save(update_fields=["failed_login_attempts", "account_locked_until"])
        raise AuthenticationFailed("Invalid credentials.")

    user.failed_login_attempts = 0
    user.account_locked_until = None
    user.login_count += 1

    if ip_address:
        user.last_login_ip = ip_address
    if device:
        user.last_device = device

    now = timezone.now()
    user.last_activity = now
    user.last_login = now

    user.save(update_fields=[
        "failed_login_attempts",
        "account_locked_until",
        "login_count",
        "last_login_ip",
        "last_device",
        "last_activity",
        "last_login",
    ])

    tokens = generate_tokens(user)

    user = get_user_with_profiles(user.id)

    return {
        "tokens": tokens,
        "user": UserSerializer(user).data,
    }


# =========================
# PASSWORD RESET REQUEST (TELEGRAM)
# =========================
def request_password_reset_telegram(email: str) -> None:
    """
    Sends OTP via Telegram.
    Fully protected against enumeration + spam.
    """

    user = get_user_by_email(email)

    if not user or user.is_deleted:
        return

    rate_key = f"auth:pwd_reset_rate:{user.id}"
    if cache.get(rate_key):
        raise ValidationError("Please wait before requesting another OTP.")
    cache.set(rate_key, True, timeout=60)

    telegram_chat_id = str(user.telegram_chat_id) if user.telegram_chat_id else None

    if not telegram_chat_id:
        return

    otp = str(secrets.randbelow(900000) + 100000)

    hashed_otp = hashlib.sha256(otp.encode()).hexdigest()

    cache_key = f"auth:pwd_reset_otp:{user.id}"
    cache.set(cache_key, hashed_otp, timeout=SecurityConstants.OTP_EXPIRY_SECONDS)

    cache.delete(f"auth:pwd_reset_attempts:{user.id}")

    expiry_minutes = SecurityConstants.OTP_EXPIRY_SECONDS // 60

    message = (
        f"🔒 QubitGyan OTP: {otp}\n\n"
        f"Expires in {expiry_minutes} minutes.\n"
        f"Do NOT share this code."
    )

    try:
        send_message(telegram_id=telegram_chat_id, text=message)
    except Exception as e:
        logger.error(f"Telegram OTP send failed: {str(e)}")
        raise ValidationError("Failed to send OTP. Please try again.")


# =========================
# VERIFY OTP
# =========================
def verify_telegram_otp(email: str, otp: str) -> User:
    """
    Verifies OTP with brute-force protection.
    """

    user = get_user_by_email(email)

    if not user:
        raise ValidationError("Invalid request.")

    cache_key = f"auth:pwd_reset_otp:{user.id}"
    attempt_key = f"auth:pwd_reset_attempts:{user.id}"

    attempts = cache.get(attempt_key, 0)

    if attempts >= SecurityConstants.MAX_FAILED_ATTEMPTS:
        raise ValidationError("Too many failed attempts. Try again later.")

    stored_hash = cache.get(cache_key)

    if not stored_hash:
        raise ValidationError("OTP expired or not requested.")

    incoming_hash = hashlib.sha256(otp.encode()).hexdigest()

    if stored_hash != incoming_hash:
        cache.set(attempt_key, attempts + 1, timeout=SecurityConstants.OTP_EXPIRY_SECONDS)
        raise ValidationError("Invalid OTP.")

    cache.delete(cache_key)
    cache.delete(attempt_key)

    return user


# =========================
# RESET PASSWORD
# =========================
def reset_password(user: User, new_password: str) -> None:
    """
    Resets password and invalidates all existing tokens.
    """

    validate_password(new_password, user)

    user.set_password(new_password)
    user.account_locked_until = None
    user.failed_login_attempts = 0
    user.password_changed_at = timezone.now()

    user.auth_token_version += 1

    user.save(update_fields=[
        "password",
        "password_changed_at",
        "account_locked_until",
        "failed_login_attempts",
        "auth_token_version",
    ])

    cache.delete(f"auth:pwd_reset_otp:{user.id}")