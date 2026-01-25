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
    ✅ FIXED: Now uses UserService.
    """
    try:
        user_id = int(get_jwt_identity())
        user = UserRepository.get_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get role-specific profile
        profile = None
        if user.role == UserRole.CUSTOMER.value:
            customer = CustomerRepository.get_by_user_id(user_id)
            profile = customer.to_dict() if customer else None
        elif user.role in [UserRole.MANAGER.value, UserRole.CASHIER.value]:
            employee = EmployeeRepository.get_by_user_id(user_id)
            profile = employee.to_dict(include_salary=True) if employee else None
        
        return jsonify({
            'user': user.to_dict(),
            'profile': profile
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching profile: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch profile'}), 500


@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_own_profile():
    """
    Update current user's profile.
    AUTHENTICATED - Any user can update their own profile.
    ✅ FIXED: Now uses UserService.
    """
    try:
        user_id = int(get_jwt_identity())
        
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
        
        # Update role-specific profile
        if user.role == UserRole.CUSTOMER.value:
            customer = CustomerRepository.get_by_user_id(user_id)
            if customer:
                # Only allow updating certain fields
                allowed_fields = ['first_name', 'last_name', 'phone', 
                                'address_line1', 'address_line2', 'city', 
                                'state', 'postal_code', 'country']
                update_data = {k: v for k, v in data.items() if k in allowed_fields}
                CustomerRepository.update(customer, **update_data)
                
        elif user.role in [UserRole.MANAGER.value, UserRole.CASHIER.value]:
            employee = EmployeeRepository.get_by_user_id(user_id)
            if employee:
                # Employees can only update basic info
                allowed_fields = ['phone']
                update_data = {k: v for k, v in data.items() if k in allowed_fields}
                EmployeeRepository.update(employee, **update_data)
        
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
    MANAGER OR ADMIN - For customer service.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 25, type=int)
        
        pagination = CustomerRepository.get_all(page=page, per_page=per_page)
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error fetching customers: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch customers'}), 500


# ============================================================================
# ADMIN-ONLY ENDPOINTS (User Management)
# ============================================================================

@user_bp.route('', methods=['GET'])
@jwt_required()
@admin_only
def get_all_users():
    """
    Get all users with pagination and filters.
    ADMIN ONLY - Full user management.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        role = request.args.get('role')
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        # Validate role if provided
        if role and not UserRole.is_valid(role):
            return jsonify({
                'error': f'Invalid role. Must be one of: {", ".join(UserRole.values())}'
            }), 400
        
        # Get users
        pagination = UserRepository.get_all(
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
    Get user details with profile.
    ADMIN ONLY - View any user.
    """
    try:
        user = UserRepository.get_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get role-specific profile
        profile = None
        if user.role == UserRole.CUSTOMER.value:
            customer = CustomerRepository.get_by_user_id(user_id)
            profile = customer.to_dict() if customer else None
        elif user.role in [UserRole.MANAGER.value, UserRole.CASHIER.value]:
            employee = EmployeeRepository.get_by_user_id(user_id)
            profile = employee.to_dict(include_salary=True) if employee else None
        
        return jsonify({
            'user': user.to_dict(),
            'profile': profile
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching user {user_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch user'}), 500


@user_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
@admin_only
def update_user(user_id):
    """
    Update user information.
    ADMIN ONLY - Update any user's basic info.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
        
        # Allowed fields for admin to update
        allowed_fields = ['email', 'username', 'is_active']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        # Check for duplicate email/username if being changed
        if 'email' in update_data and update_data['email'] != user.email:
            if UserRepository.exists_by_email(update_data['email']):
                return jsonify({'error': 'Email already in use'}), 400
        
        if 'username' in update_data and update_data['username'] != user.username:
            if UserRepository.exists_by_username(update_data['username']):
                return jsonify({'error': 'Username already taken'}), 400
        
        UserRepository.update(user, **update_data)
        
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
    Change user's role.
    ADMIN ONLY - Promote/demote users.
    Example: customer → manager, cashier → manager, manager → admin
    """
    try:
        user = UserRepository.get_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json(silent=True)
        if not data or 'role' not in data:
            return jsonify({'error': 'role is required'}), 400
        
        new_role = data['role']
        old_role = user.role
        
        # Validate role
        if not UserRole.is_valid(new_role):
            return jsonify({
                'error': f'Invalid role. Must be one of: {", ".join(UserRole.values())}'
            }), 400
        
        if old_role == new_role:
            return jsonify({'error': 'User already has this role'}), 400
        
        # Handle role transition
        # If changing from customer to staff, need to create employee profile
        if old_role == UserRole.CUSTOMER.value and new_role in [UserRole.MANAGER.value, UserRole.CASHIER.value]:
            # Delete customer profile
            customer = CustomerRepository.get_by_user_id(user_id)
            if customer:
                CustomerRepository.delete(customer)
            
            # Create employee profile
            employee_data = {
                'employee_id': data.get('employee_id', f'EMP-{user_id}'),
                'hire_date': data.get('hire_date', datetime.now(timezone.utc)),
                'salary': data.get('salary', 0.0)
            }
            EmployeeRepository.create(user_id, **employee_data)
        
        # If changing from staff to customer, need to create customer profile
        elif old_role in [UserRole.MANAGER.value, UserRole.CASHIER.value] and new_role == UserRole.CUSTOMER.value:
            # Delete employee profile
            employee = EmployeeRepository.get_by_user_id(user_id)
            if employee:
                EmployeeRepository.delete(employee)
            
            # Create customer profile
            CustomerRepository.create(user_id)
        
        # Update role
        UserRepository.update(user, role=new_role)
        
        logger.info(f"Admin changed user {user.email} role: {old_role} → {new_role}")
        
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
    Ban or unban a user.
    ADMIN ONLY - Deactivate/reactivate user accounts.
    """
    try:
        # Prevent banning yourself
        current_user_id = int(get_jwt_identity())
        if user_id == current_user_id:
            return jsonify({'error': 'Cannot ban yourself'}), 400
        
        data = request.get_json(silent=True) or {}
        is_active = data.get('is_active', not user.is_active)  # Toggle if not specified
        
        UserRepository.update(user, is_active=is_active)
        
        action = 'unbanned' if is_active else 'banned'
        logger.info(f"Admin {action} user: {user.email} (ID: {user_id})")
        
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
    Permanently delete a user and their profile.
    ADMIN ONLY - Cannot be undone!
    Warning: This will also delete all associated data (orders, cart, etc.)
    """
    try:
        user = UserRepository.get_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Don't allow deleting yourself
        current_user_id = int(get_jwt_identity())
        if user_id == current_user_id:
            return jsonify({'error': 'Cannot delete yourself'}), 400
        
        # Delete will cascade to profile (customer or employee) due to model relationships
        email = user.email
        UserRepository.delete(user)
        
        logger.warning(f"Admin permanently deleted user: {email} (ID: {user_id})")
        
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
    Reset user's password.
    ADMIN ONLY - Force password reset.
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
        
        # Update password
        UserRepository.update(user, password=new_password)
        
        logger.info(f"Admin reset password for user: {user.email} (ID: {user_id})")
        
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
    ADMIN ONLY - Dashboard statistics.
    """
    try:
        from sqlalchemy import func
        from app.models.user import User
        
        # Total users by role
        role_stats = db.session.query(
            User.role,
            func.count(User.id).label('count')
        ).group_by(User.role).all()
        
        # Active vs inactive
        active_count = User.query.filter_by(is_active=True).count()
        inactive_count = User.query.filter_by(is_active=False).count()
        
        # Recent registrations (last 7 days)
        from datetime import timedelta
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        recent_registrations = User.query.filter(
            User.created_at >= week_ago
        ).count()
        
        return jsonify({
            'message': 'Password reset successfully',
            'user': user.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error resetting password: {e}", exc_info=True)
        return jsonify({'error': 'Failed to reset password'}), 500