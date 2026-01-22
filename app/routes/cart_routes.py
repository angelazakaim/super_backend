"""Cart routes with Marshmallow validation and comprehensive error handling."""
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.services.cart_service import CartService
from app.repositories.customer_repository import CustomerRepository
from app.schemas import AddToCartSchema, UpdateCartItemSchema, validate_with_errors

logger = logging.getLogger(__name__)
cart_bp = Blueprint('cart', __name__, url_prefix='/api/cart')


def get_customer_id_from_user():
    """Helper to get customer ID from current user."""
    try:
        user_id = get_jwt_identity()
        customer = CustomerRepository.get_by_user_id(user_id)
        
        if not customer:
            logger.error(f"Customer profile not found for user: {user_id}")
            raise ValueError("Customer profile not found")
        
        return customer.id
    except Exception as e:
        logger.error(f"Failed to get customer ID: {e}", exc_info=True)
        raise


@cart_bp.route('', methods=['GET'])
@jwt_required()
def get_cart():
    """Get current user's cart."""
    try:
        customer_id = get_customer_id_from_user()
        logger.info(f"Fetching cart for customer: {customer_id}")
        
        cart = CartService.get_cart(customer_id)
        
        if not cart:
            return jsonify({
                'message': 'Cart is empty',
                'cart': None
            }), 200
        
        return jsonify(cart.to_dict()), 200
    
    except ValueError as e:
        logger.warning(f"Error fetching cart: {e}")
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Unexpected error fetching cart: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch cart'}), 500


@cart_bp.route('/items', methods=['POST'])
@jwt_required()
def add_to_cart():
    """Add item to cart."""
    try:
        customer_id = get_customer_id_from_user()
        
        # Validate request data
        is_valid, validated_data = validate_with_errors(
            AddToCartSchema,
            request.get_json()
        )
        
        if not is_valid:
            logger.warning(f"Invalid add to cart data: {validated_data}")
            return jsonify({
                'error': 'Validation failed',
                'details': validated_data
            }), 400
        
        product_id = validated_data['product_id']
        quantity = validated_data.get('quantity', 1)
        
        logger.info(
            f"Adding to cart - customer: {customer_id}, "
            f"product: {product_id}, quantity: {quantity}"
        )
        
        # Add to cart with race condition protection
        cart = CartService.add_to_cart(
            customer_id=customer_id,
            product_id=product_id,
            quantity=quantity,
            use_lock=True
        )
        
        return jsonify({
            'message': 'Item added to cart',
            'cart': cart.to_dict()
        }), 200
    
    except ValueError as e:
        logger.warning(f"Add to cart failed: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error adding to cart: {e}", exc_info=True)
        return jsonify({'error': 'Failed to add item to cart'}), 500


@cart_bp.route('/items/<int:product_id>', methods=['PUT'])
@jwt_required()
def update_cart_item(product_id):
    """Update cart item quantity."""
    try:
        customer_id = get_customer_id_from_user()
        
        # Validate request data
        is_valid, validated_data = validate_with_errors(
            UpdateCartItemSchema,
            request.get_json()
        )
        
        if not is_valid:
            logger.warning(f"Invalid update cart data: {validated_data}")
            return jsonify({
                'error': 'Validation failed',
                'details': validated_data
            }), 400
        
        quantity = validated_data['quantity']
        
        logger.info(
            f"Updating cart item - customer: {customer_id}, "
            f"product: {product_id}, quantity: {quantity}"
        )
        
        # Update cart item with race condition protection
        cart = CartService.update_cart_item(
            customer_id=customer_id,
            product_id=product_id,
            quantity=quantity,
            use_lock=True
        )
        
        return jsonify({
            'message': 'Cart item updated',
            'cart': cart.to_dict()
        }), 200
    
    except ValueError as e:
        logger.warning(f"Update cart item failed: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error updating cart item: {e}", exc_info=True)
        return jsonify({'error': 'Failed to update cart item'}), 500


@cart_bp.route('/items/<int:product_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(product_id):
    """Remove item from cart."""
    try:
        customer_id = get_customer_id_from_user()
        
        logger.info(
            f"Removing from cart - customer: {customer_id}, product: {product_id}"
        )
        
        cart = CartService.remove_from_cart(customer_id, product_id)
        
        return jsonify({
            'message': 'Item removed from cart',
            'cart': cart.to_dict() if cart else None
        }), 200
    
    except ValueError as e:
        logger.warning(f"Remove from cart failed: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error removing from cart: {e}", exc_info=True)
        return jsonify({'error': 'Failed to remove item from cart'}), 500


@cart_bp.route('/clear', methods=['POST'])
@jwt_required()
def clear_cart():
    """Clear all items from cart."""
    try:
        customer_id = get_customer_id_from_user()
        
        logger.info(f"Clearing cart for customer: {customer_id}")
        
        cart = CartService.clear_cart(customer_id)
        
        return jsonify({
            'message': 'Cart cleared',
            'cart': cart.to_dict() if cart else None
        }), 200
    
    except ValueError as e:
        logger.warning(f"Clear cart failed: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error clearing cart: {e}", exc_info=True)
        return jsonify({'error': 'Failed to clear cart'}), 500


@cart_bp.route('/validate', methods=['GET'])
@jwt_required()
def validate_cart():
    """Validate cart is ready for checkout."""
    try:
        customer_id = get_customer_id_from_user()
        
        logger.info(f"Validating cart for customer: {customer_id}")
        
        is_valid, error_message = CartService.validate_cart_for_checkout(customer_id)
        
        if is_valid:
            return jsonify({
                'valid': True,
                'message': 'Cart is valid for checkout'
            }), 200
        else:
            return jsonify({
                'valid': False,
                'message': error_message
            }), 400
    
    except Exception as e:
        logger.error(f"Unexpected error validating cart: {e}", exc_info=True)
        return jsonify({'error': 'Failed to validate cart'}), 500


@cart_bp.errorhandler(ValidationError)
def handle_validation_error(error):
    """Handle Marshmallow validation errors."""
    logger.warning(f"Validation error: {error.messages}")
    return jsonify({
        'error': 'Validation failed',
        'details': error.messages
    }), 400


@cart_bp.errorhandler(404)
def handle_not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Resource not found'}), 404


@cart_bp.errorhandler(500)
def handle_server_error(error):
    """Handle 500 errors."""
    logger.error(f"Server error: {error}", exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500