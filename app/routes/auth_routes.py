from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "Invalid JSON"}), 400

        
        # Validate required fields
        required_fields = ['email', 'username', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Extract customer data
        customer_data = {
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'phone': data.get('phone')
        }
        
        user, customer = AuthService.register(
            email=data['email'],
            username=data['username'],
            password=data['password'],
            customer_data=customer_data
        )
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict(),
            'customer': customer.to_dict()
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Registration failed'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user."""
    try:
        
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
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
        return jsonify({'error': 'Login failed'}), 500

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    try:
        user_id = get_jwt_identity()
        result = AuthService.refresh_token(user_id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': 'Token refresh failed'}), 401

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change user password."""
    try:
        user_id = get_jwt_identity()
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
        if not data.get('old_password') or not data.get('new_password'):
            return jsonify({'error': 'Old and new passwords are required'}), 400
        
        AuthService.change_password(
            user_id=user_id,
            old_password=data['old_password'],
            new_password=data['new_password']
        )
        
        return jsonify({'message': 'Password changed successfully'}), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Password change failed'}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information."""
    try:
        from app.repositories.user_repository import UserRepository
        from app.repositories.customer_repository import CustomerRepository
        
        user_id = get_jwt_identity()
        user = UserRepository.get_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        customer = CustomerRepository.get_by_user_id(user_id)
        
        return jsonify({
            'user': user.to_dict(),
            'customer': customer.to_dict() if customer else None
        }), 200
    
    except Exception as e:
        return jsonify({'error': 'Failed to fetch user'}), 500
    
    
    
    
    
    
@auth_bp.route('/debug-token', methods=['GET'])
@jwt_required()
def debug_token():
    """Debug endpoint to check token contents."""
    from flask_jwt_extended import get_jwt_identity, get_jwt
    
    user_id = get_jwt_identity()
    claims = get_jwt()
    
    return jsonify({
        'user_id': user_id,
        'claims': claims,
        'has_role': 'role' in claims,
        'role': claims.get('role', 'NOT FOUND')
    }), 200