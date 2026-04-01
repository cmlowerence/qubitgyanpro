# qubitgyanpro\events\selectors.py

from typing import Optional
from uuid import UUID
from datetime import datetime

from django.db.models import QuerySet, Count

from events.models import Event, EventStatus
from events.event_types import EventType


def get_events(
    status: Optional[str] = None,
    event_type: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
) -> QuerySet[Event]:
    """
    Fetch events with optional filtering.
    Uses created_at as the primary time dimension.
    """

    qs = Event.objects.all()

    if status:
        if status not in EventStatus.values:
            return Event.objects.none()
        qs = qs.filter(status=status)

    if event_type:
        if event_type not in vars(EventType).values():
            return Event.objects.none()
        qs = qs.filter(event_type=event_type)

    if date_from:
        qs = qs.filter(created_at__gte=date_from)

    if date_to:
        qs = qs.filter(created_at__lte=date_to)

    return qs.order_by("-created_at")


def get_event_by_id(event_id: UUID) -> Optional[Event]:
    """
    Fetch a single event by ID.
    """

    if not event_id:
        return None

    return Event.objects.filter(id=event_id).first()


def get_event_metrics() -> dict:
    """
    Returns aggregated event statistics for dashboard.
    """

    total = Event.objects.count()

    status_counts = (
        Event.objects.values("status")
        .annotate(count=Count("id"))
    )

    metrics = {
        "total": total,
        "pending": 0,
        "processing": 0,
        "processed": 0,
        "failed": 0,
    }

    for item in status_counts:
        status = item["status"]
        count = item["count"]

        if status == EventStatus.PENDING:
            metrics["pending"] = count
        elif status == EventStatus.PROCESSING:
            metrics["processing"] = count
        elif status == EventStatus.PROCESSED:
            metrics["processed"] = count
        elif status == EventStatus.FAILED:
            metrics["failed"] = count

    metrics["success_rate"] = round(
        (metrics["processed"] / total) * 100, 2
    ) if total > 0 else 0.0

    return metrics

def get_retryable_failed_events(max_retries: int) -> QuerySet[Event]:
    """
    Fetch failed events eligible for retry.
    """

    return Event.objects.filter(
        status=EventStatus.FAILED,
        attempts__lt=max_retries
    ).order_by("created_at")