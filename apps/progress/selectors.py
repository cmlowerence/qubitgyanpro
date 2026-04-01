# qubitgyanpro\apps\progress\selectors.py

from apps.progress.models import LessonProgress
from apps.courses.models import Lesson


def get_course_progress(user, course):
    total = Lesson.objects.filter(
        module__course=course,
        is_active=True
    ).count()

    completed = LessonProgress.objects.filter(
        user=user,
        lesson__module__course=course,
        is_completed=True
    ).count()

    percentage = (completed / total * 100) if total else 0

    return {
        "total": total,
        "completed": completed,
        "percentage": percentage
    }


def get_module_progress(user, module):
    total = module.lessons.filter(is_active=True).count()

    completed = LessonProgress.objects.filter(
        user=user,
        lesson__module=module,
        is_completed=True
    ).count()

    percentage = (completed / total * 100) if total else 0

    return {
        "total": total,
        "completed": completed,
        "percentage": percentage
    }