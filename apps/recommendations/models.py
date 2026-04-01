# qubitgyanpro\apps\recommendations\models.py

import uuid
from django.db import models


class UserRecommendation(models.Model):

    class Type(models.TextChoices):
        CONTINUE = "CONTINUE", "Continue Learning"
        NEXT_MODULE = "NEXT_MODULE", "Next Module"
        REVISION = "REVISION", "Revision"
        WEAK_AREA = "WEAK_AREA", "Weak Area"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        "core.User",
        on_delete=models.CASCADE,
        related_name="recommendations"
    )

    lesson = models.ForeignKey(
        "courses.Lesson",
        on_delete=models.CASCADE,
        related_name="recommended_to"
    )

    recommendation_type = models.CharField(
        max_length=50,
        choices=Type.choices
    )

    score = models.FloatField()

    reason = models.CharField(max_length=255, blank=True)

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "lesson"],
                name="unique_user_lesson_recommendation"
            )
        ]

        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["score"]),
            models.Index(fields=["user", "score"]),
            models.Index(fields=["recommendation_type"]),
        ]

        ordering = ["-score", "-created_at"]

    def __str__(self):
        return f"{self.user_id}:{self.lesson_id}"