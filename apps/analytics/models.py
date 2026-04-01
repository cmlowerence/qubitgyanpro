# qubitgyanpro\apps\analytics\models.py

import uuid
from django.db import models


class UserLessonInteraction(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        "core.User",
        on_delete=models.CASCADE,
        related_name="lesson_interactions"
    )

    lesson = models.ForeignKey(
        "courses.Lesson",
        on_delete=models.CASCADE,
        related_name="interactions"
    )

    completed = models.BooleanField(default=False)

    time_spent = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "lesson"],
                name="unique_user_lesson_interaction"
            )
        ]

        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["lesson"]),
            models.Index(fields=["completed"]),
            models.Index(fields=["user", "completed"]),
        ]

        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user_id}:{self.lesson_id}"