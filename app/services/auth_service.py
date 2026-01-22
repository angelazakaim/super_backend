from flask_jwt_extended import create_access_token, create_refresh_token
from app.repositories.user_repository import UserRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.employee_repository import EmployeeRepository

class AuthService:
    @staticmethod
    def register(email, username, password, role='customer', profile_data=None):
        """Register a new user and create the appropriate profile."""
        if UserRepository.exists_by_email(email):
            raise ValueError("Email already registered")
        
        if UserRepository.exists_by_username(username):
            raise ValueError("Username already taken")
        
        # 1. Create the base User
        user = UserRepository.create(email=email, username=username, password=password, role=role)
        
        # 2. Create the specific Profile based on role
        profile = None
        if role == 'customer':
            profile = CustomerRepository.create(user_id=user.id, **(profile_data or {}))
        elif role in ['manager', 'cashier']:
            profile = EmployeeRepository.create(user_id=user.id, **(profile_data or {}))
        
        return user, profile

    @staticmethod
    def login(email_or_username, password):
        user = UserRepository.get_by_email(email_or_username) or \
               UserRepository.get_by_username(email_or_username)
        
        if not user or not user.check_password(password) or not user.is_active:
            raise ValueError("Invalid credentials or inactive account")
        
        # Include the role in the JWT token for frontend permissions
        # Generate tokens with STRING identity to avoid "Subject must be a string" error
        access_token = create_access_token(
            identity=str(user.id),  # ← FIXED: Convert to string
            additional_claims={'role': user.role}
        )
        refresh_token = create_refresh_token(identity=str(user.id))  # ← FIXED: Convert to string
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }
    
    @staticmethod
    def refresh_token(user_id):
        """Generate new access token."""
        user = UserRepository.get_by_id(user_id)
        if not user or not user.is_active:
            raise ValueError("Invalid user")
        
        # FIXED: Convert to string
        access_token = create_access_token(
            identity=str(user.id),  # ← FIXED: Convert to string
            additional_claims={'role': user.role}
        )
        return {'access_token': access_token}
    
    @staticmethod
    def change_password(user_id, old_password, new_password):
        """Change user password."""
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        if not user.check_password(old_password):
            raise ValueError("Invalid current password")
        UserRepository.update(user, password=new_password)
        return user