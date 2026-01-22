"""Marshmallow schemas for API input validation."""
from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError
from decimal import Decimal


# ============================================================================
# AUTH SCHEMAS
# ============================================================================

class RegisterSchema(Schema):
    """Schema for user registration."""
    email = fields.Email(required=True, error_messages={
        'required': 'Email is required',
        'invalid': 'Invalid email format'
    })
    username = fields.Str(
        required=True,
        validate=validate.And(
            validate.Length(min=3, max=80, error='Username must be between 3 and 80 characters'),
            validate.Regexp(
                r'^[a-zA-Z0-9_-]+$',
                error='Username can only contain letters, numbers, underscores, and hyphens'
            )
        )
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=8, max=128, error='Password must be between 8 and 128 characters')
    )
    role = fields.Str(
        missing='customer',
        validate=validate.OneOf(
            ['customer', 'admin', 'manager', 'cashier'],
            error='Invalid role'
        )
    )
    first_name = fields.Str(validate=validate.Length(max=50))
    last_name = fields.Str(validate=validate.Length(max=50))
    phone = fields.Str(validate=validate.Length(max=20))


class LoginSchema(Schema):
    """Schema for user login."""
    email_or_username = fields.Str(required=True, error_messages={
        'required': 'Email or username is required'
    })
    password = fields.Str(required=True, error_messages={
        'required': 'Password is required'
    })


class ChangePasswordSchema(Schema):
    """Schema for changing password."""
    old_password = fields.Str(required=True, error_messages={
        'required': 'Current password is required'
    })
    new_password = fields.Str(
        required=True,
        validate=validate.Length(min=8, max=128, error='Password must be between 8 and 128 characters'),
        error_messages={'required': 'New password is required'}
    )
    
    @validates_schema
    def validate_passwords(self, data, **kwargs):
        """Ensure old and new passwords are different."""
        if data.get('old_password') == data.get('new_password'):
            raise ValidationError('New password must be different from current password')


# ============================================================================
# USER & CUSTOMER SCHEMAS
# ============================================================================

class UserUpdateSchema(Schema):
    """Schema for updating user information."""
    email = fields.Email()
    username = fields.Str(
        validate=validate.And(
            validate.Length(min=3, max=80),
            validate.Regexp(r'^[a-zA-Z0-9_-]+$')
        )
    )
    is_active = fields.Bool()


class CustomerProfileSchema(Schema):
    """Schema for customer profile data."""
    first_name = fields.Str(validate=validate.Length(max=50))
    last_name = fields.Str(validate=validate.Length(max=50))
    phone = fields.Str(validate=validate.Length(max=20))
    address_line1 = fields.Str(validate=validate.Length(max=255))
    address_line2 = fields.Str(validate=validate.Length(max=255))
    city = fields.Str(validate=validate.Length(max=100))
    state = fields.Str(validate=validate.Length(max=100))
    postal_code = fields.Str(validate=validate.Length(max=20))
    country = fields.Str(validate=validate.Length(max=100))


# ============================================================================
# CATEGORY SCHEMAS
# ============================================================================

class CategoryCreateSchema(Schema):
    """Schema for creating a category."""
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100, error='Name must be between 1 and 100 characters'),
        error_messages={'required': 'Category name is required'}
    )
    description = fields.Str(validate=validate.Length(max=1000))
    parent_id = fields.Int(allow_none=True)
    is_active = fields.Bool(missing=True)


class CategoryUpdateSchema(Schema):
    """Schema for updating a category."""
    name = fields.Str(validate=validate.Length(min=1, max=100))
    description = fields.Str(validate=validate.Length(max=1000))
    parent_id = fields.Int(allow_none=True)
    is_active = fields.Bool()


# ============================================================================
# PRODUCT SCHEMAS
# ============================================================================

class ProductCreateSchema(Schema):
    """Schema for creating a product."""
    name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=200, error='Name must be between 1 and 200 characters'),
        error_messages={'required': 'Product name is required'}
    )
    description = fields.Str(validate=validate.Length(max=5000))
    price = fields.Decimal(
        required=True,
        places=2,
        validate=validate.Range(min=0.01, error='Price must be greater than 0'),
        error_messages={'required': 'Price is required'}
    )
    compare_price = fields.Decimal(
        places=2,
        allow_none=True,
        validate=validate.Range(min=0.01)
    )
    sku = fields.Str(
        validate=validate.And(
            validate.Length(max=100),
            validate.Regexp(r'^[A-Z0-9-_]+$', error='SKU can only contain uppercase letters, numbers, hyphens, and underscores')
        )
    )
    stock_quantity = fields.Int(
        missing=0,
        validate=validate.Range(min=0, error='Stock quantity cannot be negative')
    )
    category_id = fields.Int(
        required=True,
        error_messages={'required': 'Category is required'}
    )
    weight = fields.Decimal(
        places=2,
        allow_none=True,
        validate=validate.Range(min=0)
    )
    dimensions = fields.Str(validate=validate.Length(max=100))
    image_url = fields.Url(validate=validate.Length(max=500))
    images = fields.List(fields.Url())
    is_active = fields.Bool(missing=True)
    is_featured = fields.Bool(missing=False)
    
    @validates_schema
    def validate_prices(self, data, **kwargs):
        """Ensure compare_price is greater than price if provided."""
        price = data.get('price')
        compare_price = data.get('compare_price')
        
        if compare_price and price and compare_price <= price:
            raise ValidationError(
                'Compare price must be greater than regular price',
                field_name='compare_price'
            )


class ProductUpdateSchema(Schema):
    """Schema for updating a product."""
    name = fields.Str(validate=validate.Length(min=1, max=200))
    description = fields.Str(validate=validate.Length(max=5000))
    price = fields.Decimal(
        places=2,
        validate=validate.Range(min=0.01)
    )
    compare_price = fields.Decimal(
        places=2,
        allow_none=True,
        validate=validate.Range(min=0.01)
    )
    sku = fields.Str(
        validate=validate.And(
            validate.Length(max=100),
            validate.Regexp(r'^[A-Z0-9-_]+$')
        )
    )
    stock_quantity = fields.Int(validate=validate.Range(min=0))
    category_id = fields.Int()
    weight = fields.Decimal(places=2, allow_none=True, validate=validate.Range(min=0))
    dimensions = fields.Str(validate=validate.Length(max=100))
    image_url = fields.Url(validate=validate.Length(max=500))
    images = fields.List(fields.Url())
    is_active = fields.Bool()
    is_featured = fields.Bool()
    
    @validates_schema
    def validate_prices(self, data, **kwargs):
        """Ensure compare_price is greater than price if both provided."""
        price = data.get('price')
        compare_price = data.get('compare_price')
        
        if compare_price and price and compare_price <= price:
            raise ValidationError(
                'Compare price must be greater than regular price',
                field_name='compare_price'
            )


# ============================================================================
# CART SCHEMAS
# ============================================================================

class AddToCartSchema(Schema):
    """Schema for adding item to cart."""
    product_id = fields.Int(
        required=True,
        validate=validate.Range(min=1, error='Invalid product ID'),
        error_messages={'required': 'Product ID is required'}
    )
    quantity = fields.Int(
        missing=1,
        validate=validate.Range(min=1, max=100, error='Quantity must be between 1 and 100')
    )


class UpdateCartItemSchema(Schema):
    """Schema for updating cart item quantity."""
    quantity = fields.Int(
        required=True,
        validate=validate.Range(min=1, max=100, error='Quantity must be between 1 and 100'),
        error_messages={'required': 'Quantity is required'}
    )


# ============================================================================
# ORDER SCHEMAS
# ============================================================================

class ShippingAddressSchema(Schema):
    """Schema for shipping address."""
    line1 = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=255),
        error_messages={'required': 'Address line 1 is required'}
    )
    line2 = fields.Str(validate=validate.Length(max=255), allow_none=True)
    city = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={'required': 'City is required'}
    )
    state = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={'required': 'State is required'}
    )
    postal_code = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=20),
        error_messages={'required': 'Postal code is required'}
    )
    country = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={'required': 'Country is required'}
    )


class CreateOrderSchema(Schema):
    """Schema for creating an order."""
    shipping_address = fields.Nested(
        ShippingAddressSchema,
        required=True,
        error_messages={'required': 'Shipping address is required'}
    )
    payment_method = fields.Str(
        validate=validate.OneOf(
            ['credit_card', 'debit_card', 'paypal', 'cash', 'bank_transfer'],
            error='Invalid payment method'
        )
    )
    customer_notes = fields.Str(validate=validate.Length(max=1000))


class UpdateOrderStatusSchema(Schema):
    """Schema for updating order status."""
    status = fields.Str(
        required=True,
        validate=validate.OneOf(
            ['pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded'],
            error='Invalid order status'
        ),
        error_messages={'required': 'Status is required'}
    )


class UpdatePaymentStatusSchema(Schema):
    """Schema for updating payment status."""
    payment_status = fields.Str(
        required=True,
        validate=validate.OneOf(
            ['pending', 'paid', 'failed', 'refunded'],
            error='Invalid payment status'
        ),
        error_messages={'required': 'Payment status is required'}
    )


# ============================================================================
# PAGINATION SCHEMAS
# ============================================================================

class PaginationSchema(Schema):
    """Schema for pagination parameters."""
    page = fields.Int(
        missing=1,
        validate=validate.Range(min=1, error='Page must be at least 1')
    )
    per_page = fields.Int(
        missing=20,
        validate=validate.Range(min=1, max=100, error='Items per page must be between 1 and 100')
    )


# ============================================================================
# SEARCH SCHEMAS
# ============================================================================

class ProductSearchSchema(PaginationSchema):
    """Schema for product search parameters."""
    search = fields.Str(validate=validate.Length(max=200))
    category_id = fields.Int(validate=validate.Range(min=1))
    min_price = fields.Decimal(places=2, validate=validate.Range(min=0))
    max_price = fields.Decimal(places=2, validate=validate.Range(min=0))
    featured = fields.Bool()
    in_stock_only = fields.Bool(missing=False)
    
    @validates_schema
    def validate_price_range(self, data, **kwargs):
        """Ensure min_price is less than max_price."""
        min_price = data.get('min_price')
        max_price = data.get('max_price')
        
        if min_price and max_price and min_price >= max_price:
            raise ValidationError(
                'Minimum price must be less than maximum price',
                field_name='min_price'
            )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def validate_schema(schema_class, data):
    """
    Validate data against a schema.
    
    Args:
        schema_class: Marshmallow schema class
        data: Data to validate
        
    Returns:
        Validated and deserialized data
        
    Raises:
        ValidationError: If validation fails
    """
    schema = schema_class()
    return schema.load(data)


def validate_with_errors(schema_class, data):
    """
    Validate data and return errors in a friendly format.
    
    Args:
        schema_class: Marshmallow schema class
        data: Data to validate
        
    Returns:
        Tuple of (is_valid, validated_data_or_errors)
    """
    schema = schema_class()
    try:
        validated_data = schema.load(data)
        return True, validated_data
    except ValidationError as e:
        return False, e.messages