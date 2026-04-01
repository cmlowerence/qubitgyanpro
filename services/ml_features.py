# qubitgyanpro\services\ml_features.py

import numpy as np
from django.utils import timezone

from apps.progress.models import LessonProgress
from apps.analytics.models import UserLessonInteraction


def _safe_div(a, b):
    return a / b if b else 0


def build_features(user, lesson):
    progress = LessonProgress.objects.filter(user=user, lesson=lesson).first()
    interaction = UserLessonInteraction.objects.filter(user=user, lesson=lesson).first()

    time_spent = interaction.time_spent if interaction else 0
    completed = int(progress.is_completed) if progress else 0

    if progress and progress.completed_at:
        delta = (timezone.now() - progress.completed_at).total_seconds()
    else:
        delta = 999999

    recency = np.exp(-delta / 86400)

    lesson_order = lesson.order
    module_order = lesson.module.order

    total = LessonProgress.objects.filter(user=user).count()
    done = LessonProgress.objects.filter(user=user, is_completed=True).count()

    completion_rate = _safe_div(done, total)

    engagement = np.log1p(time_spent)

    recent = LessonProgress.objects.filter(
        user=user,
        is_completed=True,
        completed_at__gte=timezone.now() - timezone.timedelta(days=2)
    ).count()

    velocity = recent / 2.0
    fatigue = min(1.0, total / 100)

    return np.array([
        time_spent,
        engagement,
        completed,
        recency,
        lesson_order,
        module_order,
        completion_rate,
        velocity,
        fatigue
    ])