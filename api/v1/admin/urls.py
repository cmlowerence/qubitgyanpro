from django.urls import path, include

urlpatterns = [
    path("events/", include("api.v1.admin.event_urls")),
]