from app.extensions import db
from app.models.cart import Cart
from app.models.cart_item import CartItem

class CartRepository:
    """Repository for Cart and CartItem model operations."""
    
    @staticmethod
    def get_by_customer_id(customer_id):
        """Get cart by customer ID."""
        return Cart.query.filter_by(customer_id=customer_id).first()
    
    @staticmethod
    def create(customer_id):
        """Create a new cart."""
        cart = Cart(customer_id=customer_id)
        db.session.add(cart)
        db.session.commit()
        return cart
    
    @staticmethod
    def get_or_create(customer_id):
        """Get existing cart or create new one."""
        cart = CartRepository.get_by_customer_id(customer_id)
        if not cart:
            cart = CartRepository.create(customer_id)
        return cart
    
    @staticmethod
    def add_item(cart, product_id, quantity=1):
        """Add item to cart or update quantity if exists."""
        cart_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product_id).first()
        
        if cart_item:
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
            db.session.add(cart_item)
        
        db.session.commit()
        return cart_item
    
    @staticmethod
    def update_item_quantity(cart_item, quantity):
        """Update cart item quantity."""
        cart_item.quantity = quantity
        db.session.commit()
        return cart_item
    
    @staticmethod
    def remove_item(cart_item):
        """Remove item from cart."""
        db.session.delete(cart_item)
        db.session.commit()
    
    @staticmethod
    def get_cart_item(cart_id, product_id):
        """Get specific cart item."""
        return CartItem.query.filter_by(cart_id=cart_id, product_id=product_id).first()
    
    @staticmethod
    def clear_cart(cart):
        """Remove all items from cart."""
        CartItem.query.filter_by(cart_id=cart.id).delete()
        db.session.commit()
    
    @staticmethod
    def delete_cart(cart):
        """Delete entire cart."""
        db.session.delete(cart)
        db.session.commit()