# qubitgyanpro\apps\courses\selectors.py

from typing import Optional
from django.db.models import QuerySet, Prefetch

from apps.courses.models import Course, Module, Lesson


def _course_base_queryset(include_inactive=False):
    """
    Optimized queryset for nested course structure.
    Avoids N+1 and reduces payload size.
    """

    module_qs = Module.objects.order_by("order")

    lesson_qs = Lesson.objects.order_by("order")

    if not include_inactive:
        module_qs = module_qs.filter(is_active=True)
        lesson_qs = lesson_qs.filter(is_active=True)

    lesson_qs = lesson_qs.only(
        "id", "title", "content_type",
        "content_data", "order", "duration_seconds"
    )

    module_qs = module_qs.only(
        "id", "title", "course_id", "order"
    ).prefetch_related(
        Prefetch("lessons", queryset=lesson_qs)
    )

    return Course.objects.only(
        "id", "title", "slug",
        "is_published", "is_active", "created_at"
    ).prefetch_related(
        Prefetch("modules", queryset=module_qs)
    )



def get_published_courses() -> QuerySet[Course]:
    """
    Fetch all published and active courses (lightweight).
    """
    return Course.objects.filter(
        is_active=True,
        is_published=True
    ).only(
        "id", "title", "slug", "thumbnail_url"
    ).order_by("-created_at")


def get_course_detail_by_slug(slug: str) -> Optional[Course]:
    """
    Fetch full course structure (modules + lessons).
    """

    if not slug or not isinstance(slug, str):
        return None

    return _course_base_queryset().filter(
        is_active=True,
        is_published=True,
        slug=slug
    ).first()


def get_all_courses() -> QuerySet[Course]:
    """
    Admin access to all courses.
    Lightweight list.
    """
    return Course.objects.only(
        "id", "title", "slug",
        "is_published", "is_active", "created_at"
    ).order_by("-created_at")


def get_course_by_id(course_id: int) -> Optional[Course]:
    """
    Admin fetch single course with full structure.
    Includes inactive content.
    """

    if not isinstance(course_id, int):
        return None

    return _course_base_queryset(include_inactive=True).filter(
        id=course_id
    ).first()

