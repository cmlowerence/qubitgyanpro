# qubitgyanpro\services\course_service.py

from django.db import transaction
from django.core.exceptions import ValidationError

from apps.courses.models import Course, Module, Lesson
from apps.core.constants import UserRole, UserStatus
from apps.security.models import AdminAuditLog

from events.dispatcher import dispatch_event
from events.event_types import EventType


def _validate_admin(user):
    if not user:
        raise ValidationError("Authentication required.")
    if user.role != UserRole.ADMIN:
        raise ValidationError("Admin privileges required.")
    if not user.is_active or user.is_deleted or user.status != UserStatus.ACTIVE:
        raise ValidationError("Invalid admin account.")


def _validate_content(content_type, content_data):
    if not isinstance(content_data, dict) or not content_data:
        raise ValidationError("content_data must be a non-empty dictionary.")

    if content_type not in {"VIDEO", "PDF", "TEXT"}:
        raise ValidationError("Invalid content_type.")

    if content_type in {"VIDEO", "PDF"}:
        url = content_data.get("url")
        if not url or not isinstance(url, str) or not url.strip():
            raise ValidationError(f"{content_type} requires a valid 'url'.")

    if content_type == "TEXT":
        text = content_data.get("text")
        if not text or not isinstance(text, str) or not text.strip():
            raise ValidationError("TEXT requires valid 'text' content.")


@transaction.atomic
def create_course(*, admin_user, title, description="", thumbnail_url=None):
    _validate_admin(admin_user)

    if not title or not isinstance(title, str):
        raise ValidationError("Invalid course title.")

    course = Course.objects.create(
        title=title.strip(),
        description=description or "",
        thumbnail_url=thumbnail_url,
    )

    transaction.on_commit(lambda: dispatch_event(
        event_type=EventType.COURSE_CREATED,
        payload={"course_id": str(course.id)}
    ))

    AdminAuditLog.objects.create(
        admin=admin_user,
        action=AdminAuditLog.Action.COURSE_CREATED,
        target_type=AdminAuditLog.TargetType.COURSE,
        target_id=course.id,    
        metadata={"type": "course_created"}
    )

    return course


@transaction.atomic
def publish_course(*, admin_user, course_id):
    _validate_admin(admin_user)

    course = Course.objects.select_for_update().filter(id=course_id).first()
    if not course:
        raise ValidationError("Course not found.")

    if not course.is_active:
        raise ValidationError("Cannot publish inactive course.")

    if course.is_published:
        return course

    course.is_published = True
    course.save(update_fields=["is_published"])

    transaction.on_commit(lambda: dispatch_event(
        event_type=EventType.COURSE_PUBLISHED,
        payload={"course_id": str(course.id)}
    ))

    AdminAuditLog.objects.create(
        admin=admin_user,
        action=AdminAuditLog.Action.COURSE_PUBLISHED,
        target_type=AdminAuditLog.TargetType.COURSE,
        target_id=course.id,
        metadata={"type": "course_published"}
    )

    return course


@transaction.atomic
def create_module(*, admin_user, course_id, title, order=None):
    _validate_admin(admin_user)

    course = Course.objects.select_for_update().filter(id=course_id, is_active=True).first()
    if not course:
        raise ValidationError("Course not found or inactive.")

    if not title or not isinstance(title, str):
        raise ValidationError("Invalid module title.")

    modules_qs = Module.objects.select_for_update().filter(course=course)

    if order is None:
        last = modules_qs.order_by("-order").first()
        order = (last.order + 1) if last else 0

    if modules_qs.filter(order=order).exists():
        raise ValidationError("Module order conflict.")

    module = Module.objects.create(
        course=course,
        title=title.strip(),
        order=order
    )

    transaction.on_commit(lambda: dispatch_event(
        event_type=EventType.MODULE_CREATED,
        payload={
            "module_id": str(module.id),
            "course_id": str(course.id),
        }
    ))

    AdminAuditLog.objects.create(
        admin=admin_user,
        action=AdminAuditLog.Action.MODULE_CREATED,
        target_type=AdminAuditLog.TargetType.MODULE,
        target_id=module.id,
        metadata={"type": "module_created"}
    )

    return module


@transaction.atomic
def create_lesson(
    *,
    admin_user,
    module_id,
    title,
    content_type,
    content_data,
    order=None,
    duration_seconds=0
):
    _validate_admin(admin_user)

    module = Module.objects.select_for_update().filter(id=module_id, is_active=True).first()
    if not module:
        raise ValidationError("Module not found or inactive.")

    if not title or not isinstance(title, str):
        raise ValidationError("Invalid lesson title.")

    _validate_content(content_type, content_data)

    lessons_qs = Lesson.objects.select_for_update().filter(module=module)

    if order is None:
        last = lessons_qs.order_by("-order").first()
        order = (last.order + 1) if last else 0

    if lessons_qs.filter(order=order).exists():
        raise ValidationError("Lesson order conflict.")

    lesson = Lesson.objects.create(
        module=module,
        title=title.strip(),
        content_type=content_type,
        content_data=content_data,
        order=order,
        duration_seconds=max(0, int(duration_seconds or 0)),
    )

    transaction.on_commit(lambda: dispatch_event(
        event_type=EventType.LESSON_CREATED,
        payload={
            "lesson_id": str(lesson.id),
            "module_id": str(module.id),
        }
    ))

    AdminAuditLog.objects.create(
        admin=admin_user,
        action=AdminAuditLog.Action.MODULE_CREATED,
        target_type=AdminAuditLog.TargetType.MODULE,
        target_id=module.id,
        metadata={"type": "lesson_created"}
    )

    return lesson


@transaction.atomic
def update_lesson(
    *,
    admin_user,
    lesson_id,
    title=None,
    content_type=None,
    content_data=None,
    duration_seconds=None
):
    _validate_admin(admin_user)

    lesson = Lesson.objects.select_for_update().filter(id=lesson_id).first()
    if not lesson:
        raise ValidationError("Lesson not found.")

    if content_type is not None:
        if content_type not in {"VIDEO", "PDF", "TEXT"}:
            raise ValidationError("Invalid content_type.")
        lesson.content_type = content_type

    if content_data is not None:
        _validate_content(lesson.content_type, content_data)
        lesson.content_data = content_data

    if title is not None:
        if not isinstance(title, str) or not title.strip():
            raise ValidationError("Invalid lesson title.")
        lesson.title = title.strip()

    if duration_seconds is not None:
        lesson.duration_seconds = max(0, int(duration_seconds))

    lesson.save()

    transaction.on_commit(lambda: dispatch_event(
        event_type=EventType.LESSON_UPDATED,
        payload={
            "lesson_id": str(lesson.id),
        }
    ))

    AdminAuditLog.objects.create(
        admin=admin_user,
        action=AdminAuditLog.Action.LESSON_UPDATED,
        target_type=AdminAuditLog.TargetType.LESSON,
        target_id=lesson.id,
        metadata={"type": "lesson_updated"}
    )

    return lesson