"""Product model with slug as database column - FIXED VERSION."""
from datetime import datetime, timezone
from app.extensions import db
import re


class Product(db.Model):
    """Product model."""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    #slug is also a database column, not a property
    slug = db.Column(db.String(250), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    compare_price = db.Column(db.Numeric(10, 2))  # Original price for discounts
    sku = db.Column(db.String(100), unique=True, nullable=False, index=True)
    barcode = db.Column(db.String(100), unique=True, index=True)
    stock_quantity = db.Column(db.Integer, default=0, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    
    # Product attributes
    weight = db.Column(db.Numeric(10, 2))  # in kg
    dimensions = db.Column(db.String(100))  # e.g., "10x20x30 cm"
    image_url = db.Column(db.String(500))
    images = db.Column(db.JSON)  # Array of image URLs
    
    # Status flags
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    def __init__(self, name, price, category_id, sku, stock_quantity,
                 description=None, slug=None, barcode=None, compare_price=None,
                 weight=None, dimensions=None, image_url=None, images=None,
                 is_active=True, is_featured=False):
        """Initialize product and auto-generate slug if not provided."""
        self.name = name
        self.price = price
        self.category_id = category_id
        self.sku = sku
        self.stock_quantity = stock_quantity
        self.description = description
        self.barcode = barcode
        self.compare_price = compare_price
        self.weight = weight
        self.dimensions = dimensions
        self.image_url = image_url
        self.images = images
        self.is_active = is_active
        self.is_featured = is_featured
        
        # Auto-generate slug from name if not provided
        self.slug = slug or self._generate_slug(name)
    
    @staticmethod
    def _generate_slug(name):
        """
        Generate URL-friendly slug from product name.
        
        Examples:
            "Samsung Galaxy S24" -> "samsung-galaxy-s24"
            "Men's T-Shirt (Blue)" -> "mens-t-shirt-blue"
            "iPhone 15 Pro Max" -> "iphone-15-pro-max"
        """
        if not name:
            return ''
        slug = name.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special characters
        slug = re.sub(r'[\s_-]+', '-', slug)  # Replace spaces with hyphens
        slug = slug.strip('-')                 # Remove leading/trailing hyphens
        return slug
    
    def update_slug(self):
        """Update slug when name changes."""
        self.slug = self._generate_slug(self.name)
    
    @property
    def is_in_stock(self):
        """Check if product is in stock."""
        return self.stock_quantity > 0
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage if compare_price is set."""
        if self.compare_price and self.compare_price > self.price:
            return round(((self.compare_price - self.price) / self.compare_price) * 100, 2)
        return 0
    
    def to_dict(self, include_category=False):
        """Convert product to dictionary."""
        data = {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,  # Always available now!
            'description': self.description,
            'price': float(self.price),
            'compare_price': float(self.compare_price) if self.compare_price else None,
            'discount_percentage': self.discount_percentage,
            'sku': self.sku,
            'barcode': self.barcode,
            'stock_quantity': self.stock_quantity,
            'is_in_stock': self.is_in_stock,
            'category_id': self.category_id,
            'weight': float(self.weight) if self.weight else None,
            'dimensions': self.dimensions,
            'image_url': self.image_url,
            'images': self.images or [],
            'is_active': self.is_active,
            'is_featured': self.is_featured,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_category and self.category:
            data['category'] = self.category.to_dict()
        
        return data
    
    def __repr__(self):
        return f'<Product {self.name}>'