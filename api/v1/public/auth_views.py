# qubitgyanpro/api/v1/public/auth_views.py

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.exceptions import AuthenticationFailed, ValidationError

from apps.core.serializers import (
    LoginInputSerializer,
    RequestResetSerializer,
    VerifyResetSerializer
)
from services import auth_service
from utils.response import SuccessResponse, ErrorResponse

import logging

logger = logging.getLogger(__name__)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR') or ''


class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'login'

    def post(self, request):
        serializer = LoginInputSerializer(data=request.data)

        if not serializer.is_valid():
            return ErrorResponse(
                message="Invalid credentials.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        user = serializer.validated_data['user']
        password = serializer.validated_data['password']
        ip_address = get_client_ip(request)
        device = str(request.META.get('HTTP_USER_AGENT', ''))[:255]

        try:
            auth_data = auth_service.login_user(user, password, ip_address, device)

            return SuccessResponse(
                message="Login successful",
                data=auth_data,
                status_code=status.HTTP_200_OK
            )

        except AuthenticationFailed:
            return ErrorResponse(
                message="Invalid credentials.",
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        except Exception as e:
            logger.exception("Login error")
            return ErrorResponse(
                message="Something went wrong. Please try again.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RequestPasswordResetView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'password_reset'

    def post(self, request):
        serializer = RequestResetSerializer(data=request.data)

        if not serializer.is_valid():
            return ErrorResponse(
                message="Invalid request.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data['email']

        try:
            auth_service.request_password_reset_telegram(email)

            return SuccessResponse(
                message="If the email exists, an OTP has been sent.",
                status_code=status.HTTP_200_OK
            )

        except ValidationError:
            return ErrorResponse(
                message="Unable to process request.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        except Exception:
            logger.exception("Password reset request error")
            return ErrorResponse(
                message="Something went wrong. Please try again.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VerifyOtpAndResetPasswordView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'otp_verify'

    def post(self, request):
        serializer = VerifyResetSerializer(data=request.data)

        if not serializer.is_valid():
            return ErrorResponse(
                message="Invalid request.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        email = serializer.validated_data['email']
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']

        try:
            user = auth_service.verify_telegram_otp(email, otp)
            auth_service.reset_password(user, new_password)

            return SuccessResponse(
                message="Password reset successful.",
                status_code=status.HTTP_200_OK
            )

        except ValidationError:
            return ErrorResponse(
                message="Invalid or expired OTP.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        except Exception:
            logger.exception("OTP verification error")
            return ErrorResponse(
                message="Something went wrong. Please try again.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )