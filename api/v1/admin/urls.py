from django.urls import path, include

urlpatterns = [
    path("events/", include("api.v1.admin.event_urls")),
    path("courses/", include("api.v1.admin.course_urls")),
]