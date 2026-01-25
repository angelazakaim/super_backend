from flask_jwt_extended import create_access_token, create_refresh_token
from app.repositories.user_repository import UserRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.employee_repository import EmployeeRepository
from app.extensions import db
from app.enums import UserRole
import logging

logger = logging.getLogger(__name__)


class AuthService:
    @staticmethod
    def register(email, username, password, role=UserRole.CUSTOMER.value, profile_data=None):
        """
        Register a new user and create the appropriate profile.
        
        Uses atomic transaction - BOTH User and Profile are created together,
        or NEITHER is created if any error occurs.
        
        This prevents orphaned users without profiles!
        """
        # Validate role
        if not UserRole.is_valid(role):
            raise ValueError(f"Invalid role. Must be one of: {', '.join(UserRole.values())}")
        
        # Check if email/username exists BEFORE starting transaction
        if UserRepository.exists_by_email(email):
            raise ValueError("Email already registered")
        
        if UserRepository.exists_by_username(username):
            raise ValueError("Username already taken")
        
        try:
            logger.info(f"Starting registration for {email} with role {role}")
            
            # Create User WITHOUT committing (adds to session only)
            user = UserRepository.create_without_commit(
                email=email, 
                username=username, 
                password=password, 
                role=role
            )
            logger.info(f"User object created (not committed): {user.email}, ID: {user.id}")
            
            # Create Profile WITHOUT committing (adds to session only)
            profile = None
            if role == UserRole.CUSTOMER.value:
                profile = CustomerRepository.create_without_commit(
                    user_id=user.id, 
                    **(profile_data or {})
                )
                logger.info(f"Customer profile created (not committed) for user {user.id}")
            elif role in [UserRole.MANAGER.value, UserRole.CASHIER.value]:
                profile = EmployeeRepository.create_without_commit(
                    user_id=user.id, 
                    **(profile_data or {})
                )
                logger.info(f"Employee profile created (not committed) for user {user.id}")
            
            # ATOMIC COMMIT - Both User and Profile saved together!
            db.session.commit()
            logger.info(f"✅ Transaction committed: User {user.email} (ID: {user.id}) registered successfully")
            
            return user, profile
        
        except Exception as e:
            # If ANYTHING fails, rollback EVERYTHING - no orphaned users!
            db.session.rollback()
            logger.error(f"❌ Registration failed, transaction rolled back: {e}", exc_info=True)
            raise  # Re-raise the exception to be handled by the route

    @staticmethod
    def login(email_or_username, password):
        """Login user and generate JWT tokens."""
        user = UserRepository.get_by_email(email_or_username) or \
               UserRepository.get_by_username(email_or_username)
        
        if not user or not user.check_password(password) or not user.is_active:
            raise ValueError("Invalid credentials or inactive account")
        
        # Generate tokens with STRING identity (JWT standard)
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'role': user.role}
        )
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': user.to_dict()
        }
    
    @staticmethod
    def refresh_token(user_id):
        """Generate new access token."""
        # Convert to int if string
        if isinstance(user_id, str):
            user_id = int(user_id)
            
        user = UserRepository.get_by_id(user_id)
        if not user or not user.is_active:
            raise ValueError("Invalid user")
        
        access_token = create_access_token(
            identity=str(user.id),
            additional_claims={'role': user.role}
        )
        return {'access_token': access_token}
    
    @staticmethod
    def change_password(user_id, old_password, new_password):
        """Change user password."""
        # Convert to int if string
        if isinstance(user_id, str):
            user_id = int(user_id)
            
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        if not user.check_password(old_password):
            raise ValueError("Invalid current password")
        UserRepository.update(user, password=new_password)
        return user
