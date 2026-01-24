"""Authorization decorators for role-based access control."""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt


def admin_required(fn):
    """
    Require admin role.
    Use for: System settings, user management, financial reports, permanent deletions.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        role = claims.get('role')
        
        if role != 'admin':
            return jsonify({
                'error': 'Admin access required',
                'your_role': role,
                'required_role': 'admin'
            }), 403
        
        return fn(*args, **kwargs)
    return wrapper


def manager_required(fn):
    """
    Require manager or admin role.
    Use for: Product management, inventory, category editing, order management.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        role = claims.get('role')
        
        if role not in ['admin', 'manager']:
            return jsonify({
                'error': 'Manager access required',
                'your_role': role,
                'required_roles': ['admin', 'manager']
            }), 403
        
        return fn(*args, **kwargs)
    return wrapper


def staff_required(fn):
    """
    Require cashier, manager, or admin role.
    Use for: Order processing, basic order viewing, customer service.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        role = claims.get('role')
        
        if role not in ['admin', 'manager', 'cashier']:
            return jsonify({
                'error': 'Staff access required',
                'your_role': role,
                'required_roles': ['admin', 'manager', 'cashier']
            }), 403
        
        return fn(*args, **kwargs)
    return wrapper


def customer_required(fn):
    """
    Require customer role (authenticated user).
    Use for: Cart, own orders, profile management.
    Note: This is mainly for clarity - jwt_required() alone works too.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        role = claims.get('role')
        
        if role not in ['customer', 'admin', 'manager', 'cashier']:
            return jsonify({
                'error': 'Authentication required',
                'your_role': role
            }), 403
        
        return fn(*args, **kwargs)
    return wrapper


def admin_only(fn):
    """
    Strict admin-only access (not manager, not cashier).
    Use for: Creating admins, deleting categories, changing prices, refunds.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        role = claims.get('role')
        
        if role != 'admin':
            return jsonify({
                'error': 'This action requires admin privileges',
                'your_role': role,
                'message': 'Only the system administrator can perform this action'
            }), 403
        
        return fn(*args, **kwargs)
    return wrapper


# Helper function to check specific permissions
def has_permission(required_roles):
    """
    Helper to check if user has required role.
    
    Usage:
        if not has_permission(['admin', 'manager']):
            return jsonify({'error': 'Access denied'}), 403
    """
    claims = get_jwt()
    user_role = claims.get('role')
    return user_role in required_roles


def get_current_user_role():
    """Get the current user's role from JWT."""
    claims = get_jwt()
    return claims.get('role')


def is_admin():
    """Check if current user is admin."""
    return get_current_user_role() == 'admin'


def is_manager():
    """Check if current user is manager or admin."""
    return get_current_user_role() in ['admin', 'manager']


def is_staff():
    """Check if current user is staff (cashier, manager, or admin)."""
    return get_current_user_role() in ['admin', 'manager', 'cashier']


def is_customer():
    """Check if current user is customer."""
    return get_current_user_role() == 'customer'