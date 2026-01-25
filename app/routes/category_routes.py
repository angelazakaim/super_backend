"""Category routes with proper 4-role permissions - FIXED VERSION."""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.services.category_service import CategoryService
from app.utils.decorators import admin_only, manager_required
import logging

category_bp = Blueprint('categories', __name__, url_prefix='/api/categories')
logger = logging.getLogger(__name__)


# ============================================================================
# PUBLIC ENDPOINTS (No Authentication)
# ============================================================================

@category_bp.route('', methods=['GET'])
def get_categories():
    """
    Get all categories.
    PUBLIC - No authentication required.
    """
    try:
        parent_only = request.args.get('parent_only', 'false').lower() == 'true'
        
        
        categories = CategoryService.get_all_categories(parent_only=parent_only)
        
        return jsonify({
            'categories': [cat.to_dict(include_children=True, include_products=True) for cat in categories]
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching categories: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch categories'}), 500


@category_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """
    Get single category by ID.
    PUBLIC - No authentication required.
    """
    try:
        
        category = CategoryService.get_category(category_id)
        return jsonify(category.to_dict(include_children=True, include_products=True)), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error fetching category {category_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch category'}), 500


@category_bp.route('/slug/<slug>', methods=['GET'])
def get_category_by_slug(slug):
    """
    Get single category by slug.
    PUBLIC - No authentication required.
    """
    try:
        
        category = CategoryService.get_category_by_slug(slug)
        return jsonify(category.to_dict(include_children=True, include_products=True)), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error fetching category by slug {slug}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch category'}), 500


# ============================================================================
# MANAGER ENDPOINTS (Manager, Admin)
# ============================================================================

@category_bp.route('/<int:category_id>', methods=['PUT'])
@jwt_required()
@manager_required
def update_category(category_id):
    """
    Update category name/description.
    MANAGER OR ADMIN - Managers can edit existing categories.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
        # Managers can only update name and description
        from app.utils.decorators import is_admin
        if not is_admin():
            # Remove fields only admin can change
            allowed_fields = ['name', 'description']
            data = {k: v for k, v in data.items() if k in allowed_fields}
        
        logger.info(f"Updating category {category_id} with data: {data}")
        
        
        category = CategoryService.update_category(category_id, **data)
        
        return jsonify({
            'message': 'Category updated successfully',
            'category': category.to_dict()
        }), 200
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating category {category_id}: {e}", exc_info=True)
        return jsonify({'error': f'Failed to update category: {str(e)}'}), 500


@category_bp.route('/<int:parent_id>/subcategory', methods=['POST'])
@jwt_required()
@manager_required
def create_subcategory(parent_id):
    """
    Create a subcategory under an existing category.
    MANAGER OR ADMIN - Managers can create subcategories.
    """
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
        # Validate required fields
        if 'name' not in data:
            return jsonify({'error': 'name is required'}), 400
        
        # Force parent_id
        data['parent_id'] = parent_id
        
        logger.info(f"Creating subcategory under {parent_id} with data: {data}")
        
        
        category = CategoryService.create_category(**data)
        
        return jsonify({
            'message': 'Subcategory created successfully',
            'category': category.to_dict()
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating subcategory: {e}", exc_info=True)
        return jsonify({'error': f'Failed to create subcategory: {str(e)}'}), 500


# ============================================================================
# ADMIN-ONLY ENDPOINTS
# ============================================================================

@category_bp.route('', methods=['POST'])
@jwt_required()
@admin_only
def create_category():
    """
    Create a new top-level category.
    ADMIN ONLY - Only admins can create top-level categories.
    """
    try:
        data = request.get_json(silent=True)
        logger.info(f"Create category request data: {data}")

        if not data:
            logger.warning("No JSON data provided")
            return jsonify({"error": "Invalid JSON"}), 400
        
        # Validate required fields
        if 'name' not in data:
            logger.warning("Missing required field: name")
            return jsonify({'error': 'name is required'}), 400
        
        
        category = CategoryService.create_category(**data)
        logger.info(f"Category created successfully: {category.name} (ID: {category.id})")
        
        return jsonify({
            'message': 'Category created successfully',
            'category': category.to_dict()
        }), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating category: {e}", exc_info=True)
        return jsonify({'error': f'Failed to create category: {str(e)}'}), 500


@category_bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_required()
@admin_only
def delete_category(category_id):
    """
    Delete category.
    ADMIN ONLY - Only admins can delete categories.
    Warning: This may affect products in this category!
    """
    try:
        logger.info(f"Deleting category {category_id}")
        
        
        # Service checks for products and children automatically
        CategoryService.delete_category(category_id)
        
        return jsonify({
            'message': 'Category deleted successfully',
            'warning': 'This action cannot be undone'
        }), 200
    
    except ValueError as e:
        # Service returns detailed error message
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error deleting category {category_id}: {e}", exc_info=True)
        return jsonify({'error': f'Failed to delete category: {str(e)}'}), 500


@category_bp.route('/reorder', methods=['PUT'])
@jwt_required()
@admin_only
def reorder_categories():
    """
    Reorder categories (change hierarchy).
    ADMIN ONLY - Only admins can restructure category tree.
    """
    try:
        data = request.get_json()
        updates = data.get('updates', [])
        
        if not updates:
            return jsonify({'error': 'No updates provided'}), 400
        
        # Format: [{'id': 1, 'parent_id': None, 'position': 0}, ...]
        for update in updates:
            category_id = update.get('id')
            parent_id = update.get('parent_id')
            
            if not category_id:
                continue
            
            
            try:
                CategoryService.update_category(category_id, parent_id=parent_id)
            except ValueError as e:
                logger.warning(f"Failed to reorder category {category_id}: {e}")
                continue
        
        return jsonify({'message': 'Categories reordered successfully'}), 200
    
    except Exception as e:
        logger.error(f"Error reordering categories: {e}", exc_info=True)
        return jsonify({'error': 'Failed to reorder categories'}), 500