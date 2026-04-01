# qubitgyanpro\api\v1\admin\course_urls.py

from django.urls import path

from api.v1.admin.course_views import (
    CreateCourseView,
    PublishCourseView,
    CreateModuleView,
    CreateLessonView,
    UpdateLessonView,
)

urlpatterns = [
    path("courses/create/", CreateCourseView.as_view()),
    path("courses/<uuid:course_id>/publish/", PublishCourseView.as_view()),

    path("modules/create/", CreateModuleView.as_view()),

    path("lessons/create/", CreateLessonView.as_view()),
    path("lessons/<uuid:lesson_id>/update/", UpdateLessonView.as_view()),
]