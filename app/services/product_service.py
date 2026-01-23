"""Product service with business logic and validation."""
from app.repositories.product_repository import ProductRepository
from app.repositories.category_repository import CategoryRepository
from app.extensions import db
import logging

logger = logging.getLogger(__name__)


class ProductService:
    """Service layer for product business logic."""
    
    @staticmethod
    def get_product(product_id):
        """
        Get product with category details.
        
        Args:
            product_id: Product ID
            
        Returns:
            Product object with category
            
        Raises:
            ValueError: If product not found or inactive
        """
        product = ProductRepository.get_by_id(product_id)
        if not product or not product.is_active:
            raise ValueError("Product not found or inactive")
        return product
    
    @staticmethod
    def get_product_by_slug(slug):
        """
        Get product by slug.
        
        Args:
            slug: Product slug
            
        Returns:
            Product object
            
        Raises:
            ValueError: If product not found
        """
        product = ProductRepository.get_by_slug(slug)
        if not product or not product.is_active:
            raise ValueError("Product not found or inactive")
        return product
    
    @staticmethod
    def get_all_products(page=1, per_page=20, filters=None):
        """
        Get all products with pagination and filters.
        
        Args:
            page: Page number (default: 1)
            per_page: Items per page (default: 20, max: 100)
            filters: Dictionary with optional filters:
                - category_id: Filter by category
                - featured: Only featured products
                - search: Search in name/description
                - min_price: Minimum price
                - max_price: Maximum price
                - in_stock: Only in-stock products
                
        Returns:
            Dictionary with products, pagination info
        """
        # Limit per_page to prevent abuse
        per_page = min(per_page, 100)
        
        filters = filters or {}
        
        # Get paginated products
        pagination = ProductRepository.get_all(
            page=page,
            per_page=per_page,
            category_id=filters.get('category_id'),
            featured=filters.get('featured'),
            search=filters.get('search'),
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
        """
        Create a new product with validation.
        
        Args:
            **data: Product data as keyword arguments
            
        Returns:
            Created product
            
        Raises:
            ValueError: If validation fails or category doesn't exist
        """
        # Validate required fields
        required_fields = ['name', 'price', 'category_id', 'sku', 'stock_quantity']
        for field in required_fields:
            if field not in data or data[field] is None:
                raise ValueError(f"{field} is required")
        
        # Validate category exists
        category = CategoryRepository.get_by_id(data['category_id'])
        if not category:
            raise ValueError("Category not found")
        
        if not category.is_active:
            raise ValueError("Category is not active")
        
        # Validate price
        if data['price'] <= 0:
            raise ValueError("Price must be greater than 0")
        
        # Validate stock quantity
        if data['stock_quantity'] < 0:
            raise ValueError("Stock quantity cannot be negative")
        
        # Validate compare_price if provided
        if data.get('compare_price') and data['compare_price'] <= data['price']:
            raise ValueError("Compare price must be greater than price")
        
        # Validate cost_price if provided
        if data.get('cost_price') and data['cost_price'] > data['price']:
            logger.warning(f"Product {data['name']}: cost_price ({data['cost_price']}) > price ({data['price']})")
        
        # Check if SKU already exists
        if ProductRepository.exists_by_sku(data['sku']):
            raise ValueError("SKU already exists")
        
        # Check if barcode exists (if provided)
        if data.get('barcode') and ProductRepository.exists_by_barcode(data['barcode']):
            raise ValueError("Barcode already exists")
        
        try:
            # Create product
            product = ProductRepository.create(**data)
            logger.info(f"Product created: {product.name} (ID: {product.id})")
            return product
        except Exception as e:
            logger.error(f"Error creating product: {e}", exc_info=True)
            raise
    
    @staticmethod
    def update_product(product_id, **data):
        """
        Update product with validation.
        
        Args:
            product_id: Product ID
            **data: Fields to update as keyword arguments
            
        Returns:
            Updated product
            
        Raises:
            ValueError: If validation fails or product not found
        """
        product = ProductRepository.get_by_id(product_id)
        if not product:
            raise ValueError("Product not found")
        
        # If updating category, validate it exists
        if 'category_id' in data and data['category_id'] != product.category_id:
            category = CategoryRepository.get_by_id(data['category_id'])
            if not category:
                raise ValueError("Category not found")
            if not category.is_active:
                raise ValueError("Category is not active")
        
        # Validate price if updating
        if 'price' in data and data['price'] <= 0:
            raise ValueError("Price must be greater than 0")
        
        # Validate stock quantity if updating
        if 'stock_quantity' in data and data['stock_quantity'] < 0:
            raise ValueError("Stock quantity cannot be negative")
        
        # Validate compare_price if updating
        if 'compare_price' in data:
            price = data.get('price', product.price)
            if data['compare_price'] and data['compare_price'] <= price:
                raise ValueError("Compare price must be greater than price")
        
        # If updating SKU, check if new SKU already exists
        if 'sku' in data and data['sku'] != product.sku:
            if ProductRepository.exists_by_sku(data['sku']):
                raise ValueError("SKU already exists")
        
        # If updating barcode, check if new barcode already exists
        if 'barcode' in data and data['barcode'] != product.barcode:
            if data['barcode'] and ProductRepository.exists_by_barcode(data['barcode']):
                raise ValueError("Barcode already exists")
        
        try:
            # Update product
            product = ProductRepository.update(product, **data)
            logger.info(f"Product updated: {product.name} (ID: {product.id})")
            return product
        except Exception as e:
            logger.error(f"Error updating product {product_id}: {e}", exc_info=True)
            raise
    
    @staticmethod
    def delete_product(product_id):
        """
        Soft delete product (set is_active to False).
        
        Args:
            product_id: Product ID
            
        Raises:
            ValueError: If product not found
        """
        product = ProductRepository.get_by_id(product_id)
        if not product:
            raise ValueError("Product not found")
        
        try:
            # Soft delete by setting is_active to False
            ProductRepository.update(product, is_active=False)
            logger.info(f"Product deleted (soft): {product.name} (ID: {product.id})")
        except Exception as e:
            logger.error(f"Error deleting product {product_id}: {e}", exc_info=True)
            raise
    
    @staticmethod
    def update_stock(product_id, quantity_change, operation='set'):
        """
        Update product stock with validation and stock tracking.
        
        Args:
            product_id: Product ID
            quantity_change: Quantity to add/subtract/set
            operation: 'add', 'subtract', or 'set' (default: 'set')
            
        Returns:
            Updated product with new stock
            
        Raises:
            ValueError: If product not found or insufficient stock
        """
        product = ProductRepository.get_by_id(product_id)
        if not product:
            raise ValueError("Product not found")
        
        old_stock = product.stock_quantity
        
        if operation == 'add':
            new_stock = old_stock + quantity_change
        elif operation == 'subtract':
            new_stock = old_stock - quantity_change
            if new_stock < 0:
                raise ValueError(
                    f"Insufficient stock. Available: {old_stock}, Requested: {quantity_change}"
                )
        elif operation == 'set':
            new_stock = quantity_change
            if new_stock < 0:
                raise ValueError("Stock quantity cannot be negative")
        else:
            raise ValueError("Invalid operation. Use 'add', 'subtract', or 'set'")
        
        try:
            # Update stock
            product = ProductRepository.update(product, stock_quantity=new_stock)
            logger.info(
                f"Stock updated for {product.name} (ID: {product.id}): "
                f"{old_stock} → {new_stock} ({operation} {quantity_change})"
            )
            return product
        except Exception as e:
            logger.error(f"Error updating stock for product {product_id}: {e}", exc_info=True)
            raise
    
    @staticmethod
    def check_stock_availability(product_id, quantity):
        """
        Check if product has sufficient stock.
        
        Args:
            product_id: Product ID
            quantity: Required quantity
            
        Returns:
            Tuple (available: bool, current_stock: int)
            
        Raises:
            ValueError: If product not found
        """
        product = ProductRepository.get_by_id(product_id)
        if not product:
            raise ValueError("Product not found")
        
        if not product.is_active:
            return False, 0
        
        available = product.stock_quantity >= quantity
        return available, product.stock_quantity
    
    @staticmethod
    def search_products(query, filters=None):
        """
        Search products with advanced filters.
        
        Args:
            query: Search query (searches in name and description)
            filters: Optional filters (category_id, price_range, etc.)
            
        Returns:
            List of matching products
        """
        filters = filters or {}
        filters['search'] = query
        
        result = ProductService.get_all_products(
            page=1,
            per_page=50,
            filters=filters
        )
        
        return result['products']
    
    @staticmethod
    def get_featured_products(limit=10):
        """
        Get featured products.
        
        Args:
            limit: Maximum number of products to return
            
        Returns:
            List of featured products
        """
        result = ProductService.get_all_products(
            page=1,
            per_page=limit,
            filters={'featured': True}
        )
        
        return result['products']
    
    @staticmethod
    def get_products_by_category(category_id, page=1, per_page=20):
        """
        Get products in a specific category.
        
        Args:
            category_id: Category ID
            page: Page number
            per_page: Items per page
            
        Returns:
            Dictionary with products and pagination
        """
        # Validate category exists
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
        """
        Get products with low stock (for inventory management).
        
        Args:
            threshold: Stock quantity threshold (default: 10)
            
        Returns:
            List of products with stock <= threshold
        """
        products = ProductRepository.get_low_stock(threshold=threshold)
        return [p.to_dict() for p in products]
    
    @staticmethod
    def bulk_update_prices(updates):
        """
        Bulk update product prices (admin operation).
        
        Args:
            updates: List of dicts with 'product_id' and 'price'
            
        Returns:
            Dictionary with success/failure counts
        """
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
                
                ProductService.update_product(product_id, {'price': price})
                success_count += 1
                
            except Exception as e:
                failed_count += 1
                errors.append(f"Product {product_id}: {str(e)}")
        
        return {
            'success': success_count,
            'failed': failed_count,
            'errors': errors
        }