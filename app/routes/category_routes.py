from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.repositories.category_repository import CategoryRepository
from app.utils.decorators import admin_required
import logging

category_bp = Blueprint('categories', __name__, url_prefix='/api/categories')
logger = logging.getLogger(__name__)

@category_bp.route('', methods=['GET'])
def get_categories():
    """Get all categories."""
    try:
        parent_only = request.args.get('parent_only', 'false').lower() == 'true'
        categories = CategoryRepository.get_all(parent_only=parent_only)
        
        return jsonify({
            'categories': [cat.to_dict(include_children=True, include_products=True) for cat in categories]
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching categories: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch categories'}), 500

@category_bp.route('/<int:category_id>', methods=['GET'])
def get_category(category_id):
    """Get single category by ID."""
    try:
        category = CategoryRepository.get_by_id(category_id)
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        return jsonify(category.to_dict(include_children=True, include_products=True)), 200
    
    except Exception as e:
        logger.error(f"Error fetching category {category_id}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch category'}), 500

@category_bp.route('/slug/<slug>', methods=['GET'])
def get_category_by_slug(slug):
    """Get single category by slug."""
    try:
        category = CategoryRepository.get_by_slug(slug)
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        return jsonify(category.to_dict(include_children=True, include_products=True)), 200
    
    except Exception as e:
        logger.error(f"Error fetching category by slug {slug}: {e}", exc_info=True)
        return jsonify({'error': 'Failed to fetch category'}), 500

@category_bp.route('', methods=['POST'])  # ← CHANGED: No /add, just ''
@jwt_required()
@admin_required
def create_category():
    """
    Create a new category (admin only).
    
    Required fields:
    - name: Category name (unique)
    
    Optional fields:
    - description: Category description
    - parent_id: ID of parent category (for subcategories)
    - is_active: Whether category is active (default: true)
    
    The slug is auto-generated from the name.
    """
    try:
        data = request.get_json(silent=True)
        logger.info(f"Create category request data: {data}")

        if not data:
            logger.warning("No JSON data provided")
            return jsonify({"error": "Invalid JSON"}), 400
        
        # Validate required fields
        required_fields = ['name']
        for field in required_fields:
            if field not in data:
                logger.warning(f"Missing required field: {field}")
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create category
        logger.info(f"Creating category with data: {data}")
        category = CategoryRepository.create(**data)
        logger.info(f"Category created successfully: {category.name} (ID: {category.id})")
        
        return jsonify({
            'message': 'Category created successfully',
            'category': category.to_dict()
        }), 201
    
    except Exception as e:
        logger.error(f"Error creating category: {e}", exc_info=True)
        # Return the actual error message for debugging
        return jsonify({'error': f'Failed to create category: {str(e)}'}), 500

@category_bp.route('/<int:category_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_category(category_id):
    """Update category (admin only)."""
    try:
        category = CategoryRepository.get_by_id(category_id)
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
        logger.info(f"Updating category {category_id} with data: {data}")
        category = CategoryRepository.update(category, **data)
        
        return jsonify({
            'message': 'Category updated successfully',
            'category': category.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Error updating category {category_id}: {e}", exc_info=True)
        return jsonify({'error': f'Failed to update category: {str(e)}'}), 500

@category_bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_category(category_id):
    """Delete category (admin only)."""
    try:
        category = CategoryRepository.get_by_id(category_id)
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        logger.info(f"Deleting category {category_id}: {category.name}")
        CategoryRepository.delete(category)
        
        return jsonify({'message': 'Category deleted successfully'}), 200
    
    except Exception as e:
        logger.error(f"Error deleting category {category_id}: {e}", exc_info=True)
        return jsonify({'error': f'Failed to delete category: {str(e)}'}), 500
