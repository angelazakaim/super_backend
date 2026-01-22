from app.extensions import db
from app.models.category import Category

class CategoryRepository:
    """Repository for Category model operations."""
    
    @staticmethod
    def get_by_id(category_id):
        """Get category by ID."""
        return Category.query.get(category_id)
    
    @staticmethod
    def get_by_slug(slug):
        """Get category by slug."""
        return Category.query.filter_by(slug=slug, is_active=True).first()
    
    @staticmethod
    def create(**kwargs):
        """Create a new category."""
        category = Category(**kwargs)
        db.session.add(category)
        db.session.commit()
        return category
    
    @staticmethod
    def update(category, **kwargs):
        """Update category attributes."""
        for key, value in kwargs.items():
            if hasattr(category, key):
                setattr(category, key, value)
        db.session.commit()
        return category
    
    @staticmethod
    def delete(category):
        """Delete a category."""
        db.session.delete(category)
        db.session.commit()
    
    @staticmethod
    def get_all(active_only=True, parent_only=False):
        """Get all categories."""
        query = Category.query
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        if parent_only:
            query = query.filter_by(parent_id=None)
        
        return query.order_by(Category.name).all()
    
    @staticmethod
    def get_children(category_id):
        """Get child categories."""
        return Category.query.filter_by(parent_id=category_id, is_active=True).all()