# product_service.py
from app.repositories.product_repository import ProductRepository


class ProductService:
    @staticmethod
    def get_product(product_id):
        """Get product with category details."""
        product = ProductRepository.get_by_id(product_id)
        if not product or not product.is_active:
            raise ValueError("Product not found or inactive")
        return product
    
    @staticmethod
    def search_products(query, filters=None):
        """Search products with advanced filters."""
        # Implement search logic with price range, category, stock filters
        pass
    
    @staticmethod
    def update_stock(product_id, quantity_change):
        """Update product stock with validation."""
        # Implement stock management
        pass