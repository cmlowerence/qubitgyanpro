# qubitgyanpro\services\recommendation_service.py

from django.db import transaction

from apps.courses.models import Lesson
from apps.recommendations.models import UserRecommendation


def _get_next_lesson_in_module(user, lesson):
    return Lesson.objects.filter(
        module=lesson.module,
        order__gt=lesson.order,
        is_active=True
    ).exclude(
        progress_records__user=user,
        progress_records__is_completed=True
    ).order_by("order").first()


def _get_first_lesson_next_module(user, lesson):
    next_module = lesson.module.course.modules.filter(
        order__gt=lesson.module.order,
        is_active=True
    ).order_by("order").first()

    if not next_module:
        return None

    return next_module.lessons.filter(
        is_active=True
    ).exclude(
        progress_records__user=user,
        progress_records__is_completed=True
    ).order_by("order").first()


def _get_revision_lesson(user):
    return Lesson.objects.filter(
        progress_records__user=user,
        progress_records__is_completed=True
    ).order_by("-updated_at").first()


@transaction.atomic
def generate_recommendations(*, user, lesson):
    recommendations = []

    next_lesson = _get_next_lesson_in_module(user, lesson)
    if next_lesson:
        recommendations.append((next_lesson, UserRecommendation.Type.CONTINUE, 1.0))

    next_module_lesson = _get_first_lesson_next_module(user, lesson)
    if next_module_lesson:
        recommendations.append((next_module_lesson, UserRecommendation.Type.NEXT_MODULE, 0.9))

    revision = _get_revision_lesson(user)
    if revision:
        recommendations.append((revision, UserRecommendation.Type.REVISION, 0.5))

    unique = {}
    for lesson_obj, rec_type, score in recommendations:
        if lesson_obj.id not in unique:
            unique[lesson_obj.id] = (lesson_obj, rec_type, score)

    UserRecommendation.objects.select_for_update().filter(user=user).delete()

    objs = [
        UserRecommendation(
            user=user,
            lesson=lesson_obj,
            recommendation_type=rec_type,
            score=score
        )
        for lesson_obj, rec_type, score in unique.values()
    ]

    UserRecommendation.objects.bulk_create(objs)

    return objs