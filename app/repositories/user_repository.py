from app.extensions import db
from app.models.user import User
from app.enums import UserRole


class UserRepository:
    """Repository for User model operations."""
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID."""
        return User.query.get(user_id)
    
    @staticmethod
    def get_by_email(email):
        """Get user by email."""
        return User.query.filter_by(email=email).first()
    
    @staticmethod
    def get_by_username(username):
        """Get user by username."""
        return User.query.filter_by(username=username).first()
    
    @staticmethod
    def create(email, username, password, role=UserRole.CUSTOMER.value):
        """Create a new user and commit immediately."""
        user = User(email=email, username=username, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def create_without_commit(email, username, password, role=UserRole.CUSTOMER.value):
        """
        Create a new user WITHOUT committing (for transactional operations).
        Use this when you need to create User + Profile atomically.
        
        Must be followed by db.session.commit() or will be rolled back.
        """
        user = User(email=email, username=username, role=role, is_active=True)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # Generate ID but don't commit yet
        return user
    
    @staticmethod
    def update(user, **kwargs):
        """Update user attributes."""
        for key, value in kwargs.items():
            if hasattr(user, key):
                if key == 'password':
                    user.set_password(value)
                else:
                    setattr(user, key, value)
        db.session.commit()
        return user
    
    @staticmethod
    def delete(user):
        """Delete a user."""
        db.session.delete(user)
        db.session.commit()
    
    @staticmethod
    def get_all(page=1, per_page=20, active_only=True, role_filter=None):
        """Get all users with pagination, optionally filtered by role."""
        query = User.query
        if active_only:
            query = query.filter_by(is_active=True)
        if role_filter:
            query = query.filter_by(role=role_filter)
        return query.order_by(User.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
    
    @staticmethod
    def exists_by_email(email):
        """Check if user exists by email."""
        return db.session.query(User.query.filter_by(email=email).exists()).scalar()
    
    @staticmethod
    def exists_by_username(username):
        """Check if user exists by username."""
        return db.session.query(User.query.filter_by(username=username).exists()).scalar()