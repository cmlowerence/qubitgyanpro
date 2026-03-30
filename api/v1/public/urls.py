# qubitgyanpro\api\v1\public\urls.py
from django.urls import path, include
from .health_views import health_view
from api.v1.public.auth_views import (
    LoginView,
    RequestPasswordResetView,
    VerifyOtpAndResetPasswordView
)

urlpatterns = [
    path('health/', health_view),
    path('auth/login/', LoginView.as_view(), name='auth-login'),
    path('auth/request-reset/', RequestPasswordResetView.as_view(), name='auth-request-reset'),
    path('auth/verify-reset/', VerifyOtpAndResetPasswordView.as_view(), name='auth-verigy-request')
]