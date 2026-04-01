# qubitgyanpro\apps\progress\models.py

import uuid
from django.db import models


class LessonProgress(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        "core.User",
        on_delete=models.CASCADE,
        related_name="lesson_progress"
    )

    lesson = models.ForeignKey(
        "courses.Lesson",
        on_delete=models.CASCADE,
        related_name="progress_records"
    )

    is_completed = models.BooleanField(default=False)

    completed_at = models.DateTimeField(null=True, blank=True)

    last_accessed_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "lesson"],
                name="unique_user_lesson_progress"
            )
        ]

        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["lesson"]),
            models.Index(fields=["is_completed"]),
            models.Index(fields=["user", "lesson"]),
        ]

    def __str__(self):
        return f"{self.user_id}:{self.lesson_id}"