"""Product routes with Marshmallow validation and comprehensive error handling."""
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
from app.utils.decorators import admin_required

logger = logging.getLogger(__name__)
product_bp = Blueprint('products', __name__, url_prefix='/api/products')


@product_bp.route('', methods=['GET'])
def get_products():
    """Get all products with optional filters."""
    try:
        # Validate query parameters
        is_valid, validated_data = validate_with_errors(
            ProductSearchSchema,
            request.args.to_dict()
        )
        
        if not is_valid:
            logger.warning(f"Invalid search parameters: {validated_data}")
            return jsonify({'error': 'Invalid parameters', 'details': validated_data}), 400
        
        # Extract parameters
        page = validated_data.get('page', 1)
        per_page = validated_data.get('per_page', 20)
        search = validated_data.get('search')
        category_id = validated_data.get('category_id')
        featured = validated_data.get('featured', False)
        
        # Get products
        if search:
            logger.info(f"Searching products: '{search}'")
            pagination = ProductService.search_products(
                query=search,
                page=page,
                per_page=per_page,
                category_id=category_id
            )
        elif featured:
            logger.info("Fetching featured products")
            pagination = ProductService.get_featured_products(page, per_page)
        else:
            logger.info(f"Fetching products (category={category_id})")
            from app.repositories.product_repository import ProductRepository
            pagination = ProductRepository.get_all(
                page=page,
                per_page=per_page,
                category_id=category_id
            )
        
        return jsonify({
            'products': [p.to_dict(include_category=True) for p in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page
        }), 200
    
    except ValueError as e:
        logger.warning(f"Business logic error: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error fetching products: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch products'}), 500


@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get single product by ID."""
    try:
        logger.info(f"Fetching product: {product_id}")
        product = ProductService.get_product(product_id)
        
        return jsonify(product.to_dict(include_category=True)), 200
    
    except ValueError as e:
        logger.warning(f"Product not found or invalid: {e}")
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Unexpected error fetching product: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch product'}), 500


@product_bp.route('/slug/<slug>', methods=['GET'])
def get_product_by_slug(slug):
    """Get single product by slug."""
    try:
        logger.info(f"Fetching product by slug: {slug}")
        from app.repositories.product_repository import ProductRepository
        product = ProductRepository.get_by_slug(slug)
        
        if not product:
            logger.warning(f"Product not found with slug: {slug}")
            return jsonify({'error': 'Product not found'}), 404
        
        return jsonify(product.to_dict(include_category=True)), 200
    
    except Exception as e:
        logger.error(f"Unexpected error fetching product: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch product'}), 500


@product_bp.route('', methods=['POST'])
@jwt_required()
@admin_required
def create_product():
    """Create a new product (admin only)."""
    try:
        # Validate request data
        is_valid, validated_data = validate_with_errors(
            ProductCreateSchema,
            request.get_json()
        )
        
        if not is_valid:
            logger.warning(f"Invalid product data: {validated_data}")
            return jsonify({'error': 'Validation failed', 'details': validated_data}), 400
        
        logger.info(f"Creating product: {validated_data.get('name')}")
        
        # Create product
        product = ProductService.create_product(**validated_data)
        
        return jsonify({
            'message': 'Product created successfully',
            'product': product.to_dict()
        }), 201
    
    except ValueError as e:
        logger.warning(f"Product creation failed: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error creating product: {e}", exc_info=True)
        return jsonify({'error': 'Failed to create product'}), 500


@product_bp.route('/<int:product_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_product(product_id):
    """Update product (admin only)."""
    try:
        # Validate request data
        is_valid, validated_data = validate_with_errors(
            ProductUpdateSchema,
            request.get_json()
        )
        
        if not is_valid:
            logger.warning(f"Invalid product update data: {validated_data}")
            return jsonify({'error': 'Validation failed', 'details': validated_data}), 400
        
        logger.info(f"Updating product: {product_id}")
        
        # Update product
        product = ProductService.update_product(product_id, **validated_data)
        
        return jsonify({
            'message': 'Product updated successfully',
            'product': product.to_dict()
        }), 200
    
    except ValueError as e:
        logger.warning(f"Product update failed: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error updating product: {e}", exc_info=True)
        return jsonify({'error': 'Failed to update product'}), 500


@product_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_product(product_id):
    """Delete product (admin only) - soft delete."""
    try:
        logger.info(f"Deleting product: {product_id}")
        
        ProductService.delete_product(product_id)
        
        return jsonify({'message': 'Product deleted successfully'}), 200
    
    except ValueError as e:
        logger.warning(f"Product deletion failed: {e}")
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Unexpected error deleting product: {e}", exc_info=True)
        return jsonify({'error': 'Failed to delete product'}), 500


@product_bp.route('/<int:product_id>/stock', methods=['PUT'])
@jwt_required()
@admin_required
def update_stock(product_id):
    """Update product stock (admin only)."""
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
        # Validate quantity_change
        quantity_change = data.get('quantity_change')
        if quantity_change is None:
            return jsonify({'error': 'quantity_change is required'}), 400
        
        try:
            quantity_change = int(quantity_change)
        except (ValueError, TypeError):
            return jsonify({'error': 'quantity_change must be an integer'}), 400
        
        logger.info(f"Updating stock for product {product_id}: {quantity_change:+d}")
        
        # Update stock with race condition protection
        product = ProductService.update_stock(product_id, quantity_change)
        
        return jsonify({
            'message': 'Stock updated successfully',
            'product': product.to_dict()
        }), 200
    
    except ValueError as e:
        logger.warning(f"Stock update failed: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Unexpected error updating stock: {e}", exc_info=True)
        return jsonify({'error': 'Failed to update stock'}), 500


@product_bp.route('/low-stock', methods=['GET'])
@jwt_required()
@admin_required
def get_low_stock_products():
    """Get products with low stock (admin only)."""
    try:
        threshold = request.args.get('threshold', 10, type=int)
        
        logger.info(f"Fetching low stock products (threshold: {threshold})")
        
        products = ProductService.get_low_stock_products(threshold)
        
        return jsonify({
            'products': [p.to_dict() for p in products],
            'count': len(products),
            'threshold': threshold
        }), 200
    
    except Exception as e:
        logger.error(f"Unexpected error fetching low stock products: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch low stock products'}), 500


@product_bp.errorhandler(ValidationError)
def handle_validation_error(error):
    """Handle Marshmallow validation errors."""
    logger.warning(f"Validation error: {error.messages}")
    return jsonify({
        'error': 'Validation failed',
        'details': error.messages
    }), 400


@product_bp.errorhandler(404)
def handle_not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Resource not found'}), 404


@product_bp.errorhandler(500)
def handle_server_error(error):
    """Handle 500 errors."""
    logger.error(f"Server error: {error}", exc_info=True)
    return jsonify({'error': 'Internal server error'}), 500