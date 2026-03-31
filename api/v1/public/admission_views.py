# qubitgyanpro/api\v1\public\admission_views.py

from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.exceptions import ValidationError

from apps.admission.serializers import CreateAdmissionSerializer, AdmissionSerializer
from services import admission_service
from utils.response import SuccessResponse, ErrorResponse


class CreateAdmissionView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'admissions_create'

    def post(self, request):
        serializer = CreateAdmissionSerializer(data=request.data)

        if not serializer.is_valid():
            return ErrorResponse(
                message="Invalid request.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            admission = admission_service.create_admission(
                data=serializer.validated_data,
                source="WEB"
            )

            return SuccessResponse(
                message="Admission submitted successfully.",
                data=AdmissionSerializer(admission).data,
                status_code=status.HTTP_201_CREATED
            )

        except ValidationError as e:
            return ErrorResponse(
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )

        except Exception:
            return ErrorResponse(
                message="Something went wrong. Please try again later.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )