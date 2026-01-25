from datetime import datetime, timezone
from app.extensions import db

class CartItem(db.Model):
    """Cart item model."""
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('carts.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    
    #Angela note: we store in DB and backend UTC time. The fronend will convert to local time as needed. This will allow concsistency in time.
    #Read document section "Handlig datetime Understanding lambda and the Timestamp Code "
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    product = db.relationship('Product')
    
    # Unique constraint to prevent duplicate products in same cart
    # Example: Can't have product_id=5 appear twice in cart_id=1
    #Angela Note:in seed_data.py, "selected_products = random.sample" was added to prevent adding the same item
    __table_args__ = (
        db.UniqueConstraint('cart_id', 'product_id', name='unique_cart_product'),
    )
    
    @property
    def total_price(self):
        """Calculate total price for this cart item."""
        return self.product.price * self.quantity
    
    def to_dict(self):
        """Convert cart item to dictionary."""
        return {
            'id': self.id,
            'cart_id': self.cart_id,
            'product_id': self.product_id,
            'product': self.product.to_dict() if self.product else None,
            'quantity': self.quantity,
            'unit_price': float(self.product.price),
            'total_price': float(self.total_price),
            'created_at': self.created_at.isoformat(),  # Sends UTC to frontend
            'updated_at': self.updated_at.isoformat()
        }
    
    
    # Converts database object to JSON-friendly dictionary
    # Used when sending data to frontend/API responses
    def __repr__(self):
        return f'<CartItem product_id={self.product_id} quantity={self.quantity}>'