from datetime import datetime, timezone
from app.extensions import db
from app.models.order import Order
from app.models.order_item import OrderItem
from app.enums import OrderStatus


class OrderRepository:
    """Repository for Order and OrderItem model operations."""
    
    @staticmethod
    def get_by_id(order_id):
        """Get order by ID."""
        return Order.query.get(order_id)
    
    @staticmethod
    def get_by_order_number(order_number):
        """Get order by order number."""
        return Order.query.filter_by(order_number=order_number).first()
    
    @staticmethod
    def create(customer_id, order_number, **kwargs):
        """Create a new order."""
        order = Order(customer_id=customer_id, order_number=order_number, **kwargs)
        db.session.add(order)
        db.session.commit()
        return order
    
    @staticmethod
    def update(order, **kwargs):
        """Update order attributes."""
        for key, value in kwargs.items():
            if hasattr(order, key):
                setattr(order, key, value)
        db.session.commit()
        return order
    
    @staticmethod
    def add_item(order, product, quantity):
        """Add item to order."""
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            product_sku=product.sku,
            unit_price=product.price,
            quantity=quantity
        )
        db.session.add(order_item)
        db.session.commit()
        return order_item
    
    @staticmethod
    def update_status(order, status):
        """Update order status with automatic timestamp management."""
        order.status = status
        
        # Set timestamps based on status using enum values
        if status == OrderStatus.CONFIRMED.value and not order.confirmed_at:
            order.confirmed_at = datetime.now(timezone.utc)
        elif status == OrderStatus.SHIPPED.value and not order.shipped_at:
            order.shipped_at = datetime.now(timezone.utc)
        elif status == OrderStatus.DELIVERED.value and not order.delivered_at:
            order.delivered_at = datetime.now(timezone.utc)
        
        db.session.commit()
        return order
    
    @staticmethod
    def update_payment_status(order, payment_status):
        """Update order payment status."""
        order.payment_status = payment_status
        db.session.commit()
        return order
    
    @staticmethod
    def get_by_customer(customer_id, page=1, per_page=20):
        """Get orders by customer with pagination."""
        return Order.query.filter_by(customer_id=customer_id)\
            .order_by(Order.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_all(page=1, per_page=20, status=None):
        """Get all orders with optional status filter."""
        query = Order.query
        
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(Order.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def get_by_date_range(start_date, end_date, page=1, per_page=20, status=None):
        """Get orders within a date range."""
        query = Order.query.filter(
            Order.created_at >= start_date,
            Order.created_at <= end_date
        )
        
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(Order.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def delete(order):
        """Delete an order."""
        db.session.delete(order)
        db.session.commit()