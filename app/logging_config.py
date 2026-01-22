"""Comprehensive logging configuration for the application."""
import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path


def setup_logging(app):
    """
    Configure comprehensive application logging.
    
    Features:
    - Rotating file handlers for different log levels
    - Separate files for errors, warnings, and info
    - Console output in development
    - Structured logging with request context
    - Performance tracking
    """
    
    # Create logs directory if it doesn't exist
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    # Get log level from config or environment
    log_level = os.getenv('LOG_LEVEL', 'INFO' if app.debug else 'WARNING')
    log_level = getattr(logging, log_level.upper())
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s (%(funcName)s:%(lineno)d): %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    json_formatter = JsonFormatter()
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove any existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Console handler (only in debug mode)
    if app.debug:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(simple_formatter)
        root_logger.addHandler(console_handler)
        app.logger.info('Console logging enabled (debug mode)')
    
    # Error log file - rotating, 10MB max, keep 10 backups
    error_handler = logging.handlers.RotatingFileHandler(
        log_dir / 'error.log',
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=10
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)
    
    # Warning log file
    warning_handler = logging.handlers.RotatingFileHandler(
        log_dir / 'warning.log',
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
    warning_handler.setLevel(logging.WARNING)
    warning_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(warning_handler)
    
    # Info log file (general application log)
    info_handler = logging.handlers.RotatingFileHandler(
        log_dir / 'app.log',
        maxBytes=20 * 1024 * 1024,  # 20MB
        backupCount=10
    )
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(info_handler)
    
    # JSON log file for structured logging (useful for log aggregation tools)
    json_handler = logging.handlers.RotatingFileHandler(
        log_dir / 'app.json.log',
        maxBytes=20 * 1024 * 1024,
        backupCount=5
    )
    json_handler.setLevel(logging.INFO)
    json_handler.setFormatter(json_formatter)
    root_logger.addHandler(json_handler)
    
    # Access log (HTTP requests)
    access_handler = logging.handlers.RotatingFileHandler(
        log_dir / 'access.log',
        maxBytes=20 * 1024 * 1024,
        backupCount=10
    )
    access_handler.setLevel(logging.INFO)
    access_handler.setFormatter(simple_formatter)
    
    # Create separate logger for access logs
    access_logger = logging.getLogger('access')
    access_logger.setLevel(logging.INFO)
    access_logger.addHandler(access_handler)
    access_logger.propagate = False  # Don't propagate to root logger
    
    # Security log (authentication, authorization events)
    security_handler = logging.handlers.RotatingFileHandler(
        log_dir / 'security.log',
        maxBytes=10 * 1024 * 1024,
        backupCount=10
    )
    security_handler.setLevel(logging.INFO)
    security_handler.setFormatter(detailed_formatter)
    
    security_logger = logging.getLogger('security')
    security_logger.setLevel(logging.INFO)
    security_logger.addHandler(security_handler)
    security_logger.propagate = False
    
    # Performance log (slow queries, long requests)
    performance_handler = logging.handlers.RotatingFileHandler(
        log_dir / 'performance.log',
        maxBytes=10 * 1024 * 1024,
        backupCount=5
    )
    performance_handler.setLevel(logging.WARNING)
    performance_handler.setFormatter(detailed_formatter)
    
    performance_logger = logging.getLogger('performance')
    performance_logger.setLevel(logging.WARNING)
    performance_logger.addHandler(performance_handler)
    performance_logger.propagate = False
    
    # Configure SQLAlchemy logging
    if app.config.get('SQLALCHEMY_ECHO'):
        logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    else:
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
    
    # Log startup message
    app.logger.info('=' * 80)
    app.logger.info(f'Application started - Environment: {app.config.get("ENV", "unknown")}')
    app.logger.info(f'Log level: {logging.getLevelName(log_level)}')
    app.logger.info(f'Debug mode: {app.debug}')
    app.logger.info('=' * 80)


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record):
        """Format log record as JSON."""
        import json
        
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'ip_address'):
            log_data['ip_address'] = record.ip_address
        
        return json.dumps(log_data)


class RequestContextFilter(logging.Filter):
    """Add request context to log records."""
    
    def filter(self, record):
        """Add request-specific information to log record."""
        from flask import has_request_context, request, g
        
        if has_request_context():
            record.url = request.url
            record.method = request.method
            record.ip_address = request.remote_addr
            
            # Add user info if authenticated
            if hasattr(g, 'current_user') and g.current_user:
                record.user_id = g.current_user.id
            
            # Add request ID if present
            if hasattr(g, 'request_id'):
                record.request_id = g.request_id
        
        return True


def log_slow_query(duration_ms, query_str):
    """Log slow database queries."""
    logger = logging.getLogger('performance')
    logger.warning(
        f'Slow query detected: {duration_ms}ms - {query_str[:200]}'
        + ('...' if len(query_str) > 200 else '')
    )


def log_security_event(event_type, user_id=None, details=None):
    """
    Log security-related events.
    
    Args:
        event_type: Type of security event (login, logout, failed_auth, etc.)
        user_id: User ID if applicable
        details: Additional details about the event
    """
    logger = logging.getLogger('security')
    
    message = f'Security Event: {event_type}'
    if user_id:
        message += f' - User: {user_id}'
    if details:
        message += f' - Details: {details}'
    
    logger.info(message)


def log_api_call(endpoint, method, status_code, duration_ms, user_id=None):
    """Log API call with performance metrics."""
    logger = logging.getLogger('access')
    
    message = f'{method} {endpoint} - Status: {status_code} - Duration: {duration_ms}ms'
    if user_id:
        message += f' - User: {user_id}'
    
    logger.info(message)
    
    # Log slow requests
    if duration_ms > 1000:  # More than 1 second
        perf_logger = logging.getLogger('performance')
        perf_logger.warning(f'Slow request: {message}')


# Example usage decorators
def log_function_call(func):
    """Decorator to log function calls with arguments."""
    import functools
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.debug(f'Calling {func.__name__} with args={args}, kwargs={kwargs}')
        
        try:
            result = func(*args, **kwargs)
            logger.debug(f'{func.__name__} completed successfully')
            return result
        except Exception as e:
            logger.error(f'{func.__name__} raised {type(e).__name__}: {e}')
            raise
    
    return wrapper


def log_performance(threshold_ms=100):
    """
    Decorator to log function performance.
    
    Args:
        threshold_ms: Log warning if execution exceeds this threshold
    """
    import functools
    import time
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration_ms = (time.time() - start_time) * 1000
                
                logger = logging.getLogger('performance')
                if duration_ms > threshold_ms:
                    logger.warning(
                        f'{func.__module__}.{func.__name__} took {duration_ms:.2f}ms '
                        f'(threshold: {threshold_ms}ms)'
                    )
        
        return wrapper
    return decorator