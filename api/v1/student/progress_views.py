# qubitgyanpro\api\v1\student\progress_views.py

import logging
from uuid import UUID

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ValidationError

from utils.response import SuccessResponse, ErrorResponse
from apps.core.permissions import IsAuthenticatedUser

from services.progress_service import mark_lesson_complete

logger = logging.getLogger(__name__)


def _parse_uuid(value):
    try:
        return UUID(value)
    except Exception:
        raise ValidationError("Invalid lesson ID.")


class CompleteLessonView(APIView):
    permission_classes = [IsAuthenticatedUser]

    def post(self, request, lesson_id):
        try:
            progress = mark_lesson_complete(
                user=request.user,
                lesson_id=_parse_uuid(lesson_id)
            )

            return SuccessResponse(
                message="Lesson marked complete",
                data={"lesson_id": str(progress.lesson_id)}
            )

        except ValidationError as e:
            return ErrorResponse(str(e), status.HTTP_400_BAD_REQUEST)

        except Exception:
            logger.exception("CompleteLesson failed")
            return ErrorResponse(
                "Failed to update progress",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )