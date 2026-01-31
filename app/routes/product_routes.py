"""Product Routes - Final Clean Version (4 Routes Only)"""
from flask import Blueprint, request, jsonify
from app.services.product_service import ProductService
import logging

logger = logging.getLogger(__name__)

product_bp = Blueprint('products', __name__, url_prefix='/api/products')


@product_bp.route('', methods=['GET'])
def get_products():
    """
    UNIFIED ENDPOINT: Handles all product retrieval and search operations.
    
    Query Parameters:
        - page (int): Page number (default: 1)
        - per_page (int): Items per page (default: 20, max: 100)
        - category_id (int): Filter by category
        - featured (bool): Only featured products
        - search_type (str): Field to search ('id', 'sku', 'slug', 'barcode', 'category_id', 'name')
        - search_value (str/int): Value to search for
        
    Examples:
        GET /api/products                                           # All products
        GET /api/products?page=2&per_page=20                       # Pagination
        GET /api/products?category_id=5                            # By category
        GET /api/products?featured=true                            # Featured only
        GET /api/products?search_type=id&search_value=42           # By ID
        GET /api/products?search_type=sku&search_value=SKU-123     # By SKU
        GET /api/products?search_type=slug&search_value=laptop-hp  # By slug
        GET /api/products?search_type=barcode&search_value=789     # By barcode
        GET /api/products?search_type=name&search_value=laptop     # By name
    """
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Build filters dictionary
        filters = {}
        
        # Category filter
        if request.args.get('category_id'):
            filters['category_id'] = request.args.get('category_id', type=int)
        
        # Featured filter
        if request.args.get('featured'):
            filters['featured'] = request.args.get('featured', type=bool)
        
        # Unified search
        if request.args.get('search_type'):
            filters['search_type'] = request.args.get('search_type', type=str)
            filters['search_value'] = request.args.get('search_value', type=str)
        
        # Get products
        result = ProductService.get_all_products(
            page=page,
            per_page=per_page,
            filters=filters
        )
        
        return jsonify(result), 200
        
    except ValueError as e:
        logger.warning(f"Validation error in get_products: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in get_products: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@product_bp.route('/add', methods=['POST'])
def create_product():
    """Create a new product."""
    try:
        data = request.get_json()
        product = ProductService.create_product(**data)
        return jsonify(product.to_dict(include_category=True)), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating product: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@product_bp.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update a product."""
    try:
        data = request.get_json()
        product = ProductService.update_product(product_id, **data)
        return jsonify(product.to_dict(include_category=True)), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@product_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Soft delete a product."""
    try:
        ProductService.delete_product(product_id)
        return jsonify({'message': 'Product deleted successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500