from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.order_service import OrderService
from app.repositories.customer_repository import CustomerRepository
from app.utils.decorators import admin_required

order_bp = Blueprint('orders', __name__, url_prefix='/api/orders')

def get_customer_id_from_user():
    """Helper to get customer ID from current user."""
    user_id = get_jwt_identity()
    customer = CustomerRepository.get_by_user_id(user_id)
    if not customer:
        raise ValueError("Customer profile not found")
    return customer.id

@order_bp.route('', methods=['POST'])
@jwt_required()
def create_order():
    """Create order from cart."""
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
        return jsonify({'error': 'Failed to create order'}), 500

@order_bp.route('', methods=['GET'])
@jwt_required()
def get_orders():
    """Get current user's orders."""
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
        return jsonify({'error': 'Failed to fetch orders'}), 500

@order_bp.route('/<int:order_id>', methods=['GET'])
@jwt_required()
def get_order(order_id):
    """Get order by ID."""
    try:
        customer_id = get_customer_id_from_user()
        order = OrderService.get_order(order_id, customer_id)
        
        return jsonify(order.to_dict()), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'Failed to fetch order'}), 500

@order_bp.route('/admin', methods=['GET'])
@jwt_required()
@admin_required
def get_all_orders():
    """Get all orders (admin only)."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        status = request.args.get('status')
        
        pagination = OrderService.get_all_orders(page, per_page, status)
        
        return jsonify({
            'orders': [order.to_dict(include_customer=True) for order in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page
        }), 200
    
    except Exception as e:
        return jsonify({'error': 'Failed to fetch orders'}), 500

@order_bp.route('/<int:order_id>/status', methods=['PUT'])
@jwt_required()
@admin_required
def update_order_status(order_id):
    """Update order status (admin only)."""
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
        if not data.get('status'):
            return jsonify({'error': 'status is required'}), 400
        
        order = OrderService.update_order_status(order_id, data['status'])
        
        return jsonify({
            'message': 'Order status updated',
            'order': order.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to update order status'}), 500

@order_bp.route('/<int:order_id>/payment-status', methods=['PUT'])
@jwt_required()
@admin_required
def update_payment_status(order_id):
    """Update payment status (admin only)."""
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
        if not data.get('payment_status'):
            return jsonify({'error': 'payment_status is required'}), 400
        
        order = OrderService.update_payment_status(order_id, data['payment_status'])
        
        return jsonify({
            'message': 'Payment status updated',
            'order': order.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Failed to update payment status'}), 500