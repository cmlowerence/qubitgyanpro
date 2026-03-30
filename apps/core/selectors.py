# qubitgyanpro/apps/core/selectors.py

from typing import Optional
from uuid import UUID
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager

from apps.core.models import User
from apps.core.constants import UserStatus


def get_user_by_email(email: str) -> Optional[User]:
    """Fetch a user by normalized email."""
    if not email:
        return None

    email = BaseUserManager().normalize_email(email)
    return User.objects.filter(email=email).first()


def get_active_user(email: str) -> Optional[User]:
    """
    Fetch user if:
    - active
    - not deleted
    - status ACTIVE
    - not locked
    """
    if not email:
        return None

    email = BaseUserManager().normalize_email(email)

    user = User.objects.filter(
        email=email,
        status=UserStatus.ACTIVE,
        is_active=True,
        is_deleted=False
    ).first()

    if user and user.is_account_locked():
        return None

    return user


def get_user_with_profiles(user_id: UUID) -> Optional[User]:
    """
    Fetch user with all related profiles (optimized query).
    Prevents N+1 queries.
    """
    return User.objects.select_related(
        'profile',
        'student_profile',
        'staff_profile',
        'admin_profile',
        'staff_permission'
    ).filter(
        id=user_id,
        is_deleted=False
    ).first()