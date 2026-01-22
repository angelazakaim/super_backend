from app.extensions import db
from app.models.product import Product

class ProductRepository:
    """Repository for Product model operations."""
    
    @staticmethod
    def get_by_id(product_id):
        """Get product by ID."""
        return Product.query.get(product_id)
    
    @staticmethod
    def get_by_slug(slug):
        """Get product by slug."""
        return Product.query.filter_by(slug=slug, is_active=True).first()
    
    @staticmethod
    def get_by_sku(sku):
        """Get product by SKU."""
        return Product.query.filter_by(sku=sku).first()
    
    @staticmethod
    def create(**kwargs):
        """Create a new product."""
        product = Product(**kwargs)
        db.session.add(product)
        db.session.commit()
        return product
    
    @staticmethod
    def update(product, **kwargs):
        """Update product attributes."""
        for key, value in kwargs.items():
            if hasattr(product, key):
                setattr(product, key, value)
        db.session.commit()
        return product
    
    @staticmethod
    def delete(product):
        """Delete a product."""
        db.session.delete(product)
        db.session.commit()
    
    @staticmethod
    def get_all(page=1, per_page=20, active_only=True, category_id=None, featured_only=False):
        """Get all products with filters and pagination."""
        query = Product.query
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        if featured_only:
            query = query.filter_by(is_featured=True)
        
        return query.order_by(Product.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def search(search_term, page=1, per_page=20):
        """Search products by name or description."""
        query = Product.query.filter(
            db.or_(
                Product.name.ilike(f'%{search_term}%'),
                Product.description.ilike(f'%{search_term}%')
            ),
            Product.is_active == True
        )
        return query.order_by(Product.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    
    @staticmethod
    def update_stock(product, quantity_change):
        """Update product stock quantity."""
        product.stock_quantity += quantity_change
        db.session.commit()
        return product