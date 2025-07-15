import logging
import time
import traceback
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class RequestResponseLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log HTTP requests, responses, and exceptions.
    """
    
    def process_request(self, request):
        """Log incoming HTTP requests."""
        request._start_time = time.time()
        
        # Log request details
        logger.info(
            f"HTTP Request: {request.method} {request.get_full_path()} "
            f"from {self.get_client_ip(request)} "
            f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'Unknown')}"
        )
        
        # Log request headers (optional, be careful with sensitive data)
        if logger.isEnabledFor(logging.DEBUG):
            headers = {k: v for k, v in request.META.items() if k.startswith('HTTP_')}
            logger.debug(f"Request Headers: {headers}")
        
        return None
    
    def process_response(self, request, response):
        """Log HTTP responses."""
        # Calculate response time
        response_time = None
        if hasattr(request, '_start_time'):
            response_time = time.time() - request._start_time
        
        # Log response details
        logger.info(
            f"HTTP Response: {request.method} {request.get_full_path()} "
            f"Status: {response.status_code} "
            f"Response Time: {response_time:.3f}s" if response_time else ""
        )
        
        # Log response headers for debugging
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Response Headers: {dict(response.items())}")
        
        return response
    
    def process_exception(self, request, exception):
        """Log exceptions that occur during request processing."""
        response_time = None
        if hasattr(request, '_start_time'):
            response_time = time.time() - request._start_time
        
        logger.error(
            f"HTTP Exception: {request.method} {request.get_full_path()} "
            f"from {self.get_client_ip(request)} "
            f"Exception: {type(exception).__name__}: {str(exception)} "
            f"Response Time: {response_time:.3f}s" if response_time else ""
        )
        
        # Log full traceback for debugging
        logger.error(f"Full Traceback:\n{traceback.format_exc()}")
        
        return None  # Let Django handle the exception normally
    
    def get_client_ip(self, request):
        """Get the client's IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip