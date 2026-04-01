# qubitgyanpro/api/v1/admin/event_urls.py

from django.urls import path

from api.v1.admin.event_views import (
    EventListView,
    EventDetailView,
    RetryEventView,
    RetryFailedEventsView,
    EventMetricsView,
)

urlpatterns = [
    path("events/", EventListView.as_view()),
    path("events/metrics/", EventMetricsView.as_view()),
    path("events/retry-failed/", RetryFailedEventsView.as_view()),
    path("events/<uuid:event_id>/", EventDetailView.as_view()),
    path("events/<uuid:event_id>/retry/", RetryEventView.as_view()),
]