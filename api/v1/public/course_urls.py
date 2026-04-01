# qubitgyanpro\api\v1\public\course_urls.py

from django.urls import path

from api.v1.public.course_views import (
    CourseListView,
    CourseDetailView,
)

urlpatterns = [
    path("courses/", CourseListView.as_view()),
    path("courses/<slug:slug>/", CourseDetailView.as_view()),
]