# qubitgyanpro\events\handlers\recommendation_handlers.py

from apps.core.models import User
from apps.courses.models import Lesson

from services.recommendation_engine import generate_advanced_recommendations


def handle_lesson_completed(payload):
    user = User.objects.filter(id=payload.get("user_id")).first()
    lesson = Lesson.objects.filter(id=payload.get("lesson_id")).first()

    if not user or not lesson:
        return

    generate_advanced_recommendations(
        user=user,
        lesson=lesson
    )