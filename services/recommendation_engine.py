# qubitgyanpro\services\recommendation_engine.py

from django.db import transaction

from apps.courses.models import Lesson
from apps.progress.models import LessonProgress
from apps.recommendations.models import UserRecommendation

from services.recommendation_features import compute_recency_score
from services.ml_inference import score_lessons


def _candidate_pool(user, lesson):
    return list(
        Lesson.objects.filter(
            module__course=lesson.module.course,
            is_active=True
        )
        .exclude(
            progress_records__user=user,
            progress_records__is_completed=True
        )[:20]
    )


def _rule_type(user, lesson):
    progress = LessonProgress.objects.filter(user=user, lesson=lesson).first()

    if not progress:
        return UserRecommendation.Type.CONTINUE

    if not progress.is_completed:
        return UserRecommendation.Type.WEAK_AREA

    return UserRecommendation.Type.REVISION


def _rule_score(user, lesson):
    progress = LessonProgress.objects.filter(user=user, lesson=lesson).first()
    if not progress:
        return 0.5
    return compute_recency_score(progress)


@transaction.atomic
def generate_advanced_recommendations(*, user, lesson):
    candidates = _candidate_pool(user, lesson)

    ml_ranked = score_lessons(user, candidates)

    final = []

    for lesson_obj, ml_score in ml_ranked:
        rule_score = _rule_score(user, lesson_obj)
        rec_type = _rule_type(user, lesson_obj)

        hybrid = (0.7 * ml_score) + (0.3 * rule_score)

        final.append((lesson_obj, hybrid, rec_type))

    final = sorted(final, key=lambda x: x[1], reverse=True)[:10]

    UserRecommendation.objects.select_for_update().filter(user=user).delete()

    objs = [
        UserRecommendation(
            user=user,
            lesson=l,
            recommendation_type=typ,
            score=score,
            reason="ML + hybrid logic"
        )
        for l, score, typ in final
    ]

    UserRecommendation.objects.bulk_create(objs)

    return objs

