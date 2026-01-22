from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.repositories.category_repository import CategoryRepository
from app.utils.decorators import admin_required

category_bp = Blueprint('categories', __name__, url_prefix='/api/categories')

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
        return jsonify({'error': 'Failed to fetch category'}), 500

@category_bp.route('/add', methods=['POST'])
@jwt_required()
@admin_required  # ← FIXED: Removed parentheses
def create_category():
    """Create a new category (admin only)."""
    try:
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
        required_fields = ['name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        category = CategoryRepository.create(**data)
        
        return jsonify({
            'message': 'Category created successfully',
            'category': category.to_dict()
        }), 201
    
    except Exception as e:
        return jsonify({'error': 'Failed to create category'}), 500

@category_bp.route('/<int:category_id>', methods=['PUT'])
@jwt_required()
@admin_required  # ← FIXED: Removed parentheses
def update_category(category_id):
    """Update category (admin only)."""
    try:
        category = CategoryRepository.get_by_id(category_id)
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        data = request.get_json(silent=True)

        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
        
        category = CategoryRepository.update(category, **data)
        
        return jsonify({
            'message': 'Category updated successfully',
            'category': category.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': 'Failed to update category'}), 500

@category_bp.route('/<int:category_id>', methods=['DELETE'])
@jwt_required()
@admin_required  # ← FIXED: Removed parentheses
def delete_category(category_id):
    """Delete category (admin only)."""
    try:
        category = CategoryRepository.get_by_id(category_id)
        if not category:
            return jsonify({'error': 'Category not found'}), 404
        
        CategoryRepository.delete(category)
        
        return jsonify({'message': 'Category deleted successfully'}), 200
    
    except Exception as e:
        return jsonify({'error': 'Failed to delete category'}), 500