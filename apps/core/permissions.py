# qubitgyanpro/apps/core/permissions.py

from rest_framework.permissions import BasePermission
from apps.core.constants import UserRole, UserStatus


class BaseActivePermission(BasePermission):
    """
    Base permission:
    Ensures user is authenticated, active, not deleted, and ACTIVE status.
    """

    def has_permission(self, request, view):
        user = request.user

        return bool(
            user and
            user.is_authenticated and
            user.is_active and
            not getattr(user, 'is_deleted', False) and
            user.status == UserStatus.ACTIVE
        )


class IsAuthenticatedUser(BaseActivePermission):
    """Authenticated + active users only."""
    pass


class IsStudent(BaseActivePermission):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == UserRole.STUDENT


class IsStaff(BaseActivePermission):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == UserRole.STAFF


class IsAdmin(BaseActivePermission):
    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.role == UserRole.ADMIN


class IsValidTokenVersion(BasePermission):
    """
    Ensures token version matches user's current auth_token_version.
    (Extra safety layer — optional if using CustomJWTAuthentication)
    """

    def has_permission(self, request, view):
        user = request.user
        token = request.auth

        if not user or not user.is_authenticated:
            return False

        if not token:
            return False

        try:
            token_version = token.get("token_version")
        except Exception:
            return False

        return token_version == user.auth_token_version