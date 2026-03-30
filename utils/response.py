# qubitgyanpro/utils/response.py

from rest_framework.response import Response
from rest_framework import status

class SuccessResponse(Response):
    """
    Standardized DRF Response for successful operations.
    Format:
    {
        "success": true,
        "message": "...",
        "data": { ... }
    }
    """
    def __init__(self, message="Operation successful.", data=None, status_code=status.HTTP_200_OK, **kwargs):
        payload = {
            "success": True,
            "message": message,
        }
        if data is not None:
            payload["data"] = data
            
        super().__init__(data=payload, status=status_code, **kwargs)


class ErrorResponse(Response):
    """
    Standardized DRF Response for failed operations.
    Format:
    {
        "success": false,
        "message": "...",
        "errors": { ... }
    }
    """
    def __init__(self, message="An error occurred.", errors=None, status_code=status.HTTP_400_BAD_REQUEST, **kwargs):
        payload = {
            "success": False,
            "message": message,
        }
        if errors is not None:
            payload["errors"] = errors
            
        super().__init__(data=payload, status=status_code, **kwargs)