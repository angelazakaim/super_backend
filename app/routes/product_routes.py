"""Product routes with proper 4-role permissions."""
import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.services.product_service import ProductService
from app.schemas import (
    ProductCreateSchema,
    ProductUpdateSchema,
    ProductSearchSchema,
    validate_with_errors
)
from app.utils.decorators import admin_only, manager_required, staff_required

logger = logging.getLogger(__name__)
product_bp = Blueprint('products', __name__, url_prefix='/api/products')


# ============================================================================
# PUBLIC ENDPOINTS (No Authentication)
# ============================================================================

@product_bp.route('', methods=['GET'])
def get_products():
    """
    Get all products with optional filters.
    PUBLIC - No authentication required.
    """
    try:
        is_valid, validated_data = validate_with_errors(
            ProductSearchSchema,
            request.args.to_dict()
        )
        
        if not is_valid:
            return jsonify({'error': 'Invalid parameters', 'details': validated_data}), 400
        
        page = validated_data.get('page', 1)
        per_page = validated_data.get('per_page', 20)
        result = ProductService.get_all_products(page, per_page, validated_data)
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error fetching products: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch products'}), 500


@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """
    Get single product by ID.
    PUBLIC - No authentication required.
    """
    try:
        product = ProductService.get_product(product_id)
        return jsonify(product.to_dict(include_category=True)), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error fetching product: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch product'}), 500


@product_bp.route('/slug/<slug>', methods=['GET'])
def get_product_by_slug(slug):
    """
    Get single product by slug.
    PUBLIC - No authentication required.
    """
    try:
        product = ProductService.get_product_by_slug(slug)
        return jsonify(product.to_dict(include_category=True)), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error fetching product: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch product'}), 500


# ============================================================================
# STAFF ENDPOINTS (Cashier, Manager, Admin)
# ============================================================================

@product_bp.route('/search', methods=['GET'])
@jwt_required()
@staff_required
def search_products():
    """
    Search products by SKU or barcode.
    STAFF ONLY - Cashier, Manager, Admin can access.
    """
    try:
        sku = request.args.get('sku')
        barcode = request.args.get('barcode')
        
        if sku:
            from app.repositories.product_repository import ProductRepository
            product = ProductRepository.get_by_sku(sku)
        elif barcode:
            from app.repositories.product_repository import ProductRepository
            product = ProductRepository.get_by_barcode(barcode)
        else:
            return jsonify({'error': 'SKU or barcode required'}), 400
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        return jsonify(product.to_dict(include_category=True)), 200
    
    except Exception as e:
        logger.error(f"Error searching product: {e}", exc_info=True)
        return jsonify({'error': 'Failed to search product'}), 500


@product_bp.route('/<int:product_id>/stock', methods=['GET'])
@jwt_required()
@staff_required
def check_stock(product_id):
    """
    Check product stock availability.
    STAFF ONLY - Cashier, Manager, Admin can access.
    """
    try:
        available, stock = ProductService.check_stock_availability(product_id, 1)
        
        return jsonify({
            'product_id': product_id,
            'stock_quantity': stock,
            'available': available
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error checking stock: {e}", exc_info=True)
        return jsonify({'error': 'Failed to check stock'}), 500


# ============================================================================
# MANAGER ENDPOINTS (Manager, Admin)
# ============================================================================

@product_bp.route('', methods=['POST'])
@jwt_required()
@manager_required
def create_product():
    """
    Create a new product.
    MANAGER OR ADMIN - Managers can create products.
    """
    try:
        is_valid, validated_data = validate_with_errors(
            ProductCreateSchema,
            request.get_json()
        )
        
        if not is_valid:
            return jsonify({'error': 'Validation failed', 'details': validated_data}), 400
        
        product = ProductService.create_product(**validated_data)
        
        return jsonify({
            'message': 'Product created successfully',
            'product': product.to_dict()
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating product: {e}", exc_info=True)
        return jsonify({'error': 'Failed to create product'}), 500


@product_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
@manager_required
def update_product(product_id):
    """
    Update product (except price).
    MANAGER OR ADMIN - Managers can update products but not prices.
    """
    try:
        is_valid, validated_data = validate_with_errors(
            ProductUpdateSchema,
            request.get_json()
        )
        
        if not is_valid:
            return jsonify({'error': 'Validation failed', 'details': validated_data}), 400
        
        # Check if trying to update price (admin only)
        from app.utils.decorators import is_admin
        if 'price' in validated_data and not is_admin():
            return jsonify({
                'error': 'Only admins can change product prices',
                'message': 'Please contact an administrator to change prices'
            }), 403
        
        product = ProductService.update_product(product_id, **validated_data)
        
        return jsonify({
            'message': 'Product updated successfully',
            'product': product.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating product: {e}", exc_info=True)
        return jsonify({'error': 'Failed to update product'}), 500


@product_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
@manager_required
def delete_product(product_id):
    """
    Soft delete product (set is_active=False).
    MANAGER OR ADMIN - Managers can soft delete (can be restored).
    """
    try:
        ProductService.delete_product(product_id)
        
        return jsonify({
            'message': 'Product deleted successfully',
            'note': 'This is a soft delete. Product can be restored by an administrator.'
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error deleting product: {e}", exc_info=True)
        return jsonify({'error': 'Failed to delete product'}), 500


@product_bp.route('/<int:product_id>/stock', methods=['PUT'])
@jwt_required()
@manager_required
def update_stock(product_id):
    """
    Update product stock.
    MANAGER OR ADMIN - Managers can update inventory.
    """
    try:
        data = request.get_json(silent=True)
        if not data or 'quantity_change' not in data:
            return jsonify({'error': 'quantity_change is required'}), 400
        
        quantity_change = int(data['quantity_change'])
        operation = data.get('operation', 'add')  # add, subtract, set
        
        product = ProductService.update_stock(product_id, quantity_change, operation)
        
        return jsonify({
            'message': 'Stock updated successfully',
            'product': product.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating stock: {e}", exc_info=True)
        return jsonify({'error': 'Failed to update stock'}), 500


@product_bp.route('/low-stock', methods=['GET'])
@jwt_required()
@manager_required
def get_low_stock_products():
    """
    Get products with low stock (inventory alerts).
    MANAGER OR ADMIN - Managers need this for inventory management.
    """
    try:
        threshold = request.args.get('threshold', 10, type=int)
        products = ProductService.get_low_stock_products(threshold)
        
        return jsonify({
            'products': products,
            'count': len(products),
            'threshold': threshold
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching low stock products: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch low stock products'}), 500


@product_bp.route('/bulk-stock', methods=['PUT'])
@jwt_required()
@manager_required
def bulk_update_stock():
    """
    Bulk update stock for multiple products.
    MANAGER OR ADMIN - For inventory management.
    """
    try:
        data = request.get_json()
        updates = data.get('updates', [])
        
        if not updates:
            return jsonify({'error': 'No updates provided'}), 400
        
        results = {
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        for update in updates:
            try:
                product_id = update.get('product_id')
                quantity = update.get('quantity')
                
                if not product_id or quantity is None:
                    results['failed'] += 1
                    results['errors'].append(f"Product {product_id}: Missing data")
                    continue
                
                ProductService.update_stock(product_id, quantity, 'set')
                results['success'] += 1
                
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Product {product_id}: {str(e)}")
        
        return jsonify(results), 200
    
    except Exception as e:
        logger.error(f"Error bulk updating stock: {e}", exc_info=True)
        return jsonify({'error': 'Failed to bulk update stock'}), 500


# ============================================================================
# ADMIN-ONLY ENDPOINTS
# ============================================================================

@product_bp.route('/<int:product_id>/price', methods=['PUT'])
@jwt_required()
@admin_only
def update_price(product_id):
    """
    Update product price.
    ADMIN ONLY - Only admins can change prices.
    """
    try:
        data = request.get_json(silent=True)
        if not data or 'price' not in data:
            return jsonify({'error': 'price is required'}), 400
        
        price = float(data['price'])
        if price <= 0:
            return jsonify({'error': 'Price must be greater than 0'}), 400
        
        product = ProductService.update_product(product_id, price=price)
        
        return jsonify({
            'message': 'Price updated successfully',
            'product': product.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating price: {e}", exc_info=True)
        return jsonify({'error': 'Failed to update price'}), 500


@product_bp.route('/bulk-price', methods=['PUT'])
@jwt_required()
@admin_only
def bulk_update_prices():
    """
    Bulk update prices for multiple products.
    ADMIN ONLY - Only admins can change prices.
    """
    try:
        data = request.get_json()
        updates = data.get('updates', [])
        
        if not updates:
            return jsonify({'error': 'No updates provided'}), 400
        
        results = ProductService.bulk_update_prices(updates)
        return jsonify(results), 200
    
    except Exception as e:
        logger.error(f"Error bulk updating prices: {e}", exc_info=True)
        return jsonify({'error': 'Failed to bulk update prices'}), 500


@product_bp.route('/<int:product_id>/permanent', methods=['DELETE'])
@jwt_required()
@admin_only
def permanently_delete_product(product_id):
    """
    Permanently delete product from database.
    ADMIN ONLY - Cannot be undone!
    """
    try:
        from app.repositories.product_repository import ProductRepository
        product = ProductRepository.get_by_id(product_id)
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        # Hard delete
        ProductRepository.delete(product)
        
        return jsonify({
            'message': 'Product permanently deleted',
            'warning': 'This action cannot be undone'
        }), 200
    
    except Exception as e:
        logger.error(f"Error permanently deleting product: {e}", exc_info=True)
        return jsonify({'error': 'Failed to delete product'}), 500


@product_bp.route('/<int:product_id>/restore', methods=['POST'])
@jwt_required()
@manager_required
def restore_product(product_id):
    """
    Restore soft-deleted product.
    MANAGER OR ADMIN - Can restore previously deleted products.
    """
    try:
        product = ProductService.update_product(product_id, is_active=True)
        
        return jsonify({
            'message': 'Product restored successfully',
            'product': product.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error restoring product: {e}", exc_info=True)
        return jsonify({'error': 'Failed to restore product'}), 500


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@product_bp.errorhandler(ValidationError)
def handle_validation_error(error):
    """Handle Marshmallow validation errors."""
    return jsonify({'error': 'Validation failed', 'details': error.messages}), 400


@product_bp.errorhandler(404)
def handle_not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Resource not found'}), 404


@product_bp.errorhandler(500)
def handle_server_error(error):
    """Handle 500 errors."""
    logger.error(f"Server error: {error}", exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500