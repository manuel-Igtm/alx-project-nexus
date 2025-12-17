"""
Custom exception handlers for the API.
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Customize the response data
        custom_response_data = {
            'success': False,
            'error': {
                'code': response.status_code,
                'message': get_error_message(response),
                'details': response.data if isinstance(response.data, dict) else {'detail': response.data}
            }
        }
        
        # Log errors for monitoring
        if response.status_code >= 500:
            logger.error(f"Server Error: {exc}", exc_info=True)
        elif response.status_code >= 400:
            logger.warning(f"Client Error: {exc}")
        
        response.data = custom_response_data
        return response
    
    # Handle unhandled exceptions
    logger.error(f"Unhandled Exception: {exc}", exc_info=True)
    
    return Response({
        'success': False,
        'error': {
            'code': 500,
            'message': 'An unexpected error occurred',
            'details': {'detail': str(exc) if logger.level <= logging.DEBUG else 'Internal server error'}
        }
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_error_message(response):
    """Extract a human-readable error message from the response."""
    status_messages = {
        400: 'Bad Request',
        401: 'Authentication Required',
        403: 'Permission Denied',
        404: 'Not Found',
        405: 'Method Not Allowed',
        429: 'Too Many Requests',
        500: 'Internal Server Error',
    }
    return status_messages.get(response.status_code, 'Error')
