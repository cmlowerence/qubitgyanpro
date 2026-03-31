# qubitgyanpro/api\v1\staff\admission_views.py

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.exceptions import ValidationError

from apps.admission.serializers import AdmissionSerializer, ReviewAdmissionSerializer
from apps.core.permissions import IsStaff, IsAdmin, IsAuthenticatedUser
from apps.admission.models import AdmissionStatus
from services import admission_service
from utils.response import SuccessResponse, ErrorResponse


class ListAdmissionsView(APIView):
    permission_classes = [IsAuthenticatedUser & (IsStaff | IsAdmin)]

    def get(self, request):
        status_filter = request.query_params.get("status")

        if status_filter and status_filter not in AdmissionStatus.values:
            return ErrorResponse(
                message="Invalid status filter.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            admissions = admission_service.list_admissions(status_filter)

            return SuccessResponse(
                message="Admissions fetched successfully.",
                data=AdmissionSerializer(admissions, many=True).data,
                status_code=status.HTTP_200_OK
            )

        except Exception:
            return ErrorResponse(
                message="Failed to fetch admissions.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ReviewAdmissionView(APIView):
    permission_classes = [IsAuthenticatedUser & (IsStaff | IsAdmin)]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'admissions_review'

    def post(self, request, admission_id):
        serializer = ReviewAdmissionSerializer(data=request.data)

        if not serializer.is_valid():
            return ErrorResponse(
                message="Invalid request.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )

        action = serializer.validated_data['action']
        reason = serializer.validated_data.get('rejection_reason')

        admission = admission_service.get_admission_by_id(admission_id)

        if not admission:
            return ErrorResponse(
                message="Admission not found.",
                status_code=status.HTTP_404_NOT_FOUND
            )

        try:
            if action == "approve":
                user = admission_service.approve_admission(admission, request.user)

                return SuccessResponse(
                    message="Admission approved.",
                    data={"user_id": str(user.id)},
                    status_code=status.HTTP_200_OK
                )

            if action == "reject":
                admission_service.reject_admission(admission, request.user, reason)

                return SuccessResponse(
                    message="Admission rejected.",
                    status_code=status.HTTP_200_OK
                )

            if action == "under_review":
                admission_service.mark_under_review(admission, request.user)

                return SuccessResponse(
                    message="Admission moved to review.",
                    status_code=status.HTTP_200_OK
                )

            return ErrorResponse(
                message="Invalid action.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        except ValidationError as e:
            return ErrorResponse(
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )

        except Exception:
            return ErrorResponse(
                message="Action failed. Please try again.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )