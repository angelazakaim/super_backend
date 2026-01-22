from datetime import datetime
from app.extensions import db

class Cart(db.Model):
    """Shopping cart model."""
    __tablename__ = 'carts'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    items = db.relationship('CartItem', backref='cart', cascade='all, delete-orphan', lazy='dynamic')
    
    @property
    def total_items(self):
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items)
    
    @property
    def subtotal(self):
        """Calculate cart subtotal."""
        return sum(item.total_price for item in self.items)
    
    def to_dict(self, include_items=True):
        """Convert cart to dictionary."""
        data = {
            'id': self.id,
            'customer_id': self.customer_id,
            'total_items': self.total_items,
            'subtotal': float(self.subtotal),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_items:
            data['items'] = [item.to_dict() for item in self.items]
        
        return data
    
    def __repr__(self):
        return f'<Cart customer_id={self.customer_id}>'

