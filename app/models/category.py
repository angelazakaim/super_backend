from datetime import datetime
from app.extensions import db
import re

class Category(db.Model):
    """Product category model."""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Self-referential relationship for hierarchical categories
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]), cascade='all, delete-orphan')
    
    # Products in this category
    products = db.relationship('Product', backref='category', lazy='dynamic')
    
    @property
    def slug(self):
        """Generate slug from category name."""
        if not self.name:
            return ''
        slug = self.name.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s_-]+', '-', slug)
        slug = slug.strip('-')
        return slug
    
    def to_dict(self, include_children=False, include_products=False):
        """Convert category to dictionary."""
        data = {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'parent_id': self.parent_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_children:
            data['children'] = [child.to_dict() for child in self.children if child.is_active]
        
        if include_products:
            data['products_count'] = self.products.filter_by(is_active=True).count()
        
        return data
    
    def __repr__(self):
        return f'<Category {self.name}>'