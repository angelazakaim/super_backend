"""User service with business logic and validation."""
import logging
from typing import Optional, Any, Dict
from app.repositories.user_repository import UserRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.employee_repository import EmployeeRepository
from app.extensions import db
from app.enums import UserRole

logger = logging.getLogger(__name__)


class UserService:
    """Service for user operations with validation and business logic."""
    
    @staticmethod
    def get_user(user_id: int, include_profile: bool = True) -> Dict:
        """
        Get user by ID with optional profile.
        
        Args:
            user_id: User ID
            include_profile: Whether to include customer/employee profile
            
        Returns:
            Dictionary with user and profile data
            
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
                result['profile'] = employee.to_dict(include_salary=True) if employee else None
        
        logger.info(f"Successfully fetched user: {user.username}")
        return result
    
    @staticmethod
    def get_customer_id(user_id: int) -> Optional[int]:
        """
        Get customer ID from user ID.
        
        Args:
            user_id: User ID
            
        Returns:
            Customer ID or None if not found
            
        Raises:
            ValueError: If user is not a customer
        """
        logger.info(f"Getting customer ID for user: {user_id}")
        
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        if user.role != UserRole.CUSTOMER.value:
            raise ValueError(f"User is not a customer (role: {user.role})")
        
        customer = CustomerRepository.get_by_user_id(user_id)
        if not customer:
            raise ValueError("Customer profile not found")
        
        return customer.id
    
    @staticmethod
    def update_profile(user_id: int, profile_data: Dict) -> Dict:
        """
        Update user profile (customer or employee).
        
        Args:
            user_id: User ID
            profile_data: Profile data to update
            
        Returns:
            Updated user data with profile
            
        Raises:
            ValueError: If user not found or invalid data
        """
        logger.info(f"Updating profile for user: {user_id}")
        
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        try:
            if user.role == UserRole.CUSTOMER.value:
                customer = CustomerRepository.get_by_user_id(user_id)
                if not customer:
                    raise ValueError("Customer profile not found")
                
                # Only allow updating certain fields
                allowed_fields = [
                    'first_name', 'last_name', 'phone',
                    'address_line1', 'address_line2', 'city',
                    'state', 'postal_code', 'country'
                ]
                update_data = {k: v for k, v in profile_data.items() if k in allowed_fields}
                
                if update_data:
                    CustomerRepository.update(customer, **update_data)
                    logger.info(f"Updated customer profile for user {user_id}")
                
            elif user.role in [UserRole.MANAGER.value, UserRole.CASHIER.value]:
                employee = EmployeeRepository.get_by_user_id(user_id)
                if not employee:
                    raise ValueError("Employee profile not found")
                
                # Employees can only update basic contact info
                allowed_fields = ['phone', 'address_line1', 'address_line2', 
                                'city', 'state', 'postal_code', 'country']
                update_data = {k: v for k, v in profile_data.items() if k in allowed_fields}
                
                if update_data:
                    EmployeeRepository.update(employee, **update_data)
                    logger.info(f"Updated employee profile for user {user_id}")
            
            # Return updated user data
            return UserService.get_user(user_id, include_profile=True)
            
        except Exception as e:
            logger.error(f"Error updating profile: {e}", exc_info=True)
            raise ValueError(f"Failed to update profile: {str(e)}")
    
    @staticmethod
    def get_all_users(page: int = 1, per_page: int = 20, role_filter: Optional[str] = None) -> Dict:
        """
        Get all users with pagination.
        
        Args:
            page: Page number
            per_page: Items per page (max 100)
            role_filter: Optional role filter (customer, manager, cashier, admin)
            
        Returns:
            Dictionary with users and pagination info
            
        Raises:
            ValueError: If invalid role filter
        """
        logger.info(f"Fetching all users - page: {page}, per_page: {per_page}, role: {role_filter}")
        
        # Validate role filter
        if role_filter and not UserRole.is_valid(role_filter):
            raise ValueError(f"Invalid role filter. Must be one of: {', '.join(UserRole.values())}")
        
        # Limit per_page to prevent abuse
        per_page = min(per_page, 100)
        
        # Get paginated users
        pagination = UserRepository.get_all(page=page, per_page=per_page, active_only=True)
        
        # Filter by role if specified
        users = pagination.items
        if role_filter:
            users = [u for u in users if u.role == role_filter]
        
        return {
            'users': [u.to_dict() for u in users],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    
    @staticmethod
    def get_all_customers(page: int = 1, per_page: int = 20) -> Dict:
        """
        Get all customers with pagination.
        
        Args:
            page: Page number
            per_page: Items per page
            
        Returns:
            Dictionary with customers and pagination info
        """
        logger.info(f"Fetching all customers - page: {page}, per_page: {per_page}")
        
        # Limit per_page
        per_page = min(per_page, 100)
        
        # Get paginated customers
        pagination = CustomerRepository.get_all(page=page, per_page=per_page)
        
        # Get user data for each customer
        customers_with_users = []
        for customer in pagination.items:
            user = UserRepository.get_by_id(customer.user_id)
            if user:
                customer_data = customer.to_dict()
                customer_data['user'] = user.to_dict()
                customers_with_users.append(customer_data)
        
        return {
            'customers': customers_with_users,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    
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
    def update_user(user_id: int, **data) -> Any:
        """
        Update user account data (admin only).
        
        Args:
            user_id: User ID
            **data: Fields to update
            
        Returns:
            Updated user
            
        Raises:
            ValueError: If user not found
        """
        logger.info(f"Updating user {user_id}")
        
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        try:
            user = UserRepository.update(user, **data)
            logger.info(f"User {user_id} updated successfully")
            return user
        except Exception as e:
            logger.error(f"Error updating user: {e}", exc_info=True)
            raise ValueError(f"Failed to update user: {str(e)}")
    
    @staticmethod
    def ban_user(user_id: int) -> Any:
        """
        Ban user (set is_active to False).
        
        Args:
            user_id: User ID
            
        Returns:
            Updated user
        """
        logger.info(f"Banning user {user_id}")
        return UserService.update_user(user_id, is_active=False)
    
    @staticmethod
    def unban_user(user_id: int) -> Any:
        """
        Unban user (set is_active to True).
        
        Args:
            user_id: User ID
            
        Returns:
            Updated user
        """
        logger.info(f"Unbanning user {user_id}")
        return UserService.update_user(user_id, is_active=True)
    
    @staticmethod
    def change_user_role(
        user_id: int,
        new_role: str,
        employee_data: Optional[Dict] = None
    ) -> Dict:
        """
        Change user role (admin only).
        
        Args:
            user_id: User ID
            new_role: New role to assign
            employee_data: Employee data if changing to manager/cashier
            
        Returns:
            Updated user data
            
        Raises:
            ValueError: If validation fails
        """
        logger.info(f"Changing role for user {user_id} to {new_role}")
        
        # Validate role
        if not UserRole.is_valid(new_role):
            raise ValueError(f"Invalid role. Must be one of: {', '.join(UserRole.values())}")
        
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        old_role = user.role
        
        try:
            # Handle role transitions
            if old_role == UserRole.CUSTOMER.value and new_role in [UserRole.MANAGER.value, UserRole.CASHIER.value]:
                # Customer -> Employee: Delete customer profile, create employee profile
                customer = CustomerRepository.get_by_user_id(user_id)
                if customer:
                    CustomerRepository.delete(customer)
                
                if employee_data:
                    EmployeeRepository.create(user_id=user_id, **employee_data)
            
            elif old_role in [UserRole.MANAGER.value, UserRole.CASHIER.value] and new_role == UserRole.CUSTOMER.value:
                # Employee -> Customer: Delete employee profile, create customer profile
                employee = EmployeeRepository.get_by_user_id(user_id)
                if employee:
                    EmployeeRepository.delete(employee)
                
                # Create basic customer profile
                CustomerRepository.create(user_id=user_id)
            
            # Update user role
            user = UserRepository.update(user, role=new_role)
            logger.info(f"Changed user {user_id} role from {old_role} to {new_role}")
            
            return UserService.get_user(user_id, include_profile=True)
            
        except Exception as e:
            logger.error(f"Error changing user role: {e}", exc_info=True)
            db.session.rollback()
            raise ValueError(f"Failed to change user role: {str(e)}")
    
    @staticmethod
    def delete_user(user_id: int) -> None:
        """
        Delete user permanently (admin only).
        
        Args:
            user_id: User ID
            
        Raises:
            ValueError: If user not found
        """
        logger.info(f"Deleting user {user_id}")
        
        user = UserRepository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        try:
            # Delete profile first (cascade should handle this, but explicit is better)
            if user.role == UserRole.CUSTOMER.value:
                customer = CustomerRepository.get_by_user_id(user_id)
                if customer:
                    CustomerRepository.delete(customer)
            elif user.role in [UserRole.MANAGER.value, UserRole.CASHIER.value]:
                employee = EmployeeRepository.get_by_user_id(user_id)
                if employee:
                    EmployeeRepository.delete(employee)
            
            # Delete user
            UserRepository.delete(user)
            logger.info(f"User {user_id} deleted successfully")
            
        except Exception as e:
            logger.error(f"Error deleting user: {e}", exc_info=True)
            db.session.rollback()
            raise ValueError(f"Failed to delete user: {str(e)}")
    
    @staticmethod
    def get_user_statistics() -> Dict:
        """
        Get user statistics (admin only).
        
        Returns:
            Dictionary with user counts by role
        """
        logger.info("Fetching user statistics")
        
        all_users = UserRepository.get_all(page=1, per_page=10000, active_only=False).items
        
        stats = {
            'total_users': len(all_users),
            'active_users': len([u for u in all_users if u.is_active]),
            'inactive_users': len([u for u in all_users if not u.is_active]),
            'by_role': {
                'customers': len([u for u in all_users if u.role == UserRole.CUSTOMER.value]),
                'managers': len([u for u in all_users if u.role == UserRole.MANAGER.value]),
                'cashiers': len([u for u in all_users if u.role == UserRole.CASHIER.value]),
                'admins': len([u for u in all_users if u.role == UserRole.ADMIN.value])
            }
        }
        
        return stats