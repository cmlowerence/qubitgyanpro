# qubitgyanpro\events\dispatcher.py

import logging
from typing import Callable, Dict, List

from django.db import transaction
from django.utils import timezone

from events.models import Event, EventStatus

logger = logging.getLogger(__name__)

_EVENT_HANDLERS: Dict[str, List[Callable]] = {}

MAX_RETRIES = 3


def register_event(event_type: str, handler: Callable):
    if event_type not in _EVENT_HANDLERS:
        _EVENT_HANDLERS[event_type] = []

    _EVENT_HANDLERS[event_type].append(handler)


def create_event(event_type: str, payload: dict) -> Event:
    return Event.objects.create(
        event_type=event_type,
        payload=payload
    )


def dispatch_event(event_type: str, payload: dict):
    event = create_event(event_type, payload)
    process_event(event.id)


def process_event(event_id):
    """
    Safe event processing with locking and retry protection.
    """
    with transaction.atomic():
        try:
            event = Event.objects.select_for_update().get(id=event_id)
        except Event.DoesNotExist:
            return

        if event.status == EventStatus.PROCESSED:
            return

        if event.attempts >= MAX_RETRIES:
            return

        handlers = _EVENT_HANDLERS.get(event.event_type)

        if not handlers:
            event.status = EventStatus.FAILED
            event.last_error = "No handlers registered"
            event.save(update_fields=["status", "last_error"])
            return

        event.status = EventStatus.PROCESSING
        event.attempts += 1
        event.save(update_fields=["status", "attempts"])

    try:
        for handler in handlers:
            handler(event.payload)

        Event.objects.filter(id=event_id).update(
            status=EventStatus.PROCESSED,
            processed_at=timezone.now()
        )

    except Exception as e:
        logger.exception(f"[EVENT FAILED] {event.event_type}")

        Event.objects.filter(id=event_id).update(
            status=EventStatus.FAILED,
            last_error=str(e)
        )

