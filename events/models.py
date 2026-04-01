# qubitgyanpro\events\models.py

from django.db import models
from django.utils import timezone
import uuid


class EventStatus(models.TextChoices):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    event_type = models.CharField(max_length=100)
    payload = models.JSONField()

    status = models.CharField(
        max_length=20,
        choices=EventStatus.choices,
        default=EventStatus.PENDING
    )

    attempts = models.PositiveIntegerField(default=0)
    last_error = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["event_type"]),
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"{self.event_type} | {self.status} | {self.attempts}"

