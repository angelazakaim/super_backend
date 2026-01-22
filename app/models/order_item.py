from datetime import datetime
from app.extensions import db


class OrderItem(db.Model):
    """Order item model."""
    __tablename__ = 'order_items'
    
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # Product snapshot at time of order
    product_name = db.Column(db.String(200), nullable=False)
    product_sku = db.Column(db.String(100))
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    product = db.relationship('Product')
    
    @property
    def total_price(self):
        """Calculate total price for this order item."""
        return self.unit_price * self.quantity
    
    def to_dict(self):
        """Convert order item to dictionary."""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'product_sku': self.product_sku,
            'unit_price': float(self.unit_price),
            'quantity': self.quantity,
            'total_price': float(self.total_price),
            'created_at': self.created_at.isoformat()
        }
    
    def __repr__(self):
        return f'<OrderItem {self.product_name} x{self.quantity}>'