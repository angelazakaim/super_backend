"""Category model with slug as database column."""
from datetime import datetime, timezone
import re
from app.extensions import db


class Category(db.Model):
    """Product category model."""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    #Angela note: we store in DB and backend UTC time. The fronend will convert to local time as needed. This will allow concsistency in time.
    #Read document section "Handlig datetime Understanding lambda and the Timestamp Code "
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
        # Self-referential relationship for hierarchical categories
    #     children = db.relationship(
    #     'Category',                              # Target: Category model
    #     backref=db.backref('parent',            # Reverse: category.parent
    #                        remote_side=[id]),    # Parent is "remote" side
    #     cascade='all, delete-orphan'            # Delete children with parent
    # )
    
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]),
                             lazy='dynamic', cascade='all, delete-orphan')
    products = db.relationship('Product', backref='category', lazy='dynamic')
    
    def __init__(self, name, description=None, parent_id=None, is_active=True, slug=None):
        """Initialize category and auto-generate slug if not provided."""
        self.name = name
        self.description = description
        self.parent_id = parent_id
        self.is_active = is_active
        # Auto-generate slug from name if not provided
        self.slug = slug or self._generate_slug(name)
    
    @staticmethod
    def _generate_slug(name):
        """
        Generate URL-friendly slug from name.
        
        Examples:
            "Electronics" -> "electronics"
            "Men's Clothing" -> "mens-clothing"
            "Home & Garden" -> "home-garden"
        """
        slug = name.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special characters
        slug = re.sub(r'[\s_-]+', '-', slug)  # Replace spaces with hyphens
        slug = slug.strip('-')                 # Remove leading/trailing hyphens
        return slug
    
    def update_slug(self):
        """Update slug when name changes."""
        self.slug = self._generate_slug(self.name)
    
    @property
    def full_path(self):
        """Get full category path (e.g., 'Electronics > Computers')."""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name
    
    def to_dict(self, include_children=False, include_products=False):
        """Convert category to dictionary."""
        data = {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,  # Always available now!
            'description': self.description,
            'parent_id': self.parent_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_children:
            data['children'] = [child.to_dict() for child in self.children]
        
        if include_products:
            data['products_count'] = self.products.count()
        
        return data
    
    def __repr__(self):
        return f'<Category {self.name}>'