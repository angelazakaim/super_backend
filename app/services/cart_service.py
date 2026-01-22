"""Cart service with race condition protection and validation."""
import logging
from typing import Optional, Any
from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository
from app.models.product import Product
from app.extensions import db
from sqlalchemy import select

logger = logging.getLogger(__name__)


class CartService:
    """Service for cart operations with race condition protection."""
    
    @staticmethod
    def get_or_create_cart(customer_id: int) -> Any:
        """
        Get customer's cart or create new one.
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Cart object
        """
        logger.info(f"Getting or creating cart for customer: {customer_id}")
        
        try:
            cart = CartRepository.get_or_create(customer_id)
            logger.info(f"Cart retrieved/created for customer {customer_id}: cart_id={cart.id}")
            return cart
        except Exception as e:
            logger.error(f"Failed to get/create cart: {e}", exc_info=True)
            raise ValueError(f"Failed to get cart: {str(e)}")
    
    @staticmethod
    def add_to_cart(
        customer_id: int,
        product_id: int,
        quantity: int = 1,
        use_lock: bool = True
    ) -> Any:
        """
        Add product to cart with race condition protection.
        
        Args:
            customer_id: Customer ID
            product_id: Product ID
            quantity: Quantity to add
            use_lock: Whether to use database locking (default: True)
            
        Returns:
            Updated cart
            
        Raises:
            ValueError: If validation fails or insufficient stock
        """
        logger.info(
            f"Adding to cart - customer: {customer_id}, "
            f"product: {product_id}, quantity: {quantity}"
        )
        
        # Validate quantity
        if quantity < 1:
            logger.error(f"Invalid quantity: {quantity}")
            raise ValueError("Quantity must be at least 1")
        
        if quantity > 100:
            logger.error(f"Quantity too large: {quantity}")
            raise ValueError("Maximum quantity per item is 100")
        
        try:
            # Use SELECT FOR UPDATE to prevent race conditions
            if use_lock:
                product = db.session.execute(
                    select(Product)
                    .where(Product.id == product_id)
                    .with_for_update()
                ).scalar_one_or_none()
            else:
                product = ProductRepository.get_by_id(product_id)
            
            # Validate product exists
            if not product:
                logger.error(f"Product not found: {product_id}")
                raise ValueError("Product not found")
            
            # Validate product is active
            if not product.is_active:
                logger.error(f"Product is inactive: {product_id}")
                raise ValueError("Product is not available")
            
            # Validate stock availability
            if product.stock_quantity < quantity:
                logger.error(
                    f"Insufficient stock for product {product_id}. "
                    f"Available: {product.stock_quantity}, Requested: {quantity}"
                )
                raise ValueError(
                    f"Only {product.stock_quantity} item(s) available in stock"
                )
            
            # Get or create cart
            cart = CartRepository.get_or_create(customer_id)
            
            # Check if item already exists in cart
            existing_item = CartRepository.get_cart_item(cart.id, product_id)
            if existing_item:
                new_quantity = existing_item.quantity + quantity
                
                # Validate total quantity doesn't exceed stock
                if new_quantity > product.stock_quantity:
                    logger.error(
                        f"Adding {quantity} would exceed stock. "
                        f"Cart has: {existing_item.quantity}, "
                        f"Stock: {product.stock_quantity}"
                    )
                    raise ValueError(
                        f"Cannot add {quantity}. Cart already has {existing_item.quantity}. "
                        f"Only {product.stock_quantity} available in stock."
                    )
                
                # Validate doesn't exceed max per item
                if new_quantity > 100:
                    raise ValueError("Maximum 100 items per product")
            
            # Add item to cart
            cart_item = CartRepository.add_item(cart, product_id, quantity)
            
            # Commit transaction
            db.session.commit()
            
            logger.info(
                f"Successfully added {quantity} of product {product_id} "
                f"to cart for customer {customer_id}"
            )
            
            return cart
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to add to cart: {e}", exc_info=True)
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Failed to add item to cart: {str(e)}")
    
    @staticmethod
    def update_cart_item(
        customer_id: int,
        product_id: int,
        quantity: int,
        use_lock: bool = True
    ) -> Any:
        """
        Update cart item quantity with race condition protection.
        
        Args:
            customer_id: Customer ID
            product_id: Product ID
            quantity: New quantity
            use_lock: Whether to use database locking
            
        Returns:
            Updated cart
            
        Raises:
            ValueError: If validation fails
        """
        logger.info(
            f"Updating cart item - customer: {customer_id}, "
            f"product: {product_id}, new quantity: {quantity}"
        )
        
        # Validate quantity
        if quantity < 1:
            logger.error(f"Invalid quantity: {quantity}")
            raise ValueError("Quantity must be at least 1")
        
        if quantity > 100:
            logger.error(f"Quantity too large: {quantity}")
            raise ValueError("Maximum quantity per item is 100")
        
        try:
            # Use SELECT FOR UPDATE to prevent race conditions
            if use_lock:
                product = db.session.execute(
                    select(Product)
                    .where(Product.id == product_id)
                    .with_for_update()
                ).scalar_one_or_none()
            else:
                product = ProductRepository.get_by_id(product_id)
            
            # Validate product exists
            if not product:
                logger.error(f"Product not found: {product_id}")
                raise ValueError("Product not found")
            
            # Validate stock availability
            if product.stock_quantity < quantity:
                logger.error(
                    f"Insufficient stock for product {product_id}. "
                    f"Available: {product.stock_quantity}, Requested: {quantity}"
                )
                raise ValueError(
                    f"Only {product.stock_quantity} item(s) available in stock"
                )
            
            # Get cart
            cart = CartRepository.get_by_customer_id(customer_id)
            if not cart:
                logger.error(f"Cart not found for customer: {customer_id}")
                raise ValueError("Cart not found")
            
            # Get cart item
            cart_item = CartRepository.get_cart_item(cart.id, product_id)
            if not cart_item:
                logger.error(
                    f"Item not in cart - customer: {customer_id}, product: {product_id}"
                )
                raise ValueError("Item not in cart")
            
            # Update quantity
            CartRepository.update_item_quantity(cart_item, quantity)
            
            # Commit transaction
            db.session.commit()
            
            logger.info(
                f"Successfully updated quantity to {quantity} for product {product_id} "
                f"in customer {customer_id}'s cart"
            )
            
            return cart
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to update cart item: {e}", exc_info=True)
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Failed to update cart item: {str(e)}")
    
    @staticmethod
    def remove_from_cart(customer_id: int, product_id: int) -> Any:
        """
        Remove product from cart.
        
        Args:
            customer_id: Customer ID
            product_id: Product ID
            
        Returns:
            Updated cart
            
        Raises:
            ValueError: If cart or item not found
        """
        logger.info(
            f"Removing from cart - customer: {customer_id}, product: {product_id}"
        )
        
        try:
            cart = CartRepository.get_by_customer_id(customer_id)
            if not cart:
                logger.error(f"Cart not found for customer: {customer_id}")
                raise ValueError("Cart not found")
            
            cart_item = CartRepository.get_cart_item(cart.id, product_id)
            if not cart_item:
                logger.error(
                    f"Item not in cart - customer: {customer_id}, product: {product_id}"
                )
                raise ValueError("Item not in cart")
            
            CartRepository.remove_item(cart_item)
            
            logger.info(
                f"Successfully removed product {product_id} "
                f"from customer {customer_id}'s cart"
            )
            
            return cart
            
        except Exception as e:
            logger.error(f"Failed to remove from cart: {e}", exc_info=True)
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Failed to remove item from cart: {str(e)}")
    
    @staticmethod
    def clear_cart(customer_id: int) -> Optional[Any]:
        """
        Clear all items from cart.
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Empty cart or None if cart doesn't exist
        """
        logger.info(f"Clearing cart for customer: {customer_id}")
        
        try:
            cart = CartRepository.get_by_customer_id(customer_id)
            if cart:
                CartRepository.clear_cart(cart)
                logger.info(f"Successfully cleared cart for customer: {customer_id}")
            else:
                logger.info(f"No cart found for customer: {customer_id}")
            
            return cart
            
        except Exception as e:
            logger.error(f"Failed to clear cart: {e}", exc_info=True)
            raise ValueError(f"Failed to clear cart: {str(e)}")
    
    @staticmethod
    def get_cart(customer_id: int) -> Optional[Any]:
        """
        Get customer's cart.
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Cart object or None if cart doesn't exist
        """
        logger.info(f"Fetching cart for customer: {customer_id}")
        
        try:
            cart = CartRepository.get_by_customer_id(customer_id)
            
            if cart:
                logger.info(
                    f"Cart found for customer {customer_id}: "
                    f"{cart.total_items} items, subtotal: ${cart.subtotal}"
                )
            else:
                logger.info(f"No cart found for customer: {customer_id}")
            
            return cart
            
        except Exception as e:
            logger.error(f"Failed to fetch cart: {e}", exc_info=True)
            raise ValueError(f"Failed to fetch cart: {str(e)}")
    
    @staticmethod
    def validate_cart_for_checkout(customer_id: int) -> tuple[bool, str]:
        """
        Validate cart is ready for checkout.
        
        Args:
            customer_id: Customer ID
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        logger.info(f"Validating cart for checkout - customer: {customer_id}")
        
        try:
            cart = CartRepository.get_by_customer_id(customer_id)
            
            # Check cart exists
            if not cart:
                return False, "Cart is empty"
            
            # Check has items
            if not cart.items or cart.items.count() == 0:
                return False, "Cart is empty"
            
            # Validate each item
            for item in cart.items:
                product = item.product
                
                # Check product is active
                if not product.is_active:
                    return False, f"Product '{product.name}' is no longer available"
                
                # Check stock availability
                if product.stock_quantity < item.quantity:
                    return False, (
                        f"Insufficient stock for '{product.name}'. "
                        f"Only {product.stock_quantity} available, "
                        f"but cart has {item.quantity}"
                    )
            
            logger.info(f"Cart validation passed for customer: {customer_id}")
            return True, ""
            
        except Exception as e:
            logger.error(f"Cart validation failed: {e}", exc_info=True)
            return False, f"Cart validation failed: {str(e)}"