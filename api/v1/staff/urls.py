from django.urls import path
from .admission_views import (
    ListAdmissionsView,
    ReviewAdmissionView
)

urlpatterns = [
    path('admissions/', ListAdmissionsView.as_view(), name='list-admissions'),
    path('admissions/<int:admission_id>/review/', ReviewAdmissionView.as_view(), name='review-admission'),
]