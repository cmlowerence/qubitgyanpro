# qubitgyanpro\events\retry.py

from django.utils import timezone
from django.db.models import F

from events.models import Event, EventStatus
from events.dispatcher import process_event

MAX_RETRIES = 3


def retry_failed_events():
    failed_events = Event.objects.filter(
        status=EventStatus.FAILED,
        attempts__lt=MAX_RETRIES
    ).order_by("created_at")

    for event in failed_events:
        process_event(event.id)

        