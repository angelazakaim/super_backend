"""Product Service - Final Clean Version"""
from app.repositories.product_repository import ProductRepository
from app.repositories.category_repository import CategoryRepository
import logging

logger = logging.getLogger(__name__)


class ProductService:
    """Service layer for product business logic."""
    
    @staticmethod
    def get_product(product_id):
        """Get product by ID (used internally by update/delete operations)."""
        product = ProductRepository.get_by_id(product_id)
        if not product or not product.is_active:
            raise ValueError("Product not found or inactive")
        return product
    
    @staticmethod
    def get_all_products(page=1, per_page=20, filters=None):
        """
        Get all products with pagination and unified search filters.
        
        Args:
            page: Page number
            per_page: Items per page
            filters: Dictionary of filter options:
                - category_id: Filter by category
                - featured: Only featured products
                - search_type: Field to search ('id', 'sku', 'slug', 'barcode', 'category_id', 'name')
                - search_value: Value to search for
                
        Returns:
            Dictionary with products and pagination metadata
        """
        per_page = min(per_page, 100)
        filters = filters or {}
        
        pagination = ProductRepository.get_all(
            page=page,
            per_page=per_page,
            category_id=filters.get('category_id'),
            featured=filters.get('featured'),
            search_type=filters.get('search_type'),
            search_value=filters.get('search_value'),
            active_only=True
        )
        
        return {
            'products': [p.to_dict() for p in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    
    @staticmethod
    def create_product(**data):
        """Create a new product with validation."""
        required_fields = ['name', 'price', 'category_id', 'sku', 'stock_quantity']
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValueError(f"{field} is required")
        
        category = CategoryRepository.get_by_id(data['category_id'])
        if not category:
            raise ValueError("Category not found")
        if not category.is_active:
            raise ValueError("Category is not active")
        
        if data['price'] <= 0:
            raise ValueError("Price must be greater than 0")
        
        if data['stock_quantity'] < 0:
            raise ValueError("Stock quantity cannot be negative")
        
        if data.get('compare_price') and data['compare_price'] <= data['price']:
            raise ValueError("Compare price must be greater than price")
        
        if ProductRepository.exists_by_sku(data['sku']):
            raise ValueError("SKU already exists")
        
        if data.get('barcode') and ProductRepository.exists_by_barcode(data['barcode']):
            raise ValueError("Barcode already exists")
        
        try:
            product = ProductRepository.create(**data)
            logger.info(f"Product created: {product.name} (ID: {product.id})")
            return product
        except Exception as e:
            logger.error(f"Error creating product: {e}", exc_info=True)
            raise
    
    @staticmethod
    def update_product(product_id, **data):
        """Update product with validation."""
        product = ProductRepository.get_by_id(product_id)
        if not product:
            raise ValueError("Product not found")
        
        if 'category_id' in data and data['category_id'] != product.category_id:
            category = CategoryRepository.get_by_id(data['category_id'])
            if not category:
                raise ValueError("Category not found")
            if not category.is_active:
                raise ValueError("Category is not active")
        
        if 'price' in data and data['price'] <= 0:
            raise ValueError("Price must be greater than 0")
        
        if 'stock_quantity' in data and data['stock_quantity'] < 0:
            raise ValueError("Stock quantity cannot be negative")
        
        if 'compare_price' in data:
            price = data.get('price', product.price)
            if data['compare_price'] and data['compare_price'] <= price:
                raise ValueError("Compare price must be greater than price")
        
        if 'sku' in data and data['sku'] != product.sku:
            if ProductRepository.exists_by_sku(data['sku']):
                raise ValueError("SKU already exists")
        
        if 'barcode' in data and data['barcode'] != product.barcode:
            if data['barcode'] and ProductRepository.exists_by_barcode(data['barcode']):
                raise ValueError("Barcode already exists")
        
        try:
            product = ProductRepository.update(product, **data)
            logger.info(f"Product updated: {product.name} (ID: {product.id})")
            return product
        except Exception as e:
            logger.error(f"Error updating product {product_id}: {e}", exc_info=True)
            raise
    
    @staticmethod
    def delete_product(product_id):
        """Soft delete product (set is_active to False)."""
        product = ProductRepository.get_by_id(product_id)
        if not product:
            raise ValueError("Product not found")
        
        try:
            ProductRepository.update(product, is_active=False)
            logger.info(f"Product deleted (soft): {product.name} (ID: {product.id})")
        except Exception as e:
            logger.error(f"Error deleting product {product_id}: {e}", exc_info=True)
            raise
    
    @staticmethod
    def hard_delete_product(product_id):
        """
        Permanently delete product from database (admin only).
        WARNING: This cannot be undone!
        """
        product = ProductRepository.get_by_id(product_id)
        if not product:
            raise ValueError("Product not found")
        
        try:
            product_name = product.name
            ProductRepository.delete(product)
            logger.warning(f"Product PERMANENTLY deleted: {product_name} (ID: {product_id})")
        except Exception as e:
            logger.error(f"Error permanently deleting product {product_id}: {e}", exc_info=True)
            raise ValueError(f"Failed to delete product: {str(e)}")
    
    @staticmethod
    def update_stock(product_id, quantity_change, operation='set'):
        """Update product stock with validation."""
        product = ProductRepository.get_by_id(product_id)
        if not product:
            raise ValueError("Product not found")
        
        old_stock = product.stock_quantity
        
        if operation == 'add':
            new_stock = old_stock + quantity_change
        elif operation == 'subtract':
            new_stock = old_stock - quantity_change
            if new_stock < 0:
                raise ValueError(f"Insufficient stock. Available: {old_stock}, Requested: {quantity_change}")
        elif operation == 'set':
            new_stock = quantity_change
            if new_stock < 0:
                raise ValueError("Stock quantity cannot be negative")
        else:
            raise ValueError("Invalid operation. Use 'add', 'subtract', or 'set'")
        
        try:
            product = ProductRepository.update(product, stock_quantity=new_stock)
            logger.info(f"Stock updated for {product.name}: {old_stock} → {new_stock}")
            return product
        except Exception as e:
            logger.error(f"Error updating stock: {e}", exc_info=True)
            raise
    
    @staticmethod
    def check_stock_availability(product_id, quantity):
        """Check if product has sufficient stock."""
        product = ProductRepository.get_by_id(product_id)
        if not product:
            raise ValueError("Product not found")
        
        if not product.is_active:
            return False, 0
        
        available = product.stock_quantity >= quantity
        return available, product.stock_quantity
    
    @staticmethod
    def search_products(query, filters=None):
        """Search products by name/description - convenience wrapper."""
        filters = filters or {}
        filters['search_type'] = 'name'
        filters['search_value'] = query
        
        result = ProductService.get_all_products(page=1, per_page=50, filters=filters)
        return result['products']
    
    @staticmethod
    def get_featured_products(limit=10):
        """Get featured products - convenience wrapper."""
        result = ProductService.get_all_products(
            page=1,
            per_page=limit,
            filters={'featured': True}
        )
        return result['products']
    
    @staticmethod
    def get_products_by_category(category_id, page=1, per_page=20):
        """Get products in a specific category - convenience wrapper."""
        category = CategoryRepository.get_by_id(category_id)
        if not category:
            raise ValueError("Category not found")
        
        return ProductService.get_all_products(
            page=page,
            per_page=per_page,
            filters={'category_id': category_id}
        )
    
    @staticmethod
    def get_low_stock_products(threshold=10):
        """Get products with low stock."""
        products = ProductRepository.get_low_stock(threshold=threshold)
        return [p.to_dict() for p in products]
    
    @staticmethod
    def bulk_update_prices(updates):
        """Bulk update product prices."""
        success_count = 0
        failed_count = 0
        errors = []
        
        for update in updates:
            try:
                product_id = update.get('product_id')
                price = update.get('price')
                
                if not product_id or not price:
                    failed_count += 1
                    errors.append(f"Product {product_id}: Missing data")
                    continue
                
                ProductService.update_product(product_id, price=price)
                success_count += 1
                
            except Exception as e:
                failed_count += 1
                errors.append(f"Product {product_id}: {str(e)}")
        
        return {
            'success': success_count,
            'failed': failed_count,
            'errors': errors
        }