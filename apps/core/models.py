# qubitgyanpro\apps\core\models.py
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.managers import UserManager
from apps.core.constants import (
    UserRole, 
    UserStatus, 
    Gender, 
    EmploymentType, 
    AcademicStatus, 
    AdminTier
)


class User(AbstractBaseUser, PermissionsMixin):

    # Primary Identity
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_("email address"), unique=True, max_length=255)
    
    # Classification
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.STUDENT)
    status = models.CharField(max_length=20, choices=UserStatus.choices, default=UserStatus.PENDING)
    
    # Core States
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_onboarded = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    # Security & Authentication Tracking
    mfa_enabled = models.BooleanField(default=False)
    mfa_secret = models.CharField(max_length=255, null=True, blank=True)
    password_changed_at = models.DateTimeField(null=True, blank=True)
    failed_login_attempts = models.PositiveSmallIntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_device = models.CharField(max_length=255, null=True, blank=True)
    login_count = models.PositiveIntegerField(default=0)
    last_login = models.DateTimeField(null=True, blank=True)
    auth_token_version = models.PositiveIntegerField(default=0)

    # Audit & Compliance
    created_by = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='created_users'
    )
    updated_by = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_users'
    )
    date_joined = models.DateTimeField(default=timezone.now)
    last_activity = models.DateTimeField(default=timezone.now)
    deleted_at = models.DateTimeField(null=True, blank=True)
    terms_accepted_at = models.DateTimeField(null=True, blank=True)
    privacy_policy_accepted_at = models.DateTimeField(null=True, blank=True)

    # Telegram Integration
    telegram_user_id = models.CharField(max_length=100, null=True, blank=True, unique=True, db_index=True)
    telegram_chat_id = models.CharField(max_length=100, null=True, blank=True)
    telegram_username = models.CharField(max_length=150, null=True, blank=True)
    telegram_verified = models.BooleanField(default=False)
    telegram_linked_at = models.DateTimeField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


    def set_password(self, raw_password):
        super().set_password(raw_password)
        self.password_changed_at = timezone.now()
    
    def clean(self):
        errors = {}
        if self.role == UserRole.ADMIN and not self.is_staff:
            errors['is_staff'] = _("Admin must have is_staff=True")

        if self.role == UserRole.STAFF and self.is_superuser:
            errors['is_superuser'] = _("Staff cannot be superuser")
        
        if self.telegram_verified and not self.telegram_user_id:
            errors['telegram_user_id'] = _("Telegram verified but no user_id linked")
            
        if errors:
            raise ValidationError(errors)
        
    def is_account_locked(self):
        if self.account_locked_until:
            return self.account_locked_until and timezone.now() < self.account_locked_until
        return False

    def update_activity(self):
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        if not kwargs.get('update_fields'):
            self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        indexes = [
            models.Index(fields=['role', 'status']),
            models.Index(fields=['role']),
            models.Index(fields=['status']),
            models.Index(fields=['telegram_user_id']),
            models.Index(fields=['is_deleted']),
        ]

    def __str__(self):
        return f"{self.email or 'NoEmail'} - {self.role}"
    
    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.is_active = False
        self.status = UserStatus.SUSPENDED
        self.save(update_fields=[
            'is_deleted', 'deleted_at', 'is_active', 'status'
        ])


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Personal Information
    full_name = models.CharField(max_length=255, blank=True)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=20, choices=Gender.choices, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    
    # Location
    address_line_1 = models.CharField(max_length=255, null=True, blank=True)
    address_line_2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    timezone = models.CharField(max_length=50, default="UTC")
    locale = models.CharField(max_length=10, default="en")
    
    # Assets & Links
    profile_image = models.URLField(max_length=1024, null=True, blank=True)
    linkedin_url = models.URLField(max_length=1024, null=True, blank=True)
    github_url = models.URLField(max_length=1024, null=True, blank=True)
    personal_website = models.URLField(max_length=1024, null=True, blank=True)

    # Emergency Contact
    emergency_contact_name = models.CharField(max_length=255, null=True, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, null=True, blank=True)
    emergency_contact_relation = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = _("User Profile")
        verbose_name_plural = _("User Profiles")

    def __str__(self):
        return f"Profile: {self.full_name} ({self.user.email})"


class StudentProfile(models.Model):
    def clean(self):
        if self.user.role != UserRole.STUDENT:
            raise ValidationError({'user': _("Profile can only be assigned to STUDENT users")})
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    
    # Academic Identifiers
    enrollment_id = models.CharField(max_length=100, unique=True)
    batch_year = models.PositiveSmallIntegerField(null=True, blank=True)
    institution_name = models.CharField(max_length=255, null=True, blank=True)
    expected_graduation_year = models.PositiveSmallIntegerField(null=True, blank=True)
    
    # Core Learning Data
    target_exam = models.CharField(max_length=100, null=True, blank=True)
    current_level = models.CharField(max_length=100, null=True, blank=True)
    academic_status = models.CharField(max_length=50, choices=AcademicStatus.choices, default=AcademicStatus.GOOD_STANDING)
    preferred_language = models.CharField(max_length=50, default="English")
    learning_style = models.CharField(max_length=100, null=True, blank=True)
    accessibility_requirements = models.TextField(null=True, blank=True)
    
    # Guardian Information (For minors/compliance)
    guardian_name = models.CharField(max_length=255, null=True, blank=True)
    guardian_phone = models.CharField(max_length=20, null=True, blank=True)
    guardian_email = models.EmailField(max_length=255, null=True, blank=True)

    joined_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not kwargs.get('update_fields'):
            self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Student Profile")
        verbose_name_plural = _("Student Profiles")
        indexes = [
            models.Index(fields=['enrollment_id']),
            models.Index(fields=['batch_year']),
            models.Index(fields=['academic_status']),
        ]

    def __str__(self):
        return f"Student: {self.enrollment_id} - {self.user.email}"


class StaffProfile(models.Model):
    def clean(self):
        if self.user.role != UserRole.STAFF:
            raise ValidationError({'user': _("Profile can only be assigned to STAFF users")})
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    
    # HR Identifiers
    employee_id = models.CharField(max_length=100, unique=True)
    department = models.CharField(max_length=150)
    designation = models.CharField(max_length=150)
    employment_type = models.CharField(max_length=50, choices=EmploymentType.choices, default=EmploymentType.FULL_TIME)
    
    # Hierarchy & Logistics
    reporting_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='direct_reports')
    work_location = models.CharField(max_length=255, null=True, blank=True)
    shift_timing = models.CharField(max_length=100, null=True, blank=True)
    
    # Professional Data
    skills = models.JSONField(default=list, blank=True, help_text=_("List of professional skills/technologies"))
    hired_at = models.DateTimeField(default=timezone.now)
    contract_end_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not kwargs.get('update_fields'):
            self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Staff Profile")
        verbose_name_plural = _("Staff Profiles")
        indexes = [
            models.Index(fields=['employee_id']),
            models.Index(fields=['department']),
        ]

    def __str__(self):
        return f"Staff: {self.employee_id} - {self.user.email}"


class AdminProfile(models.Model):
    def clean(self):
        if self.user.role != UserRole.ADMIN:
            raise ValidationError({'user': _("Profile can only be assigned to ADMIN users")})
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin_profile')
    admin_tier = models.CharField(max_length=50, choices=AdminTier.choices, default=AdminTier.SYSTEM_ADMIN)
    super_admin = models.BooleanField(default=False)
    last_audit_review_at = models.DateTimeField(null=True, blank=True)
    system_notifications_enabled = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not kwargs.get('update_fields'):
            self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Admin Profile")
        verbose_name_plural = _("Admin Profiles")

    def __str__(self):
        return f"Admin ({self.admin_tier}): {self.user.email}"


class StaffPermission(models.Model):

    def clean(self):
        if self.user.role != UserRole.STAFF:
            raise ValidationError({'user': _("Permissions can only be assigned to STAFF users")})


    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_permission')
    role_level = models.PositiveSmallIntegerField(default=1)
    
    # Granular Permissions
    can_approve_admissions = models.BooleanField(default=False)
    can_edit_content = models.BooleanField(default=False)
    can_manage_users = models.BooleanField(default=False)
    can_view_reports = models.BooleanField(default=False)
    can_manage_billing = models.BooleanField(default=False)
    can_manage_roles = models.BooleanField(default=False)
    can_bypass_mfa = models.BooleanField(default=False)
    can_export_data = models.BooleanField(default=False)
    
    # Tracking
    permissions_updated_at = models.DateTimeField(auto_now=True)
    permissions_updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='granted_permissions')

    def save(self, *args, **kwargs):
        if not kwargs.get('update_fields'):
            self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Staff Permission")
        verbose_name_plural = _("Staff Permissions")

    def __str__(self):
        return f"Permissions Level {self.role_level}: {self.user.email}"

