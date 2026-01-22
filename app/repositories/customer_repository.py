from app.extensions import db
from app.models.customer import Customer

class CustomerRepository:
    """Repository for Customer model operations."""
    
    @staticmethod
    def get_by_id(customer_id):
        """Get customer by ID."""
        return Customer.query.get(customer_id)
    
    @staticmethod
    def get_by_user_id(user_id):
        """Get customer by user ID."""
        return Customer.query.filter_by(user_id=user_id).first()
    
    @staticmethod
    def create(user_id, **kwargs):
        """Create a new customer profile."""
        customer = Customer(user_id=user_id, **kwargs)
        db.session.add(customer)
        db.session.commit()
        return customer
    
    @staticmethod
    def update(customer, **kwargs):
        """Update customer attributes."""
        for key, value in kwargs.items():
            if hasattr(customer, key):
                setattr(customer, key, value)
        db.session.commit()
        return customer
    
    @staticmethod
    def delete(customer):
        """Delete a customer."""
        db.session.delete(customer)
        db.session.commit()
    
    @staticmethod
    def get_all(page=1, per_page=20):
        """Get all customers with pagination."""
        return Customer.query.order_by(Customer.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)