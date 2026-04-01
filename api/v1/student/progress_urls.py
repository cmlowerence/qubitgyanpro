

from django.urls import path
from api.v1.student.progress_views import CompleteLessonView

urlpatterns = [
    path("lessons/<uuid:lesson_id>/complete/", CompleteLessonView.as_view()),
]
