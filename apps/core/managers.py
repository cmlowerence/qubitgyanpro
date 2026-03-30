# qubitgyanpro\apps\core\managers.py
from django.contrib.auth.base_user import BaseUserManager
from django.utils import timezone
from apps.core.constants import UserRole, UserStatus

class UserManager(BaseUserManager):
    """
    Custom manager for the User model.
    Handles user creation, superuser creation, and default role assignments.
    Includes soft-delete query filtering.
    """

    def get_queryset(self):
        return super().get_queryset()
    
    def active(self):
        return self.get_queryset().filter(is_deleted=False)

    def all_with_deleted(self):
        return super().get_queryset()

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address.")
        
        email = self.normalize_email(email)
        role = extra_fields.get("role", UserRole.STUDENT)
        status = extra_fields.get("status", UserStatus.PENDING)

        extra_fields.setdefault("role", role)
        extra_fields.setdefault("status", status)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
            
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("role", UserRole.ADMIN)
        extra_fields.setdefault("status", UserStatus.ACTIVE)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_verified", True)
        extra_fields.setdefault("is_onboarded", True)
        extra_fields.setdefault("mfa_enabled", False)

        if extra_fields.get("role") != UserRole.ADMIN:
            raise ValueError("Superuser must have role=ADMIN.")
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

