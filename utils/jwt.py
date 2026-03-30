# qubitgyanpro/utils/authentication.py

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from apps.core.constants import UserStatus


class CustomJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that validates:
    - token_version (for forced logout)
    - user status
    - deletion state
    """

    def get_user(self, validated_token):
        user = super().get_user(validated_token)

        if "token_version" not in validated_token:
            raise AuthenticationFailed("Invalid token payload.")

        token_version = validated_token["token_version"]

        if token_version != user.auth_token_version:
            raise AuthenticationFailed("Token expired. Please login again.")

        if not user.is_active or user.is_deleted:
            raise AuthenticationFailed("User account is inactive.")

        if user.status != UserStatus.ACTIVE:
            raise AuthenticationFailed("User account is not active.")

        return user