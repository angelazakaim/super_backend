from flask import request
import time

def setup_middleware(app):
    """Configure application middleware."""
    
    @app.before_request
    def log_request_info():
        """Log request information."""
        app.logger.info(f'Request: {request.method} {request.url}')
        request.start_time = time.time()
    
    @app.after_request
    def log_response_info(response):
        """Log response information."""
        if hasattr(request, 'start_time'):
            elapsed = time.time() - request.start_time
            app.logger.info(f'Response: {response.status_code} - {elapsed:.3f}s')
        return response
    
    @app.after_request
    def add_security_headers(response):
        """Add security headers to response."""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response