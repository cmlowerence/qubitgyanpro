# qubitgyanpro\api\v1\public\course_views.py

import logging
from rest_framework.views import APIView
from rest_framework import status

from utils.response import SuccessResponse, ErrorResponse

from apps.courses.selectors import (
    get_published_courses,
    get_course_detail_by_slug,
)

logger = logging.getLogger(__name__)


class CourseListView(APIView):

    def get(self, request):
        try:
            courses = get_published_courses()

            data = [
                {
                    "id": str(c.id),
                    "title": c.title,
                    "slug": c.slug,
                    "thumbnail_url": c.thumbnail_url,
                }
                for c in courses
            ]

            return SuccessResponse(
                message="Courses fetched",
                data=data
            )

        except Exception:
            logger.exception("CourseList failed")
            return ErrorResponse("Failed to fetch courses", status.HTTP_500_INTERNAL_SERVER_ERROR)


class CourseDetailView(APIView):

    def get(self, request, slug):
        try:
            course = get_course_detail_by_slug(slug)

            if not course:
                return ErrorResponse("Course not found", status.HTTP_404_NOT_FOUND)

            data = {
                "id": str(course.id),
                "title": course.title,
                "modules": [
                    {
                        "id": str(m.id),
                        "title": m.title,
                        "lessons": [
                            {
                                "id": str(l.id),
                                "title": l.title,
                                "content_type": l.content_type,
                                "content_data": l.content_data,
                                "duration": l.duration_seconds,
                            }
                            for l in m.lessons.all()
                        ]
                    }
                    for m in course.modules.all()
                ]
            }

            return SuccessResponse(
                message="Course detail fetched",
                data=data
            )

        except Exception:
            logger.exception("CourseDetail failed")
            return ErrorResponse("Failed to fetch course", status.HTTP_500_INTERNAL_SERVER_ERROR)