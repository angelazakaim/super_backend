"""Custom decorators for route protection and authorization."""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt
import logging

logger = logging.getLogger(__name__)


def admin_required(fn):
    """
    Decorator to require admin role.
    Must be used AFTER @jwt_required()
    
    Usage:
        @jwt_required()
        @admin_required
        def my_route():
            ...
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            # Don't call verify_jwt_in_request() - it's already done by @jwt_required()
            claims = get_jwt()
            
            role = claims.get('role')
            logger.info(f"Admin check - User role: {role}")
            
            if role != 'admin':
                logger.warning(f"Access denied - User has role '{role}', requires 'admin'")
                return jsonify({'error': 'Admin access required'}), 403
            
            logger.info("Admin access granted")
            return fn(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Admin decorator error: {e}", exc_info=True)
            return jsonify({'error': 'Authorization failed'}), 401
    
    return wrapper


def role_required(*roles):
    """
    Decorator to require specific roles.
    Must be used AFTER @jwt_required()
    
    Usage:
        @jwt_required()
        @role_required('admin', 'manager')
        def my_route():
            ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                # Don't call verify_jwt_in_request() - it's already done by @jwt_required()
                claims = get_jwt()
                
                user_role = claims.get('role')
                logger.info(f"Role check - User role: {user_role}, Required: {roles}")
                
                if user_role not in roles:
                    logger.warning(
                        f"Access denied - User has role '{user_role}', "
                        f"requires one of: {', '.join(roles)}"
                    )
                    return jsonify({
                        'error': f'Access denied. Required roles: {", ".join(roles)}'
                    }), 403
                
                return fn(*args, **kwargs)
                
            except Exception as e:
                logger.error(f"Role decorator error: {e}", exc_info=True)
                return jsonify({'error': 'Authorization failed'}), 401
        
        return wrapper
    return decorator


def manager_or_admin_required(fn):
    """
    Decorator to require manager or admin role.
    Convenience decorator for common use case.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            # Don't call verify_jwt_in_request() - it's already done by @jwt_required()
            claims = get_jwt()
            
            user_role = claims.get('role')
            
            if user_role not in ['admin', 'manager']:
                logger.warning(
                    f"Access denied - User has role '{user_role}', "
                    f"requires admin or manager"
                )
                return jsonify({
                    'error': 'Manager or Admin access required'
                }), 403
            
            return fn(*args, **kwargs)
            
        except Exception as e:
            logger.error(f"Manager/Admin decorator error: {e}", exc_info=True)
            return jsonify({'error': 'Authorization failed'}), 401
    
    return wrapper