"""Order routes with proper 4-role permissions."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.order_service import OrderService
from app.repositories.customer_repository import CustomerRepository
from app.utils.decorators import admin_only, manager_required, staff_required
from app.enums import OrderStatus, PaymentStatus, UserRole
from datetime import datetime, timezone, timedelta
import logging

order_bp = Blueprint('orders', __name__, url_prefix='/api/orders')
logger = logging.getLogger(__name__)


def get_customer_id_from_user():
    """Helper to get customer ID from current user."""
    user_id = get_jwt_identity()
    customer = CustomerRepository.get_by_user_id(user_id)
    if not customer:
        raise ValueError("Customer profile not found")
    return customer.id


# ============================================================================
# CUSTOMER ENDPOINTS
# ============================================================================

@order_bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    """
    Create order from cart.
    CUSTOMER - Any authenticated user can create orders.
    """
    try:
        customer_id = get_customer_id_from_user()
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
        # Validate shipping address
        shipping_address = data.get('shipping_address')
        if not shipping_address:
            return jsonify({'error': 'shipping_address is required'}), 400
        
        required_address_fields = ['line1', 'city', 'state', 'postal_code', 'country']
        for field in required_address_fields:
            if field not in shipping_address:
                return jsonify({'error': f'shipping_address.{field} is required'}), 400
        
        order = OrderService.create_order_from_cart(
            customer_id=customer_id,
            shipping_address=shipping_address,
            payment_method=data.get('payment_method'),
            customer_notes=data.get('customer_notes')
        )
        
        return jsonify({
            'message': 'Order created successfully',
            'order': order.to_dict()
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating order: {e}", exc_info=True)
        return jsonify({'error': 'Failed to create order'}), 500


@order_bp.route('', methods=['GET'])
@jwt_required()
def get_customer_orders():
    """
    Get current user's orders.
    CUSTOMER - Users can only see their own orders.
    """
    try:
        customer_id = get_customer_id_from_user()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        pagination = OrderService.get_customer_orders(customer_id, page, per_page)
        
        return jsonify({
            'orders': [order.to_dict(include_items=False) for order in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error fetching orders: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch orders'}), 500


@order_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """
    Get order by ID.
    CUSTOMER - Users can only see their own orders.
    STAFF - Can see any order.
    """
    try:
        from app.utils.decorators import is_staff
        
        if is_staff():
            # Staff can see any order
            order = OrderService.get_order(order_id, customer_id=None)
        else:
            # Customers can only see their own orders
            customer_id = get_customer_id_from_user()
            order = OrderService.get_order(order_id, customer_id)
        
        return jsonify(order.to_dict()), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error fetching order: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch order'}), 500


@order_bp.route('/<int:order_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_order(order_id):
    """
    Cancel own order.
    CUSTOMER - Can cancel their own orders if status allows.
    """
    try:
        customer_id = get_customer_id_from_user()
        order = OrderService.get_order(order_id, customer_id)
        
        # Check if order can be cancelled (using enum values)
        if order.status in [OrderStatus.DELIVERED.value, OrderStatus.CANCELLED.value, OrderStatus.REFUNDED.value]:
            return jsonify({
                'error': f'Cannot cancel order with status: {order.status}',
                'message': 'Please contact customer support for assistance'
            }), 400
        
        order = OrderService.update_order_status(order_id, OrderStatus.CANCELLED.value)
        
        return jsonify({
            'message': 'Order cancelled successfully',
            'order': order.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error cancelling order: {e}", exc_info=True)
        return jsonify({'error': 'Failed to cancel order'}), 500


# ============================================================================
# STAFF ENDPOINTS (Cashier, Manager, Admin)
# ============================================================================

@order_bp.route('/today', methods=['GET'])
@jwt_required()
@staff_required
def get_today_orders():
    """
    Get today's orders.
    STAFF ONLY - Cashiers need this for daily operations.
    """
    try:
        from app.repositories.order_repository import OrderRepository
        
        # Get orders from today
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        pagination = OrderRepository.get_by_date_range(
            start_date=today_start,
            end_date=datetime.now(timezone.utc),
            page=1,
            per_page=100
        )
        
        return jsonify({
            'orders': [order.to_dict(include_customer=True) for order in pagination.items],
            'total': pagination.total,
            'date': today_start.isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching today's orders: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch orders'}), 500


@order_bp.route('/search', methods=['GET'])
@jwt_required()
@staff_required
def search_orders():
    """
    Search orders by order number.
    STAFF ONLY - For quick order lookup at checkout.
    """
    try:
        order_number = request.args.get('number')
        if not order_number:
            return jsonify({'error': 'order number is required'}), 400
        
        from app.repositories.order_repository import OrderRepository
        order = OrderRepository.get_by_order_number(order_number)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        return jsonify(order.to_dict(include_customer=True)), 200
    
    except Exception as e:
        logger.error(f"Error searching order: {e}", exc_info=True)
        return jsonify({'error': 'Failed to search order'}), 500


@order_bp.route('/<int:order_id>/status', methods=['PUT'])
@jwt_required()
@staff_required
def update_order_status(order_id):
    """
    Update order status.
    STAFF - Cashiers can update to: confirmed, processing
    MANAGER - Can update to any status except refunded
    ADMIN - Can update to any status including refunded
    """
    try:
        data = request.get_json(silent=True)
        if not data or not data.get('status'):
            return jsonify({'error': 'status is required'}), 400
        
        status = data['status']
        
        # Validate status is valid
        if not OrderStatus.is_valid(status):
            return jsonify({
                'error': f'Invalid status. Must be one of: {", ".join(OrderStatus.values())}'
            }), 400
        
        # Check permissions based on role
        from app.utils.decorators import get_current_user_role
        role = get_current_user_role()
        
        # Cashiers can only set to: confirmed, processing
        if role == UserRole.CASHIER.value and status not in [OrderStatus.CONFIRMED.value, OrderStatus.PROCESSING.value]:
            return jsonify({
                'error': 'Cashiers can only update status to: confirmed, processing',
                'your_role': role,
                'allowed_statuses': [OrderStatus.CONFIRMED.value, OrderStatus.PROCESSING.value]
            }), 403
        
        # Managers cannot set to: refunded (admin only)
        if role == UserRole.MANAGER.value and status == OrderStatus.REFUNDED.value:
            return jsonify({
                'error': 'Only admins can set status to refunded',
                'message': 'Please contact an administrator for refunds'
            }), 403
        
        order = OrderService.update_order_status(order_id, status)
        
        return jsonify({
            'message': 'Order status updated',
            'order': order.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating order status: {e}", exc_info=True)
        return jsonify({'error': 'Failed to update order status'}), 500


@order_bp.route('/<int:order_id>/payment-status', methods=['PUT'])
@jwt_required()
@staff_required
def update_payment_status(order_id):
    """
    Update payment status.
    STAFF - Cashiers can update payment status: pending, paid, failed.
    """
    try:
        data = request.get_json(silent=True)
        if not data or not data.get('payment_status'):
            return jsonify({'error': 'payment_status is required'}), 400
        
        payment_status = data['payment_status']
        
        # Validate payment status is valid
        if not PaymentStatus.is_valid(payment_status):
            return jsonify({
                'error': f'Invalid payment status. Must be one of: {", ".join(PaymentStatus.values())}'
            }), 400
        
        # Refunded payment status is admin only
        from app.utils.decorators import is_admin
        if payment_status == PaymentStatus.REFUNDED.value and not is_admin():
            return jsonify({
                'error': 'Only admins can set payment status to refunded',
                'message': 'Please contact an administrator for refunds'
            }), 403
        
        order = OrderService.update_payment_status(order_id, payment_status)
        
        return jsonify({
            'message': 'Payment status updated',
            'order': order.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating payment status: {e}", exc_info=True)
        return jsonify({'error': 'Failed to update payment status'}), 500


@order_bp.route('/<int:order_id>/ship', methods=['POST'])
@jwt_required()
@staff_required
def mark_as_shipped(order_id):
    """
    Mark order as shipped.
    STAFF - Any staff member can mark orders as shipped.
    """
    try:
        data = request.get_json(silent=True) or {}
        tracking_number = data.get('tracking_number')
        
        order = OrderService.update_order_status(order_id, OrderStatus.SHIPPED.value)
        
        # Add tracking number if provided
        if tracking_number:
            from app.repositories.order_repository import OrderRepository
            OrderRepository.update(order, tracking_number=tracking_number)
        
        return jsonify({
            'message': 'Order marked as shipped',
            'order': order.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error marking order as shipped: {e}", exc_info=True)
        return jsonify({'error': 'Failed to mark as shipped'}), 500


# ============================================================================
# MANAGER ENDPOINTS (Manager, Admin)
# ============================================================================

@order_bp.route('/admin', methods=['GET'])
@jwt_required()
@manager_required
def get_all_orders():
    """
    Get all orders with filters.
    MANAGER - Can see last 30 days
    ADMIN - Can see all orders (no time limit)
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status')
        
        # Validate status if provided
        if status and not OrderStatus.is_valid(status):
            return jsonify({
                'error': f'Invalid status. Must be one of: {", ".join(OrderStatus.values())}'
            }), 400
        
        # Check role for date restrictions
        from app.utils.decorators import is_admin
        if not is_admin():
            # Managers can only see last 30 days
            days = 30
            from app.repositories.order_repository import OrderRepository
            start_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            pagination = OrderRepository.get_by_date_range(
                start_date=start_date,
                end_date=datetime.now(timezone.utc),
                page=page,
                per_page=per_page,
                status=status
            )
        else:
            # Admins see all orders
            pagination = OrderService.get_all_orders(page, per_page, status)
        
        return jsonify({
            'orders': [order.to_dict(include_customer=True) for order in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching orders: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch orders'}), 500


@order_bp.route('/<int:order_id>/notes', methods=['POST'])
@jwt_required()
@manager_required
def add_order_notes(order_id):
    """
    Add notes to order.
    MANAGER OR ADMIN - For internal tracking.
    """
    try:
        data = request.get_json(silent=True)
        if not data or not data.get('notes'):
            return jsonify({'error': 'notes is required'}), 400
        
        from app.repositories.order_repository import OrderRepository
        order = OrderRepository.get_by_id(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Append to existing notes
        existing_notes = order.admin_notes or ''
        new_notes = f"{existing_notes}\n[{datetime.now(timezone.utc).isoformat()}] {data['notes']}"
        
        OrderRepository.update(order, admin_notes=new_notes.strip())
        
        return jsonify({
            'message': 'Notes added successfully',
            'order': order.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Error adding notes: {e}", exc_info=True)
        return jsonify({'error': 'Failed to add notes'}), 500


# ============================================================================
# ADMIN-ONLY ENDPOINTS
# ============================================================================

@order_bp.route('/<int:order_id>/refund', methods=['POST'])
@jwt_required()
@admin_only
def process_refund(order_id):
    """
    Process refund for order.
    ADMIN ONLY - Only admins can issue refunds.
    """
    try:
        data = request.get_json(silent=True) or {}
        reason = data.get('reason', 'Customer request')
        
        # Update order status to refunded
        order = OrderService.update_order_status(order_id, OrderStatus.REFUNDED.value)
        
        # Update payment status
        OrderService.update_payment_status(order_id, PaymentStatus.REFUNDED.value)
        
        # Add refund notes
        from app.repositories.order_repository import OrderRepository
        notes = f"REFUND PROCESSED: {reason}\nDate: {datetime.now(timezone.utc).isoformat()}"
        OrderRepository.update(order, admin_notes=notes)
        
        return jsonify({
            'message': 'Refund processed successfully',
            'order': order.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error processing refund: {e}", exc_info=True)
        return jsonify({'error': 'Failed to process refund'}), 500


@order_bp.route('/<int:order_id>', methods=['DELETE'])
@jwt_required()
@admin_only
def delete_order(order_id):
    """
    Permanently delete order.
    ADMIN ONLY - Cannot be undone!
    """
    try:
        from app.repositories.order_repository import OrderRepository
        order = OrderRepository.get_by_id(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        OrderRepository.delete(order)
        
        return jsonify({
            'message': 'Order permanently deleted',
            'warning': 'This action cannot be undone'
        }), 200
    
    except Exception as e:
        logger.error(f"Error deleting order: {e}", exc_info=True)
        return jsonify({'error': 'Failed to delete order'}), 500