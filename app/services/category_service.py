"""Category service with business logic and validation."""
from app.repositories.category_repository import CategoryRepository
import logging

logger = logging.getLogger(__name__)


class CategoryService:
    """Service layer for category business logic."""
    
    @staticmethod
    def get_category(category_id):
        """
        Get category by ID.
        
        Args:
            category_id: Category ID
            
        Returns:
            Category object
            
        Raises:
            ValueError: If category not found or inactive
        """
        category = CategoryRepository.get_by_id(category_id)
        if not category:
            raise ValueError("Category not found")
        return category
    
    @staticmethod
    def get_category_by_slug(slug):
        """
        Get category by slug.
        
        Args:
            slug: Category slug
            
        Returns:
            Category object
            
        Raises:
            ValueError: If category not found
        """
        category = CategoryRepository.get_by_slug(slug)
        if not category:
            raise ValueError("Category not found")
        return category
    
    @staticmethod
    def get_all_categories(parent_only=False):
        """
        Get all categories.
        
        Args:
            parent_only: If True, return only root categories
            
        Returns:
            List of categories
        """
        return CategoryRepository.get_all(active_only=True, parent_only=parent_only)
    
    @staticmethod
    def create_category(**data):
        """
        Create a new category with validation.
        
        Args:
            **data: Category data
            
        Returns:
            Created category
            
        Raises:
            ValueError: If validation fails
        """
        # Validate required fields
        if 'name' not in data or not data['name']:
            raise ValueError("Category name is required")
        
        # Validate parent exists if parent_id provided
        if data.get('parent_id'):
            parent = CategoryRepository.get_by_id(data['parent_id'])
            if not parent:
                raise ValueError("Parent category not found")
            if not parent.is_active:
                raise ValueError("Parent category is not active")
        
        try:
            category = CategoryRepository.create(**data)
            logger.info(f"Category created: {category.name} (ID: {category.id})")
            return category
        except Exception as e:
            logger.error(f"Error creating category: {e}", exc_info=True)
            raise ValueError(f"Failed to create category: {str(e)}")
    
    @staticmethod
    def update_category(category_id, **data):
        """
        Update category with validation.
        
        Args:
            category_id: Category ID
            **data: Fields to update
            
        Returns:
            Updated category
            
        Raises:
            ValueError: If validation fails
        """
        category = CategoryRepository.get_by_id(category_id)
        if not category:
            raise ValueError("Category not found")
        
        # Validate parent if changing
        if 'parent_id' in data and data['parent_id']:
            # Can't set parent to self
            if data['parent_id'] == category_id:
                raise ValueError("Category cannot be its own parent")
            
            parent = CategoryRepository.get_by_id(data['parent_id'])
            if not parent:
                raise ValueError("Parent category not found")
            if not parent.is_active:
                raise ValueError("Parent category is not active")
        
        try:
            category = CategoryRepository.update(category, **data)
            logger.info(f"Category updated: {category.name} (ID: {category.id})")
            return category
        except Exception as e:
            logger.error(f"Error updating category: {e}", exc_info=True)
            raise ValueError(f"Failed to update category: {str(e)}")
    
    @staticmethod
    def delete_category(category_id):
        """
        Delete category with validation.
        
        Args:
            category_id: Category ID
            
        Raises:
            ValueError: If category has products or children
        """
        category = CategoryRepository.get_by_id(category_id)
        if not category:
            raise ValueError("Category not found")
        
        # Check for products
        if category.products.count() > 0:
            raise ValueError(
                f"Cannot delete category with {category.products.count()} products. "
                "Please move or delete them first."
            )
        
        # Check for children
        if category.children:
            raise ValueError(
                f"Cannot delete category with {len(category.children)} subcategories. "
                "Please delete them first."
            )
        
        try:
            CategoryRepository.delete(category)
            logger.info(f"Category deleted: {category.name} (ID: {category_id})")
        except Exception as e:
            logger.error(f"Error deleting category: {e}", exc_info=True)
            raise ValueError(f"Failed to delete category: {str(e)}")
    
    @staticmethod
    def get_children(category_id):
        """
        Get child categories.
        
        Args:
            category_id: Parent category ID
            
        Returns:
            List of child categories
        """
        category = CategoryRepository.get_by_id(category_id)
        if not category:
            raise ValueError("Category not found")
        
        return CategoryRepository.get_children(category_id)
