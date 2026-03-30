import uuid
from django.db.models.signals import post_save
from django.db import transaction
from django.dispatch import receiver
from django.utils import timezone

from apps.core.models import (
    User,
    UserProfile,
    StudentProfile,
    StaffProfile,
    AdminProfile,
    StaffPermission
)
from apps.core.constants import UserRole, EmploymentType


@receiver(post_save, sender=User)
def create_user_profiles(sender, instance, created, **kwargs):
    if not created:
        return

    with transaction.atomic():
        UserProfile.objects.get_or_create(
            user=instance,
            defaults={"full_name": instance.email.split("@")[0] if instance.email else "User"}
        )

        if instance.role == UserRole.STUDENT:
            StudentProfile.objects.create(
                user=instance,
                enrollment_id=f"STU-{uuid.uuid4().hex[:10]}".upper(),
                preferred_language="English",
                joined_at=timezone.now()
            )

        elif instance.role == UserRole.STAFF:
            StaffProfile.objects.create(
                user=instance,
                employee_id=f"EMP-{uuid.uuid4().hex[:10]}".upper(),
                department="General",
                designation="Staff",
                employment_type=EmploymentType.FULL_TIME,
                hired_at=timezone.now()
            )
            StaffPermission.objects.create(
                user=instance,
                role_level=1
            )

        elif instance.role == UserRole.ADMIN:
            AdminProfile.objects.create(user=instance)