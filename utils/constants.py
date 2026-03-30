# qubitgyanpro\utils\constants.py

class SecurityConstants:
    """System-wide security and rate-limiting configuration constants."""
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 15
    OTP_EXPIRY_SECONDS = 600