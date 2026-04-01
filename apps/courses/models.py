# qubitgyanpro\apps\courses\models.py

from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.utils.text import slugify


class Course(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)

    description = models.TextField(blank=True)
    thumbnail_url = models.URLField(blank=True, null=True)

    is_published = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=["is_published"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="modules"
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    order = models.PositiveIntegerField(
        validators=[MinValueValidator(0)]
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

        constraints = [
            models.UniqueConstraint(
                fields=["course", "order"],
                name="unique_module_order_per_course"
            )
        ]

        indexes = [
            models.Index(fields=["course", "order"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.course_id})"


class Lesson(models.Model):
    CONTENT_TYPES = (
        ("VIDEO", "Video"),
        ("PDF", "PDF"),
        ("TEXT", "Text"),
    )

    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name="lessons"
    )

    title = models.CharField(max_length=255)

    content_type = models.CharField(
        max_length=20,
        choices=CONTENT_TYPES
    )

    content_data = models.JSONField(default=dict)

    order = models.PositiveIntegerField(
        validators=[MinValueValidator(0)]
    )

    duration_seconds = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def clean(self):
        if not isinstance(self.content_data, dict) or not self.content_data:
            raise ValidationError("content_data must be a non-empty dictionary.")

        if self.content_type in ["VIDEO", "PDF"]:
            url = self.content_data.get("url")
            if not url or not isinstance(url, str):
                raise ValidationError(f"{self.content_type} must include a valid 'url'.")

        elif self.content_type == "TEXT":
            text = self.content_data.get("text")
            if not text or not isinstance(text, str):
                raise ValidationError("TEXT must include valid 'text' content.")

    def save(self, *args, **kwargs):
        self.full_clean()  # 🔥 CRITICAL FIX
        super().save(*args, **kwargs)

    class Meta:
        ordering = ["order"]

        constraints = [
            models.UniqueConstraint(
                fields=["module", "order"],
                name="unique_lesson_order_per_module"
            )
        ]

        indexes = [
            models.Index(fields=["module", "order"]),
            models.Index(fields=["content_type"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.module_id})"
    
    