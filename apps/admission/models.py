# qubitgyanpro\apps\admission\models.py

from django.db import models
from django.utils import timezone
import uuid


class AdmissionStatus(models.TextChoices):
    PENDING = "PENDING", "Pending"
    UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
    APPROVED = "APPROVED", "Approved"
    REJECTED = "REJECTED", "Rejected"


class AdmissionSource(models.TextChoices):
    WEB = "WEB", "Web"
    TELEGRAM = "TELEGRAM", "Telegram"
    ADMIN = "ADMIN", "Admin"


class Admission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Core Identity
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)

    # Contact
    phone_number = models.CharField(max_length=20, null=True, blank=True)

    # Telegram (MANDATORY)
    telegram_user_id = models.CharField(max_length=100, unique=True)
    telegram_username = models.CharField(max_length=150, null=True, blank=True)
    telegram_verified = models.BooleanField(default=False)
    telegram_verified_at = models.DateTimeField(null=True, blank=True)

    # Academic Intent
    target_exam = models.CharField(max_length=100, null=True, blank=True)
    preferred_language = models.CharField(max_length=50, default="English")

    # System State
    status = models.CharField(
        max_length=20,
        choices=AdmissionStatus.choices,
        default=AdmissionStatus.PENDING
    )

    source = models.CharField(
        max_length=20,
        choices=AdmissionSource.choices,
        default=AdmissionSource.WEB
    )

    # Linking (IMPORTANT)
    user = models.OneToOneField(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='admission'
    )

    # Review Tracking
    reviewed_by = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_admissions'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)

    # Audit
    created_by = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_admissions'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['status']),
            models.Index(fields=['telegram_user_id']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.email} - {self.status}"

    # =========================
    # DOMAIN METHODS
    # =========================

    def mark_under_review(self, reviewer):
        self.status = AdmissionStatus.UNDER_REVIEW
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.save(update_fields=['status', 'reviewed_by', 'reviewed_at'])

    def approve(self, reviewer, user):
        self.status = AdmissionStatus.APPROVED
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.user = user
        self.rejection_reason = None
        self.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'user', 'rejection_reason'])

    def reject(self, reviewer, reason: str):
        self.status = AdmissionStatus.REJECTED
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.rejection_reason = reason
        self.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'rejection_reason'])