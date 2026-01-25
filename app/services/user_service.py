"""User service with business logic and validation."""
import logging
from typing import Optional, Any
from app.repositories.user_repository import UserRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.employee_repository import EmployeeRepository
from app.extensions import db
from app.enums import UserRole

logger = logging.getLogger(__name__)


class UserService:
    """Service for user operations with validation and business logic."""
    
    @staticmethod
    def get_user(user_id: int, include_profile: bool = True) -> dict:
        """
        Get user by ID with optional profile.
        
        Args:
            user_id: User ID
            include_profile: Whether to include customer/employee profile
            
        Returns:
            Dictionary with user data
            
        Raises:
            ValueError: If user not found
        """
        logger.info(f"Fetching user with ID: {user_id}")
        
        user = UserRepository.get_by_id(user_id)
        if not user:
            logger.warning(f"User not found: {user_id}")
            raise ValueError("User not found")
        
        result = {'user': user.to_dict()}
        
        if include_profile:
            if user.role == UserRole.CUSTOMER.value:
                customer = CustomerRepository.get_by_user_id(user_id)
                result['profile'] = customer.to_dict() if customer else None
            elif user.role in [UserRole.MANAGER.value, UserRole.CASHIER.value]:
                employee = EmployeeRepository.get_by_user_id(user_id)
                # FIXED: Use to_dict() method instead of __dict__
                result['profile'] = employee.to_dict(include_salary=True) if employee else None
        
        logger.info(f"Successfully fetched user: {user.username}")
        return result
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[Any]:
        """Get user by email."""
        logger.info(f"Fetching user by email: {email}")
        
        user = UserRepository.get_by_email(email)
        if not user:
            logger.warning(f"User not found with email: {email}")
            return None
        
        return user
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[Any]:
        """Get user by username."""
        logger.info(f"Fetching user by username: {username}")
        
        user = UserRepository.get_by_username(username)
        if not user:
            logger.warning(f"User not found with username: {username}")
            return None
        
        return user
    
    @staticmethod
    def create_user(
        email: str,
        username: str,
        password: str,
        role: str = UserRole.CUSTOMER.value,
        profile_data: Optional[dict] = None
    ) -> dict:
        """
        Create a new user with profile using ATOMIC TRANSACTIONS.
        
        FIXED: Now uses create_without_commit() to prevent orphaned users!
        
        Args:
            email: User email
            username: Username
            password: Plain text password (will be hashed)
            role: User role (customer, admin, manager, cashier)
            profile_data: Additional profile data
            
        Returns:
            Dictionary with user and profile data
            
        Raises:
            ValueError: If validation fails
        """
        logger.info(f"Creating user: {username} ({email}) with role: {role}")
        
        # Validate role
        if not UserRole.is_valid(role):
            logger.error(f"Invalid role: {role}")
            raise ValueError(f"Role must be one of: {', '.join(UserRole.values())}")
        
        # Check if email exists
        if UserRepository.exists_by_email(email):
            logger.error(f"Email already exists: {email}")
            raise ValueError("Email already registered")
        
        # Check if username exists
        if UserRepository.exists_by_username(username):
            logger.error(f"Username already exists: {username}")
            raise ValueError("Username already taken")
        
        # Validate email format
        if not UserService._is_valid_email(email):
            logger.error(f"Invalid email format: {email}")
            raise ValueError("Invalid email format")
        
        # Validate password strength
        is_valid, msg = UserService.validate_password_complexity(password)
        if not is_valid:
            logger.error(f"Weak password: {msg}")
            raise ValueError(msg)
        
        try:
            # ✅ ATOMIC TRANSACTION - Create user WITHOUT committing
            user = UserRepository.create_without_commit(
                email=email,
                username=username,
                password=password,
                role=role
            )
            logger.info(f"User object created (not committed): {user.email}, ID: {user.id}")
            
            # ✅ Create profile WITHOUT committing
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
            
            # ✅ COMMIT BOTH TOGETHER - Both saved or both fail!
            db.session.commit()
            logger.info(f"✅ Transaction committed: User {user.email} (ID: {user.id}) created successfully")
            
            return {
                'user': user,
                'profile': profile
            }
            
        except Exception as e:
            # ✅ ROLLBACK EVERYTHING - No orphaned users!
            db.session.rollback()
            logger.error(f"❌ User creation failed, transaction rolled back: {e}", exc_info=True)
            raise ValueError(f"Failed to create user: {str(e)}")
    
    @staticmethod
    def update_user(user_id: int, **kwargs) -> Any:
        """
        Update user information.
        
        Args:
            user_id: User ID
            **kwargs: Fields to update
            
        Returns:
            Updated user
            
        Raises:
            ValueError: If validation fails
        """
        logger.info(f"Updating user: {user_id}")
        
        user = UserRepository.get_by_id(user_id)
        if not user:
            logger.error(f"User not found: {user_id}")
            raise ValueError("User not found")
        
        # Validate email if being updated
        if 'email' in kwargs and kwargs['email'] != user.email:
            if UserRepository.exists_by_email(kwargs['email']):
                logger.error(f"Email already exists: {kwargs['email']}")
                raise ValueError("Email already in use")
            
            if not UserService._is_valid_email(kwargs['email']):
                logger.error(f"Invalid email format: {kwargs['email']}")
                raise ValueError("Invalid email format")
        
        # Validate username if being updated
        if 'username' in kwargs and kwargs['username'] != user.username:
            if UserRepository.exists_by_username(kwargs['username']):
                logger.error(f"Username already exists: {kwargs['username']}")
                raise ValueError("Username already taken")
        
        # Validate role if being updated
        if 'role' in kwargs:
            if not UserRole.is_valid(kwargs['role']):
                logger.error(f"Invalid role: {kwargs['role']}")
                raise ValueError(f"Role must be one of: {', '.join(UserRole.values())}")
        
        try:
            updated_user = UserRepository.update(user, **kwargs)
            logger.info(f"Successfully updated user: {user_id}")
            return updated_user
        except Exception as e:
            logger.error(f"Failed to update user: {e}", exc_info=True)
            db.session.rollback()
            raise ValueError(f"Failed to update user: {str(e)}")
    
    @staticmethod
    def update_profile(user_id: int, **kwargs) -> Any:
        """
        Update user's profile (customer or employee).
        
        Args:
            user_id: User ID
            **kwargs: Profile fields to update
            
        Returns:
            Updated profile
            
        Raises:
            ValueError: If profile not found
        """
        logger.info(f"Updating profile for user: {user_id}")
        
        user = UserRepository.get_by_id(user_id)
        if not user:
            logger.error(f"User not found: {user_id}")
            raise ValueError("User not found")
        
        try:
            if user.role == UserRole.CUSTOMER.value:
                customer = CustomerRepository.get_by_user_id(user_id)
                if not customer:
                    logger.error(f"Customer profile not found for user: {user_id}")
                    raise ValueError("Customer profile not found")
                
                updated_profile = CustomerRepository.update(customer, **kwargs)
                logger.info(f"Successfully updated customer profile for user: {user_id}")
                return updated_profile
                
            elif user.role in [UserRole.MANAGER.value, UserRole.CASHIER.value]:
                employee = EmployeeRepository.get_by_user_id(user_id)
                if not employee:
                    logger.error(f"Employee profile not found for user: {user_id}")
                    raise ValueError("Employee profile not found")
                
                # FIXED: Use EmployeeRepository.update() method
                updated_profile = EmployeeRepository.update(employee, **kwargs)
                logger.info(f"Successfully updated employee profile for user: {user_id}")
                return updated_profile
            else:
                logger.error(f"User role '{user.role}' does not have a profile")
                raise ValueError("User role does not have a profile")
                
        except Exception as e:
            logger.error(f"Failed to update profile: {e}", exc_info=True)
            db.session.rollback()
            raise ValueError(f"Failed to update profile: {str(e)}")
    
    @staticmethod
    def deactivate_user(user_id: int) -> Any:
        """
        Deactivate user account.
        
        Args:
            user_id: User ID
            
        Returns:
            Deactivated user
            
        Raises:
            ValueError: If user not found
        """
        logger.info(f"Deactivating user: {user_id}")
        
        user = UserRepository.get_by_id(user_id)
        if not user:
            logger.error(f"User not found: {user_id}")
            raise ValueError("User not found")
        
        try:
            updated_user = UserRepository.update(user, is_active=False)
            logger.info(f"Successfully deactivated user: {user_id}")
            return updated_user
        except Exception as e:
            logger.error(f"Failed to deactivate user: {e}", exc_info=True)
            db.session.rollback()
            raise ValueError(f"Failed to deactivate user: {str(e)}")
    
    @staticmethod
    def activate_user(user_id: int) -> Any:
        """
        Activate user account.
        
        Args:
            user_id: User ID
            
        Returns:
            Activated user
            
        Raises:
            ValueError: If user not found
        """
        logger.info(f"Activating user: {user_id}")
        
        user = UserRepository.get_by_id(user_id)
        if not user:
            logger.error(f"User not found: {user_id}")
            raise ValueError("User not found")
        
        try:
            updated_user = UserRepository.update(user, is_active=True)
            logger.info(f"Successfully activated user: {user_id}")
            return updated_user
        except Exception as e:
            logger.error(f"Failed to activate user: {e}", exc_info=True)
            db.session.rollback()
            raise ValueError(f"Failed to activate user: {str(e)}")
    
    @staticmethod
    def delete_user(user_id: int, hard_delete: bool = False) -> None:
        """
        Delete user (soft delete by default).
        
        Args:
            user_id: User ID
            hard_delete: Whether to permanently delete (default: False)
            
        Raises:
            ValueError: If user not found
        """
        logger.info(f"Deleting user: {user_id} (hard_delete={hard_delete})")
        
        user = UserRepository.get_by_id(user_id)
        if not user:
            logger.error(f"User not found: {user_id}")
            raise ValueError("User not found")
        
        try:
            if hard_delete:
                UserRepository.delete(user)
                logger.warning(f"Hard deleted user: {user_id}")
            else:
                UserRepository.update(user, is_active=False)
                logger.info(f"Soft deleted user: {user_id}")
        except Exception as e:
            logger.error(f"Failed to delete user: {e}", exc_info=True)
            db.session.rollback()
            raise ValueError(f"Failed to delete user: {str(e)}")
    
    @staticmethod
    def get_all_users(
        page: int = 1,
        per_page: int = 20,
        role: Optional[str] = None,
        active_only: bool = True
    ) -> Any:
        """
        Get all users with optional filters.
        
        Args:
            page: Page number
            per_page: Items per page
            role: Filter by role
            active_only: Only include active users
            
        Returns:
            Paginated user results
        """
        logger.info(f"Fetching all users (role={role}, active_only={active_only})")
        
        # Validate role if provided
        if role and not UserRole.is_valid(role):
            raise ValueError(f"Invalid role. Must be one of: {', '.join(UserRole.values())}")
        
        try:
            results = UserRepository.get_all(
                page=page,
                per_page=per_page,
                active_only=active_only
            )
            
            logger.info(f"Fetched {results.total} users")
            return results
            
        except Exception as e:
            logger.error(f"Failed to fetch users: {e}", exc_info=True)
            raise ValueError(f"Failed to fetch users: {str(e)}")
    
    # Helper methods
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Validate email format."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def _is_strong_password(password: str) -> bool:
        """
        Validate password strength (basic check).
        
        DEPRECATED: Use validate_password_complexity() instead.
        
        Requirements:
        - At least 8 characters
        - Contains letters and numbers
        """
        if len(password) < 8:
            return False
        
        has_letter = any(c.isalpha() for c in password)
        has_number = any(c.isdigit() for c in password)
        
        return has_letter and has_number
    
    @staticmethod
    def validate_password_complexity(password: str) -> tuple[bool, str]:
        """
        Validate password with detailed feedback.
        
        Returns:
            Tuple of (is_valid, message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if len(password) > 128:
            return False, "Password must be less than 128 characters"
        
        has_uppercase = any(c.isupper() for c in password)
        has_lowercase = any(c.islower() for c in password)
        has_number = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
        
        if not (has_uppercase and has_lowercase):
            return False, "Password must contain both uppercase and lowercase letters"
        
        if not has_number:
            return False, "Password must contain at least one number"
        
        # Optional: require special character
        # if not has_special:
        #     return False, "Password must contain at least one special character"
        
        return True, "Password is valid"
