from uuid import UUID
from django.db import transaction
from rest_framework.exceptions import ValidationError
import logging

from events.models import Event, EventStatus
from events.dispatcher import process_event, MAX_RETRIES
from events.selectors import get_retryable_failed_events

from apps.core.constants import UserRole, UserStatus
from apps.security.models import AdminAuditLog

logger = logging.getLogger(__name__)


def _validate_admin(user):
    if not user:
        raise ValidationError("Authentication required.")

    if user.role != UserRole.ADMIN:
        raise ValidationError("Admin privileges required.")

    if not user.is_active or user.is_deleted or user.status != UserStatus.ACTIVE:
        raise ValidationError("Inactive or invalid admin account.")


def _validate_retryable(event: Event):
    if not event:
        raise ValidationError("Event not found.")

    if event.status != EventStatus.FAILED:
        raise ValidationError("Only failed events can be retried.")

    if event.attempts >= MAX_RETRIES:
        raise ValidationError("Max retry attempts reached.")


# =========================
# RETRY SINGLE EVENT
# =========================

def retry_event(event_id: UUID, admin_user) -> dict:
    """
    Retry a single failed event.
    Includes audit logging.
    """

    _validate_admin(admin_user)

    # Lock event row
    with transaction.atomic():
        event = Event.objects.select_for_update().filter(id=event_id).first()
        _validate_retryable(event)

        attempt_before = event.attempts

    # ⚠️ Call outside transaction (VERY IMPORTANT)
    process_event(event_id)

    # Audit log AFTER processing
    AdminAuditLog.objects.create(
        admin=admin_user,
        action=AdminAuditLog.Action.EVENT_RETRY,
        target_type=AdminAuditLog.TargetType.EVENT,
        target_id=event_id,
        metadata={
            "event_type": event.event_type,
            "attempt_before": attempt_before,
        }
    )

    return {
        "event_id": str(event_id),
        "status": "retry_triggered"
    }


# =========================
# RETRY ALL FAILED EVENTS
# =========================

def retry_failed_events_service(admin_user) -> dict:
    """
    Retry all eligible failed events.
    """

    _validate_admin(admin_user)

    events = list(get_retryable_failed_events(MAX_RETRIES))

    if not events:
        return {"retried": 0}

    retried_count = 0

    for event in events:
        try:
            process_event(event.id)
            retried_count += 1

        except Exception as e:
            logger.exception(f"Failed retry for event {event.id}")
            continue

    # Audit log
    AdminAuditLog.objects.create(
        admin=admin_user,
        action=AdminAuditLog.Action.EVENT_BULK_RETRY,
        metadata={
            "total_retried": retried_count,
        }
    )

    return {
        "retried": retried_count
    }