# qubitgyanpro\services\recommendation_features.py

from django.utils import timezone
from datetime import timedelta

from apps.progress.models import LessonProgress


def compute_recency_score(progress):
    if not progress.completed_at:
        return 0.0

    delta = timezone.now() - progress.completed_at

    if delta < timedelta(hours=6):
        return 0.2
    if delta < timedelta(days=1):
        return 0.5
    if delta < timedelta(days=3):
        return 0.8

    return 1.0


def compute_completion_score(progress):
    return 1.0 if progress.is_completed else 0.0