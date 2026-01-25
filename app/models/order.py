from datetime import datetime, timezone
from app.extensions import db
from app.enums import OrderStatus, PaymentStatus, PaymentMethod


class Order(db.Model):
    """Order model."""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    
    # Order status
    # Status options: pending, confirmed, processing, shipped, delivered, cancelled, refunded
    status = db.Column(db.String(20), default=OrderStatus.PENDING.value, nullable=False)
    
    # Pricing
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)
    tax = db.Column(db.Numeric(10, 2), default=0)
    shipping_cost = db.Column(db.Numeric(10, 2), default=0)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Shipping information
    shipping_address_line1 = db.Column(db.String(255), nullable=False)
    shipping_address_line2 = db.Column(db.String(255))
    shipping_city = db.Column(db.String(100), nullable=False)
    shipping_state = db.Column(db.String(100), nullable=False)
    shipping_postal_code = db.Column(db.String(20), nullable=False)
    shipping_country = db.Column(db.String(100), nullable=False)
    
    # Payment information
    payment_method = db.Column(db.String(50))
    # Payment status: pending, paid, failed, refunded
    payment_status = db.Column(db.String(20), default=PaymentStatus.PENDING.value)
    
    # Notes
    customer_notes = db.Column(db.Text)
    admin_notes = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    confirmed_at = db.Column(db.DateTime)
    shipped_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    
    # Relationships
    items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan')
    
    @property
    def total_items(self):
        """Get total number of items in order."""
        return sum(item.quantity for item in self.items)
    
    @property
    def is_pending(self):
        """Check if order is pending."""
        return self.status == OrderStatus.PENDING.value
    
    @property
    def is_confirmed(self):
        """Check if order is confirmed."""
        return self.status == OrderStatus.CONFIRMED.value
    
    @property
    def is_shipped(self):
        """Check if order is shipped."""
        return self.status == OrderStatus.SHIPPED.value
    
    @property
    def is_delivered(self):
        """Check if order is delivered."""
        return self.status == OrderStatus.DELIVERED.value
    
    @property
    def is_cancelled(self):
        """Check if order is cancelled."""
        return self.status == OrderStatus.CANCELLED.value
    
    @property
    def is_active(self):
        """Check if order is active (not cancelled or refunded)."""
        return self.status in OrderStatus.active_statuses()
    
    @property
    def is_paid(self):
        """Check if payment is completed."""
        return self.payment_status == PaymentStatus.PAID.value
    
    def to_dict(self, include_items=True, include_customer=False):
        """Convert order to dictionary."""
        data = {
            'id': self.id,
            'order_number': self.order_number,
            'customer_id': self.customer_id,
            'status': self.status,
            'payment_status': self.payment_status,
            'payment_method': self.payment_method,
            'subtotal': float(self.subtotal),
            'tax': float(self.tax),
            'shipping_cost': float(self.shipping_cost),
            'total': float(self.total),
            'total_items': self.total_items,
            'shipping_address': {
                'line1': self.shipping_address_line1,
                'line2': self.shipping_address_line2,
                'city': self.shipping_city,
                'state': self.shipping_state,
                'postal_code': self.shipping_postal_code,
                'country': self.shipping_country
            },
            'customer_notes': self.customer_notes,
            'admin_notes': self.admin_notes,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'confirmed_at': self.confirmed_at.isoformat() if self.confirmed_at else None,
            'shipped_at': self.shipped_at.isoformat() if self.shipped_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None
        }
        
        if include_items:
            data['items'] = [item.to_dict() for item in self.items]
        
        if include_customer and self.customer:
            data['customer'] = self.customer.to_dict()
        
        return data
    
    def __repr__(self):
        return f'<Order {self.order_number}>'