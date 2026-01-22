from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class User(db.Model):
    """User model for authentication and authorization."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    # Roles: 'admin', 'customer', 'manager', 'cashier'
    role = db.Column(db.String(20), default='customer', nullable=False)  
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
        
    # Relationships for different roles One-to-One Relationship Extension
    #Example: the Customer model extends the User model using a pattern called One-to-One Relationship Extension. 
    #Instead of traditional Python class inheritance, this uses database relationships to link a generic
    # "User" account to a specific "Customer" profile.
    # Here is how the extension works in your code:
    # 1. The Foreign Key Link
    # In customer.py, the Customer table contains a user_id column.
    # This column is defined as a ForeignKey('users.id'), which creates a direct link back to the id of the User table. 
    # The unique=True constraint ensures that one User can only ever have one Customer profile, effectively extending that specific user's data.
    # Creating a user and extending it with a profile
    # new_user = User(username="jdoe", email="john@example.com")
    # new_user.set_password("secure_pass")
    # # The extension:
    # profile = Customer(user=new_user, first_name="John", last_name="Doe")
    # db.session.add(new_user)
    # db.session.commit()

    customer = db.relationship('Customer', backref='user', uselist=False, cascade='all, delete-orphan')
    employee = db.relationship('Employee', backref='user', uselist=False, cascade='all, delete-orphan')
   
   
   
   
      
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary."""
        data = {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        return data
    
    def __repr__(self):
        return f'<User {self.username}>'