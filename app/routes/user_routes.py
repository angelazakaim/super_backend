"""User management routes - FIXED VERSION using UserService."""
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.user_service import UserService
from app.utils.decorators import admin_only, manager_required
from app.enums import UserRole

logger = logging.getLogger(__name__)
user_bp = Blueprint('users', __name__, url_prefix='/api/users')


# ============================================================================
# AUTHENTICATED USER ENDPOINTS (Own Profile)
# ============================================================================

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_own_profile():
    """
    Get current user's full profile.
    AUTHENTICATED - Any user can view their own profile.
    """
    try:
        user_id = int(get_jwt_identity())
        
        result = UserService.get_user(user_id, include_profile=True)
        
        return jsonify(result), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error fetching profile: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch profile'}), 500


@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_own_profile():
    """
    Update current user's profile.
    AUTHENTICATED - Any user can update their own profile.
    """
    try:
        user_id = int(get_jwt_identity())
        
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
        
        result = UserService.update_profile(user_id, data)
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': result['user'],
            'profile': result.get('profile')
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating profile: {e}", exc_info=True)
        return jsonify({'error': 'Failed to update profile'}), 500


# ============================================================================
# MANAGER ENDPOINTS (Managers can view customers)
# ============================================================================

@user_bp.route('/customers', methods=['GET'])
@jwt_required()
@manager_required
def get_all_customers():
    """
    Get all customers with pagination.
    MANAGER OR ADMIN - Managers can view customer list.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 25, type=int)
        
        result = UserService.get_all_customers(page=page, per_page=per_page)
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error fetching customers: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch customers'}), 500


@user_bp.route('/employees', methods=['GET'])
@jwt_required()
@manager_required
def get_all_employees():
    """
    Get all employees (managers + cashiers) with pagination.
    MANAGER OR ADMIN - Managers can view employee list.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 25, type=int)
        role = request.args.get('role', None, type=str)

        result = UserService.get_all_employees(page=page, per_page=per_page, role_filter=role)

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error fetching employees: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch employees'}), 500


# ============================================================================
# ADMIN-ONLY ENDPOINTS (User Management)
# ============================================================================

@user_bp.route('', methods=['GET'])
@jwt_required()
@admin_only
def get_all_users():
    """
    Get all users with pagination and optional role filter.
    ADMIN ONLY - View all users in system.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 25, type=int)
        role_filter = request.args.get('role', None, type=str)
        
        result = UserService.get_all_users(
            page=page,
            per_page=per_page,
            role_filter=role_filter
        )
        
        return jsonify(result), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error fetching users: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch users'}), 500


@user_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
@admin_only
def get_user_by_id(user_id):
    """
    Get specific user by ID.
    ADMIN ONLY - View any user's details.
    """
    try:
        result = UserService.get_user(user_id, include_profile=True)
        
        return jsonify(result), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch user'}), 500


@user_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
@admin_only
def update_user(user_id):
    """
    Update user account data.
    ADMIN ONLY - Can update any user account.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
        
        # Allowed fields for admin to update
        allowed_fields = ['email', 'username', 'is_active']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not update_data:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        user = UserService.update_user(user_id, **update_data)
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating user {user_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to update user'}), 500


@user_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_only
def delete_user(user_id):
    """
    Delete user permanently.
    ADMIN ONLY - Permanent deletion (use with caution!).
    """
    try:
        # Prevent deleting yourself
        current_user_id = int(get_jwt_identity())
        if current_user_id == user_id:
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        UserService.delete_user(user_id)
        
        return jsonify({
            'message': 'User deleted successfully',
            'warning': 'This action cannot be undone'
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error deleting user {user_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to delete user'}), 500


@user_bp.route('/<int:user_id>/ban', methods=['POST'])
@jwt_required()
@admin_only
def ban_user(user_id):
    """
    Ban user (set is_active to False).
    ADMIN ONLY - Temporarily disable user account.
    """
    try:
        # Prevent banning yourself
        current_user_id = int(get_jwt_identity())
        if current_user_id == user_id:
            return jsonify({'error': 'Cannot ban your own account'}), 400
        
        user = UserService.ban_user(user_id)
        
        return jsonify({
            'message': 'User banned successfully',
            'user': user.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error banning user {user_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to ban user'}), 500


@user_bp.route('/<int:user_id>/unban', methods=['POST'])
@jwt_required()
@admin_only
def unban_user(user_id):
    """
    Unban user (set is_active to True).
    ADMIN ONLY - Re-enable disabled user account.
    """
    try:
        user = UserService.unban_user(user_id)
        
        return jsonify({
            'message': 'User unbanned successfully',
            'user': user.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error unbanning user {user_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to unban user'}), 500


@user_bp.route('/<int:user_id>/role', methods=['PUT'])
@jwt_required()
@admin_only
def change_user_role(user_id):
    """
    Change user role.
    ADMIN ONLY - Promote/demote users between roles.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
        
        new_role = data.get('role')
        if not new_role:
            return jsonify({'error': 'role is required'}), 400
        
        # Validate role
        if not UserRole.is_valid(new_role):
            return jsonify({
                'error': f'Invalid role. Must be one of: {", ".join(UserRole.values())}'
            }), 400
        
        # Employee data for role transitions
        employee_data = None
        if new_role in [UserRole.MANAGER.value, UserRole.CASHIER.value]:
            employee_data = {
                'first_name': data.get('first_name'),
                'last_name': data.get('last_name'),
                'phone': data.get('phone'),
                'employee_id': data.get('employee_id'),
                'salary': data.get('salary')
            }
        
        result = UserService.change_user_role(
            user_id=user_id,
            new_role=new_role,
            employee_data=employee_data
        )
        
        return jsonify({
            'message': 'User role changed successfully',
            'user': result['user'],
            'profile': result.get('profile')
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error changing user role: {e}", exc_info=True)
        return jsonify({'error': 'Failed to change user role'}), 500


@user_bp.route('/statistics', methods=['GET'])
@jwt_required()
@admin_only
def get_user_statistics():
    """
    Get user statistics.
    ADMIN ONLY - View user counts and analytics.
    """
    try:
        stats = UserService.get_user_statistics()
        
        return jsonify(stats), 200
    
    except Exception as e:
        logger.error(f"Error fetching user statistics: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch user statistics'}), 500


@user_bp.route('/<int:user_id>/password-reset', methods=['POST'])
@jwt_required()
@admin_only
def admin_reset_password(user_id):
    """
    Admin reset user password.
    ADMIN ONLY - Reset password for any user.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
        
        new_password = data.get('new_password')
        if not new_password:
            return jsonify({'error': 'new_password is required'}), 400
        
        # Validate password length
        if len(new_password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        
        
        user = UserService.update_user(user_id, password=new_password)
        
        return jsonify({
            'message': 'Password reset successfully',
            'user': user.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error resetting password: {e}", exc_info=True)
        return jsonify({'error': 'Failed to reset password'}), 500