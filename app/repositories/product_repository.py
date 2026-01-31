"""Product Repository - Final Clean Version"""
from app.extensions import db
from app.models.product import Product


class ProductRepository:
    """Repository for Product model operations."""
    
    @staticmethod
    def get_by_id(product_id):
        """Get product by ID."""
        return Product.query.get(product_id)
    
    @staticmethod
    def exists_by_sku(sku):
        """Check if SKU already exists (used for validation)."""
        return db.session.query(
            db.exists().where(Product.sku == sku)
        ).scalar()
    
    @staticmethod
    def exists_by_barcode(barcode):
        """Check if barcode already exists (used for validation)."""
        if not barcode:
            return False
        return db.session.query(
            db.exists().where(Product.barcode == barcode)
        ).scalar()
    
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
    def get_all(page=1, per_page=20, active_only=True, category_id=None, 
                featured=False, search_type=None, search_value=None):
        """
        Get all products with unified search support.
        
        Args:
            page: Page number
            per_page: Items per page
            active_only: Only active products
            category_id: Filter by category
            featured: Only featured products
            search_type: Field to search ('id', 'sku', 'slug', 'barcode', 'category_id', 'name')
            search_value: Value to search for
            
        Returns:
            Paginated query result
        """
        query = Product.query
        
        if active_only:
            query = query.filter_by(is_active=True)
        
        # Unified search - handles all search types
        if search_type and search_value:
            if search_type == 'id':
                query = query.filter_by(id=int(search_value))
            elif search_type == 'sku':
                query = query.filter_by(sku=search_value)
            elif search_type == 'slug':
                query = query.filter_by(slug=search_value)
            elif search_type == 'barcode':
                query = query.filter_by(barcode=search_value)
            elif search_type == 'category_id':
                query = query.filter_by(category_id=int(search_value))
            elif search_type == 'name':
                # Search in name and description
                search_term = f'%{search_value}%'
                query = query.filter(
                    db.or_(
                        Product.name.ilike(search_term),
                        Product.description.ilike(search_term)
                    )
                )
        # Standalone category filter (when not using search)
        elif category_id:
            query = query.filter_by(category_id=category_id)
        
        if featured:
            query = query.filter_by(is_featured=True)
        
        return query.order_by(Product.created_at.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
    
    @staticmethod
    def get_low_stock(threshold=10):
        """
        Get products with stock below threshold.
        
        Args:
            threshold: Stock quantity threshold
            
        Returns:
            List of products with low stock
        """
        return Product.query.filter(
            Product.is_active == True,
            Product.stock_quantity <= threshold
        ).order_by(Product.stock_quantity.asc()).all()