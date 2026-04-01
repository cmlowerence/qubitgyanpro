# qubitgyanpro/apps/security/models.py

import uuid
from django.db import models


class AdminAuditLog(models.Model):

    class Action(models.TextChoices):
        EVENT_RETRY = "EVENT_RETRY", "Event Retry"
        EVENT_BULK_RETRY = "EVENT_BULK_RETRY", "Bulk Event Retry"

        COURSE_CREATED = "COURSE_CREATED", "Course Created"
        COURSE_PUBLISHED = "COURSE_PUBLISHED", "Course Published"

        MODULE_CREATED = "MODULE_CREATED", "Module Created"

        LESSON_CREATED = "LESSON_CREATED", "Lesson Created"
        LESSON_UPDATED = "LESSON_UPDATED", "Lesson Updated"

    class TargetType(models.TextChoices):
        EVENT = "EVENT", "Event"
        COURSE = "COURSE", "Course"
        MODULE = "MODULE", "Module"
        LESSON = "LESSON", "Lesson"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    admin = models.ForeignKey(
        'core.User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='admin_actions'
    )

    action = models.CharField(max_length=50, choices=Action.choices)

    target_type = models.CharField(
        max_length=50,
        choices=TargetType.choices,
        null=True,
        blank=True
    )

    target_id = models.UUIDField(null=True, blank=True)

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["admin"]),
            models.Index(fields=["action"]),
            models.Index(fields=["target_type"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["target_type", "target_id"]),
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} | admin={self.admin_id} | target={self.target_type}:{self.target_id}"