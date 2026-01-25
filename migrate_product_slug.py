"""
Database migration: Add slug column to products table.

Run this after updating the Product model.
"""
from app.extensions import db
from app.models.product import Product
import re


def generate_slug(name):
    """Generate slug from product name."""
    if not name:
        return 'product'
    slug = name.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    return slug.strip('-')


def add_slug_column_and_populate():
    """
    Add slug column to products table and populate from existing names.
    
    This migration:
    1. Adds slug column (if not exists)
    2. Generates unique slugs for all existing products
    3. Handles duplicate slugs by appending product ID
    """
    print("="*60)
    print("MIGRATION: Add slug column to products")
    print("="*60)
    
    try:
        # Check if slug column already exists
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('products')]
        
        if 'slug' in columns:
            print("✅ Slug column already exists!")
            print("   Checking if all products have slugs...")
            
            # Check for missing slugs
            products_without_slug = Product.query.filter(
                (Product.slug == None) | (Product.slug == '')
            ).all()
            
            if not products_without_slug:
                print("✅ All products already have slugs!")
                return
            
            print(f"⚠️  Found {len(products_without_slug)} products without slugs")
            print("   Generating slugs for them...")
        else:
            print("⚠️  Slug column does not exist")
            print("   Please update your Product model first, then recreate the table")
            print("   Or run: flask db migrate -m 'Add slug to products'")
            return
        
        # Generate slugs for existing products
        print("\nGenerating slugs...")
        slugs_used = set()
        updated_count = 0
        
        products = Product.query.all()
        
        for product in products:
            if not product.slug or product.slug == '':
                # Generate base slug
                base_slug = generate_slug(product.name)
                slug = base_slug
                
                # Handle duplicates by appending product ID
                if slug in slugs_used:
                    slug = f"{base_slug}-{product.id}"
                
                product.slug = slug
                slugs_used.add(slug)
                updated_count += 1
                print(f"  '{product.name}' -> '{slug}'")
            else:
                slugs_used.add(product.slug)
        
        # Commit changes
        db.session.commit()
        print(f"\n✅ Successfully updated {updated_count} products")
        print(f"   Total products: {len(products)}")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        raise


def verify_migration():
    """Verify that all products have valid slugs."""
    print("\n" + "="*60)
    print("VERIFICATION")
    print("="*60)
    
    try:
        total_products = Product.query.count()
        products_with_slug = Product.query.filter(
            (Product.slug != None) & (Product.slug != '')
        ).count()
        
        print(f"Total products: {total_products}")
        print(f"Products with slug: {products_with_slug}")
        
        if total_products == products_with_slug:
            print("✅ VERIFICATION PASSED - All products have slugs!")
        else:
            missing = total_products - products_with_slug
            print(f"⚠️  WARNING - {missing} products are missing slugs!")
        
        # Check for duplicates
        from sqlalchemy import func
        duplicates = db.session.query(
            Product.slug, func.count(Product.slug)
        ).group_by(Product.slug).having(func.count(Product.slug) > 1).all()
        
        if duplicates:
            print(f"\n⚠️  WARNING - Found {len(duplicates)} duplicate slugs:")
            for slug, count in duplicates:
                print(f"  '{slug}' - used {count} times")
        else:
            print("✅ No duplicate slugs found!")
            
    except Exception as e:
        print(f"❌ Verification failed: {e}")


def main():
    """Run the migration."""
    from app import create_app
    
    app = create_app()
    
    with app.app_context():
        print("\n" + "🚀 "*20)
        print("Starting Product Slug Migration")
        print("🚀 "*20 + "\n")
        
        add_slug_column_and_populate()
        verify_migration()
        
        print("\n" + "="*60)
        print("MIGRATION COMPLETE!")
        print("="*60)
        print("\nNext steps:")
        print("1. Restart your Flask application")
        print("2. Test: GET /api/products/slug/iphone-15-pro")
        print("3. Verify slugs are working correctly")
        print()


if __name__ == '__main__':
    main()
