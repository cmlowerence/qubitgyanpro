# qubitgyanpro/services\admission_service.py

from django.utils import timezone
from django.db import transaction
from django.contrib.auth.base_user import BaseUserManager
from rest_framework.exceptions import ValidationError

from apps.admission.models import Admission, AdmissionStatus
from apps.core.models import User
from apps.core.constants import UserRole, UserStatus

from events.dispatcher import dispatch_event
from events.event_types import EventType


def create_admission(data: dict, source: str = "WEB", created_by=None) -> Admission:
    raw_email = data.get("email")
    telegram_user_id = data.get("telegram_user_id")

    if not raw_email:
        raise ValidationError("Email is required.")

    if not telegram_user_id:
        raise ValidationError("Telegram user ID is required.")

    email = BaseUserManager().normalize_email(raw_email.strip())

    if Admission.objects.filter(email=email).exists():
        raise ValidationError("Admission already exists.")

    if Admission.objects.filter(telegram_user_id=str(telegram_user_id)).exists():
        raise ValidationError("Telegram already used.")

    admission = Admission.objects.create(
        email=email,
        full_name=data.get("full_name"),
        phone_number=data.get("phone_number"),
        telegram_user_id=str(telegram_user_id),
        telegram_username=data.get("telegram_username"),
        target_exam=data.get("target_exam"),
        preferred_language=data.get("preferred_language", "English"),
        source=source,
        created_by=created_by
    )

    transaction.on_commit(lambda: dispatch_event(
        EventType.ADMISSION_CREATED,
        {"admission": admission}
    ))

    return admission


def mark_under_review(admission: Admission, reviewer: User) -> Admission:
    if reviewer.role not in [UserRole.ADMIN, UserRole.STAFF]:
        raise ValidationError("Permission denied.")

    if admission.status != AdmissionStatus.PENDING:
        raise ValidationError("Only pending admissions allowed.")

    admission.mark_under_review(reviewer)

    transaction.on_commit(lambda: dispatch_event(
        EventType.ADMISSION_UNDER_REVIEW,
        {"admission": admission}
    ))

    return admission


@transaction.atomic
def approve_admission(admission: Admission, reviewer: User) -> User:
    if reviewer.role not in [UserRole.ADMIN, UserRole.STAFF]:
        raise ValidationError("Permission denied.")

    admission = Admission.objects.select_for_update().get(id=admission.id)

    if admission.status not in [AdmissionStatus.PENDING, AdmissionStatus.UNDER_REVIEW]:
        raise ValidationError("Cannot approve.")

    if admission.user:
        raise ValidationError("Already approved.")

    if User.objects.filter(email=admission.email).exists():
        raise ValidationError("User exists.")

    user = User.objects.create_user(
        email=admission.email,
        password=None,
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
        is_verified=True
    )

    user.telegram_user_id = admission.telegram_user_id
    user.telegram_username = admission.telegram_username
    user.telegram_verified = admission.telegram_verified
    user.telegram_linked_at = timezone.now()

    user.save(update_fields=[
        'telegram_user_id',
        'telegram_username',
        'telegram_verified',
        'telegram_linked_at'
    ])

    admission.approve(reviewer, user)

    transaction.on_commit(lambda: dispatch_event(
        EventType.ADMISSION_APPROVED,
        {"admission": admission, "user": user}
    ))

    return user


def reject_admission(admission: Admission, reviewer: User, reason: str) -> Admission:
    if reviewer.role not in [UserRole.ADMIN, UserRole.STAFF]:
        raise ValidationError("Permission denied.")

    if admission.status not in [AdmissionStatus.PENDING, AdmissionStatus.UNDER_REVIEW]:
        raise ValidationError("Cannot reject.")

    if not reason:
        raise ValidationError("Reason required.")

    admission.reject(reviewer, reason)

    transaction.on_commit(lambda: dispatch_event(
        EventType.ADMISSION_REJECTED,
        {"admission": admission}
    ))

    return admission


def get_admission_by_id(admission_id):
    return Admission.objects.select_related('user', 'reviewed_by').filter(id=admission_id).first()


def list_admissions(status=None):
    qs = Admission.objects.select_related('user', 'reviewed_by')

    if status:
        if status not in AdmissionStatus.values:
            raise ValidationError("Invalid status.")
        qs = qs.filter(status=status)

    return qs.order_by('-created_at')

