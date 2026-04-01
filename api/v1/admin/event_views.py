from uuid import UUID
import logging

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.throttling import ScopedRateThrottle

from apps.core.permissions import IsAuthenticatedUser, IsAdmin
from utils.response import SuccessResponse, ErrorResponse

from events.selectors import (
    get_events,
    get_event_by_id,
    get_event_metrics,
)
from events.services import (
    retry_event,
    retry_failed_events_service,
)

logger = logging.getLogger(__name__)


def _parse_uuid(value):
    try:
        return UUID(value)
    except Exception:
        raise ValidationError("Invalid event ID.")



class EventListView(APIView):
    permission_classes = [IsAuthenticatedUser & IsAdmin]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "admin_events_list"

    def get(self, request):
        status_filter = request.query_params.get("status")
        event_type = request.query_params.get("event_type")

        try:
            events = get_events(
                status=status_filter,
                event_type=event_type,
            )[:100] 

            data = [
                {
                    "id": str(e.id),
                    "event_type": e.event_type,
                    "status": e.status,
                    "attempts": e.attempts,
                    "created_at": e.created_at.isoformat(),
                    "processed_at": e.processed_at.isoformat() if e.processed_at else None,
                }
                for e in events
            ]

            return SuccessResponse(
                message="Events fetched successfully.",
                data=data,
                status_code=status.HTTP_200_OK
            )

        except Exception:
            logger.exception("Event list fetch failed")
            return ErrorResponse(
                message="Failed to fetch events.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class EventDetailView(APIView):
    permission_classes = [IsAuthenticatedUser & IsAdmin]

    def get(self, request, event_id):
        try:
            event = get_event_by_id(_parse_uuid(event_id))

            if not event:
                return ErrorResponse(
                    message="Event not found.",
                    status_code=status.HTTP_404_NOT_FOUND
                )

            data = {
                "id": str(event.id),
                "event_type": event.event_type,
                "status": event.status,
                "attempts": event.attempts,
                "payload": event.payload,
                "last_error": event.last_error,
                "created_at": event.created_at.isoformat(),
                "processed_at": event.processed_at.isoformat() if event.processed_at else None,
            }

            return SuccessResponse(
                message="Event fetched successfully.",
                data=data,
                status_code=status.HTTP_200_OK
            )

        except ValidationError as e:
            return ErrorResponse(str(e), status_code=status.HTTP_400_BAD_REQUEST)

        except Exception:
            logger.exception("Event detail fetch failed")
            return ErrorResponse(
                message="Failed to fetch event.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class RetryEventView(APIView):
    permission_classes = [IsAuthenticatedUser & IsAdmin]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "admin_event_retry"

    def post(self, request, event_id):
        try:
            result = retry_event(_parse_uuid(event_id), request.user)

            return SuccessResponse(
                message="Event retry triggered.",
                data=result,
                status_code=status.HTTP_200_OK
            )

        except ValidationError as e:
            return ErrorResponse(str(e), status_code=status.HTTP_400_BAD_REQUEST)

        except Exception:
            logger.exception("Single event retry failed")
            return ErrorResponse(
                message="Retry failed.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RetryFailedEventsView(APIView):
    permission_classes = [IsAuthenticatedUser & IsAdmin]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "admin_event_bulk_retry"

    def post(self, request):
        try:
            result = retry_failed_events_service(request.user)

            return SuccessResponse(
                message="Bulk retry executed.",
                data=result,
                status_code=status.HTTP_200_OK
            )

        except ValidationError as e:
            return ErrorResponse(str(e), status_code=status.HTTP_400_BAD_REQUEST)

        except Exception:
            logger.exception("Bulk retry failed")
            return ErrorResponse(
                message="Bulk retry failed.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EventMetricsView(APIView):
    permission_classes = [IsAuthenticatedUser & IsAdmin]

    def get(self, request):
        try:
            metrics = get_event_metrics()

            return SuccessResponse(
                message="Metrics fetched successfully.",
                data=metrics,
                status_code=status.HTTP_200_OK
            )

        except Exception:
            logger.exception("Metrics fetch failed")
            return ErrorResponse(
                message="Failed to fetch metrics.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )