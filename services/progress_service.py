# qubitgyanpro\services\progress_service.py

from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from apps.progress.models import LessonProgress
from apps.courses.models import Lesson

from events.dispatcher import dispatch_event
from events.event_types import EventType


@transaction.atomic
def mark_lesson_complete(*, user, lesson_id):
    lesson = Lesson.objects.select_for_update().filter(
        id=lesson_id,
        is_active=True
    ).first()

    if not lesson:
        raise ValidationError("Lesson not found.")

    progress, _ = LessonProgress.objects.select_for_update().get_or_create(
        user=user,
        lesson=lesson
    )

    if progress.is_completed:
        return progress

    progress.is_completed = True
    progress.completed_at = timezone.now()
    progress.save(update_fields=["is_completed", "completed_at"])

    transaction.on_commit(lambda: dispatch_event(
        event_type=EventType.LESSON_COMPLETED,
        payload={
            "user_id": str(user.id),
            "lesson_id": str(lesson.id),
            "module_id": str(lesson.module_id),
        }
    ))

    return progress