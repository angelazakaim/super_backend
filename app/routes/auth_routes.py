from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.auth_service import AuthService
import logging

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')
logger = logging.getLogger(__name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    try:
        data = request.get_json()
        logger.info(f"Registration attempt for email: {data.get('email')}")
        
        # Validate required fields
        required_fields = ['email', 'username', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Extract role (default to customer)
        role = data.get('role', 'customer')
        
        # Extract profile data based on role
        profile_data = {}
        if role == 'customer':
            profile_data = {
                'first_name': data.get('first_name'),
                'last_name': data.get('last_name'),
                'phone': data.get('phone'),
                'address_line1': data.get('address_line1'),
                'address_line2': data.get('address_line2'),
                'city': data.get('city'),
                'state': data.get('state'),
                'postal_code': data.get('postal_code'),
                'country': data.get('country')
            }
        elif role in ['manager', 'cashier']:
            profile_data = {
                'first_name': data.get('first_name'),
                'last_name': data.get('last_name'),
                'phone': data.get('phone'),
                'hire_date': data.get('hire_date'),
                'salary': data.get('salary')
            }
        
        logger.info(f"Registering user with role: {role}")
        user, profile = AuthService.register(
            email=data['email'],
            username=data['username'],
            password=data['password'],
            role=role,
            profile_data=profile_data
        )
        
        logger.info(f"User registered successfully: {user.email} (ID: {user.id})")
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'profile': profile.to_dict() if profile else None
        }), 201
    
    except ValueError as e:
        logger.warning(f"Registration validation error: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Registration failed: {e}", exc_info=True)
        # Return the actual error message for debugging
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user."""
    try:
        data = request.get_json()
        
        if not data.get('email_or_username') or not data.get('password'):
            return jsonify({'error': 'Email/username and password are required'}), 400
        
        result = AuthService.login(
            email_or_username=data['email_or_username'],
            password=data['password']
        )
        
        return jsonify(result), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        logger.error(f"Login failed: {e}", exc_info=True)
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    try:
        user_id = get_jwt_identity()
        result = AuthService.refresh_token(int(user_id))  # Convert to int
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Token refresh failed: {e}", exc_info=True)
        return jsonify({'error': f'Token refresh failed: {str(e)}'}), 401

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data.get('old_password') or not data.get('new_password'):
            return jsonify({'error': 'Old and new passwords are required'}), 400
        
        AuthService.change_password(
            user_id=int(user_id),  # Convert to int
            old_password=data['old_password'],
            new_password=data['new_password']
        )
        
        return jsonify({'message': 'Password changed successfully'}), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Password change failed: {e}", exc_info=True)
        return jsonify({'error': f'Password change failed: {str(e)}'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information."""
    try:
        from app.repositories.user_repository import UserRepository
        from app.repositories.customer_repository import CustomerRepository
        
        user_id = int(get_jwt_identity())  # Convert to int
        user = UserRepository.get_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        customer = CustomerRepository.get_by_user_id(user_id)
        
        return jsonify({
            'user': user.to_dict(),
            'customer': customer.to_dict() if customer else None
        }), 200
    
    except Exception as e:
        logger.error(f"Failed to fetch user: {e}", exc_info=True)
        return jsonify({'error': f'Failed to fetch user: {str(e)}'}), 500

@auth_bp.route('/debug-token', methods=['GET'])
@jwt_required()
def debug_token():
    """Debug endpoint to check token contents."""
    from flask_jwt_extended import get_jwt
    
    user_id = get_jwt_identity()
    claims = get_jwt()
    
    return jsonify({
        'user_id': user_id,
        'claims': claims,
        'has_role': 'role' in claims,
        'role': claims.get('role', 'NOT FOUND')
    }), 200