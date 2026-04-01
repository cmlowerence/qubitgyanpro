# qubitgyanpro\api\v1\admin\course_views.py

from uuid import UUID
import logging

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ValidationError

from apps.core.permissions import IsAuthenticatedUser, IsAdmin
from utils.response import SuccessResponse, ErrorResponse

from services.course_service import (
    create_course,
    publish_course,
    create_module,
    create_lesson,
    update_lesson,
)

logger = logging.getLogger(__name__)


def _parse_uuid(value):
    try:
        return UUID(value)
    except Exception:
        raise ValidationError("Invalid ID format.")


class CreateCourseView(APIView):
    permission_classes = [IsAuthenticatedUser & IsAdmin]

    def post(self, request):
        try:
            course = create_course(
                admin_user=request.user,
                title=request.data.get("title"),
                description=request.data.get("description"),
                thumbnail_url=request.data.get("thumbnail_url"),
            )

            return SuccessResponse(
                message="Course created",
                data={"id": str(course.id)},
                status_code=status.HTTP_201_CREATED
            )

        except ValidationError as e:
            return ErrorResponse(str(e), status.HTTP_400_BAD_REQUEST)

        except Exception:
            logger.exception("CreateCourse failed")
            return ErrorResponse("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


class PublishCourseView(APIView):
    permission_classes = [IsAuthenticatedUser & IsAdmin]

    def post(self, request, course_id):
        try:
            course = publish_course(
                admin_user=request.user,
                course_id=_parse_uuid(course_id)
            )

            return SuccessResponse(
                message="Course published",
                data={"id": str(course.id)}
            )

        except ValidationError as e:
            return ErrorResponse(str(e), status.HTTP_400_BAD_REQUEST)

        except Exception:
            logger.exception("PublishCourse failed")
            return ErrorResponse("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateModuleView(APIView):
    permission_classes = [IsAuthenticatedUser & IsAdmin]

    def post(self, request):
        try:
            module = create_module(
                admin_user=request.user,
                course_id=request.data.get("course_id"),
                title=request.data.get("title"),
                order=request.data.get("order"),
            )

            return SuccessResponse(
                message="Module created",
                data={"id": str(module.id)},
                status_code=status.HTTP_201_CREATED
            )

        except ValidationError as e:
            return ErrorResponse(str(e), status.HTTP_400_BAD_REQUEST)

        except Exception:
            logger.exception("CreateModule failed")
            return ErrorResponse("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateLessonView(APIView):
    permission_classes = [IsAuthenticatedUser & IsAdmin]

    def post(self, request):
        try:
            lesson = create_lesson(
                admin_user=request.user,
                module_id=request.data.get("module_id"),
                title=request.data.get("title"),
                content_type=request.data.get("content_type"),
                content_data=request.data.get("content_data"),
                order=request.data.get("order"),
                duration_seconds=request.data.get("duration_seconds"),
            )

            return SuccessResponse(
                message="Lesson created",
                data={"id": str(lesson.id)},
                status_code=status.HTTP_201_CREATED
            )

        except ValidationError as e:
            return ErrorResponse(str(e), status.HTTP_400_BAD_REQUEST)

        except Exception:
            logger.exception("CreateLesson failed")
            return ErrorResponse("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)


class UpdateLessonView(APIView):
    permission_classes = [IsAuthenticatedUser & IsAdmin]

    def patch(self, request, lesson_id):
        try:
            lesson = update_lesson(
                admin_user=request.user,
                lesson_id=_parse_uuid(lesson_id),
                title=request.data.get("title"),
                content_type=request.data.get("content_type"),
                content_data=request.data.get("content_data"),
                duration_seconds=request.data.get("duration_seconds"),
            )

            return SuccessResponse(
                message="Lesson updated",
                data={"id": str(lesson.id)}
            )

        except ValidationError as e:
            return ErrorResponse(str(e), status.HTTP_400_BAD_REQUEST)

        except Exception:
            logger.exception("UpdateLesson failed")
            return ErrorResponse("Internal server error", status.HTTP_500_INTERNAL_SERVER_ERROR)