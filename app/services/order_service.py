import uuid
from decimal import Decimal
from app.repositories.order_repository import OrderRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.customer_repository import CustomerRepository

class OrderService:
    """Service for order operations."""
    
    @staticmethod
    def create_order_from_cart(customer_id, shipping_address, payment_method=None, customer_notes=None):
        """Create order from customer's cart."""
        # Get cart
        cart = CartRepository.get_by_customer_id(customer_id)
        if not cart or not cart.items.count():
            raise ValueError("Cart is empty")
        
        # Validate stock for all items
        for item in cart.items:
            if item.product.stock_quantity < item.quantity:
                raise ValueError(f"Insufficient stock for {item.product.name}")
        
        # Calculate totals
        subtotal = cart.subtotal
        tax = subtotal * Decimal('0.1')  # 10% tax
        shipping_cost = Decimal('10.00')  # Flat rate shipping
        total = subtotal + tax + shipping_cost
        
        # Generate order number
        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        # Create order
        order = OrderRepository.create(
            customer_id=customer_id,
            order_number=order_number,
            subtotal=subtotal,
            tax=tax,
            shipping_cost=shipping_cost,
            total=total,
            shipping_address_line1=shipping_address.get('line1'),
            shipping_address_line2=shipping_address.get('line2'),
            shipping_city=shipping_address.get('city'),
            shipping_state=shipping_address.get('state'),
            shipping_postal_code=shipping_address.get('postal_code'),
            shipping_country=shipping_address.get('country'),
            payment_method=payment_method,
            customer_notes=customer_notes
        )
        
        # Add items to order and update stock
        for cart_item in cart.items:
            OrderRepository.add_item(order, cart_item.product, cart_item.quantity)
            ProductRepository.update_stock(cart_item.product, -cart_item.quantity)
        
        # Clear cart
        CartRepository.clear_cart(cart)
        
        return order
    
    @staticmethod
    def get_order(order_id, customer_id=None):
        """Get order by ID, optionally validate customer."""
        order = OrderRepository.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        
        if customer_id and order.customer_id != customer_id:
            raise ValueError("Unauthorized access to order")
        
        return order
    
    @staticmethod
    def get_customer_orders(customer_id, page=1, per_page=20):
        """Get all orders for a customer."""
        return OrderRepository.get_by_customer(customer_id, page, per_page)
    
    @staticmethod
    def update_order_status(order_id, status):
        """Update order status."""
        valid_statuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded']
        if status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        order = OrderRepository.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        
        # Handle cancellation
        if status == 'cancelled' and order.status not in ['cancelled', 'refunded']:
            # Restore stock
            for item in order.items:
                ProductRepository.update_stock(item.product, item.quantity)
        
        return OrderRepository.update_status(order, status)
    
    @staticmethod
    def update_payment_status(order_id, payment_status):
        """Update order payment status."""
        valid_statuses = ['pending', 'paid', 'failed', 'refunded']
        if payment_status not in valid_statuses:
            raise ValueError(f"Invalid payment status. Must be one of: {', '.join(valid_statuses)}")
        
        order = OrderRepository.get_by_id(order_id)
        if not order:
            raise ValueError("Order not found")
        
        return OrderRepository.update_payment_status(order, payment_status)
    
    @staticmethod
    def get_all_orders(page=1, per_page=20, status=None):
        """Get all orders (admin only)."""
        return OrderRepository.get_all(page, per_page, status)