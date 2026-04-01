# qubitgyanpro\api\v1\student\recommendation_views.py

import logging

from rest_framework.views import APIView
from rest_framework import status

from utils.response import SuccessResponse, ErrorResponse
from apps.core.permissions import IsAuthenticatedUser

from apps.recommendations.selectors import get_user_recommendations

logger = logging.getLogger(__name__)


class RecommendationView(APIView):
    permission_classes = [IsAuthenticatedUser]

    def get(self, request):
        try:
            recs = get_user_recommendations(request.user)

            data = [
                {
                    "lesson_id": str(r.lesson_id),
                    "title": r.lesson.title,
                    "type": r.recommendation_type,
                    "score": r.score,
                    "reason": r.reason
                }
                for r in recs
            ]

            return SuccessResponse(
                message="Recommendations fetched",
                data=data
            )

        except Exception:
            logger.exception("Recommendation fetch failed")
            return ErrorResponse(
                "Failed to fetch recommendations",
                status.HTTP_500_INTERNAL_SERVER_ERROR
            )