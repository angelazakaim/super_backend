"""
Script to seed the database with sample data for development and testing.

USAGE:
    Development: python seed_data.py
    Production:  Set FLASK_ENV=production before running

IMPORTANT:
    - This will DROP ALL existing data
    - Creates test users with roles: admin, manager, cashier, customer
    - Creates sample products with categories
"""
from decimal import Decimal
from datetime import datetime, time
from app import create_app
from app.extensions import db
from app.repositories.user_repository import UserRepository
from app.repositories.customer_repository import CustomerRepository
from app.repositories.category_repository import CategoryRepository
from app.repositories.product_repository import ProductRepository
from app.models.employee import Employee 
import os

def seed_database():
    """Seed database with sample data."""
    env = os.getenv('FLASK_ENV', 'development')
    app = create_app(env)
    
    with app.app_context():
        print(f"\n{'='*60}")
        print(f"  Seeding Database - Environment: {env.upper()}")
        print(f"{'='*60}\n")
        
        # Warning for production
        if env == 'production':
            confirm = input("⚠️  WARNING: You're about to seed PRODUCTION database. Type 'YES' to continue: ")
            if confirm != 'YES':
                print("❌ Seeding cancelled.")
                return
        
        print("🗑️  Cleaning old data...")
        db.drop_all()
        db.create_all()
        
        print("🌱 Seeding database...\n")
        
        # 1. Create Users with different roles
        print("👥 Creating Users...")
        
        # Admin User
        admin = UserRepository.create(
            email='admin@supermarket.com',
            username='admin',
            password='admin123',  # Simple password for testing
            role='admin'
        )
        CustomerRepository.create(
            user_id=admin.id, 
            first_name='Admin', 
            last_name='User',
            phone='+1-555-0100',
            address_line1='123 Admin Street',
            city='New York',
            state='NY',
            postal_code='10001',
            country='USA'
        )
        print(f"   ✅ Admin: {admin.email} / admin123")

        # Manager User (Can add/edit/delete products)
        manager_user = UserRepository.create(
            email='manager@test.com',  # Matches frontend quick login
            username='manager',
            password='manager123',
            role='manager'
        )
        manager_emp = Employee(
            user_id=manager_user.id,
            employee_id='MGR001',
            salary=5500.0,
            hire_date=datetime.utcnow()
        )
        db.session.add(manager_emp)
        print(f"   ✅ Manager: {manager_user.email} / manager123")

        # Cashier User
        cashier_user = UserRepository.create(
            email='cashier@supermarket.com',
            username='cashier',
            password='cashier123',
            role='cashier'
        )
        cashier_emp = Employee(
            user_id=cashier_user.id,
            employee_id='CSH001',
            salary=3200.0,
            shift_start=time(8, 0),
            shift_end=time(16, 0),
            hire_date=datetime.utcnow()
        )
        db.session.add(cashier_emp)
        print(f"   ✅ Cashier: {cashier_user.email} / cashier123")

        # Regular Customer User
        customer = UserRepository.create(
            email='customer@test.com',  # Matches frontend quick login
            username='customer',
            password='customer123',
            role='customer'
        )
        CustomerRepository.create(
            user_id=customer.id,
            first_name='John',
            last_name='Doe',
            phone='+1-555-0101',
            address_line1='456 Customer Ave',
            city='Los Angeles',
            state='CA',
            postal_code='90001',
            country='USA'
        )
        print(f"   ✅ Customer: {customer.email} / customer123\n")

        # 2. Create Categories
        print("📁 Creating Categories...")
        categories_data = [
            {'name': 'Fruits & Vegetables', 'description': 'Fresh produce, fruits, and vegetables'},
            {'name': 'Beverages', 'description': 'Drinks, juices, and soft drinks'},
            {'name': 'Bakery', 'description': 'Fresh bread, pastries, and baked goods'},
            {'name': 'Dairy', 'description': 'Milk, cheese, yogurt, and eggs'},
            {'name': 'Meat', 'description': 'Fresh and frozen meat'},
            {'name': 'Snacks', 'description': 'Chips, cookies, and snacks'},
        ]
        
        created_categories = {}
        for cat_data in categories_data:
            cat = CategoryRepository.create(**cat_data)
            created_categories[cat.name] = cat
            print(f"   ✅ {cat.name}")
        print()

        # 3. Create Products
        print("📦 Creating Products...")
        products = [
            # Fruits & Vegetables
            {
                'name': 'Fresh Apples',
                'description': 'Crisp and juicy apples, perfect for snacking or baking. Grown locally with care.',
                'price': Decimal('1.99'),
                'compare_price': Decimal('2.49'),
                'sku': 'APPL-001',
                'stock_quantity': 100,
                'category_id': created_categories['Fruits & Vegetables'].id,
                'is_featured': True,
                'weight': Decimal('0.5'),
                'dimensions': '3x3x3 inches',
                'image_url': 'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=400'
            },
            {
                'name': 'Organic Bananas',
                'description': 'Fresh organic bananas, naturally sweet and nutritious.',
                'price': Decimal('0.99'),
                'sku': 'BANA-001',
                'stock_quantity': 150,
                'category_id': created_categories['Fruits & Vegetables'].id,
                'weight': Decimal('0.6'),
                'image_url': 'https://images.unsplash.com/photo-1571771894821-ce9b6c11b08e?w=400'
            },
            {
                'name': 'Fresh Tomatoes',
                'description': 'Ripe red tomatoes, perfect for salads and cooking.',
                'price': Decimal('2.99'),
                'sku': 'TOMA-001',
                'stock_quantity': 80,
                'category_id': created_categories['Fruits & Vegetables'].id,
                'weight': Decimal('0.5'),
                'image_url': 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=400'
            },
            {
                'name': 'Baby Spinach 250g',
                'description': 'Fresh baby spinach leaves, great for salads.',
                'price': Decimal('3.99'),
                'sku': 'SPIN-001',
                'stock_quantity': 60,
                'category_id': created_categories['Fruits & Vegetables'].id,
                'is_featured': True,
                'weight': Decimal('0.25'),
                'image_url': 'https://images.unsplash.com/photo-1576045057995-568f588f82fb?w=400'
            },
            
            # Beverages
            {
                'name': 'Orange Juice 1L',
                'description': '100% pure orange juice, no added sugar. Freshly squeezed taste.',
                'price': Decimal('2.49'),
                'sku': 'ORJC-001',
                'stock_quantity': 90,
                'category_id': created_categories['Beverages'].id,
                'is_featured': True,
                'weight': Decimal('1.05'),
                'image_url': 'https://images.unsplash.com/photo-1600271886742-f049cd451bba?w=400'
            },
            {
                'name': 'Sparkling Water 500ml',
                'description': 'Refreshing sparkling mineral water.',
                'price': Decimal('1.99'),
                'sku': 'SPWA-001',
                'stock_quantity': 200,
                'category_id': created_categories['Beverages'].id,
                'weight': Decimal('0.5'),
                'image_url': 'https://images.unsplash.com/photo-1523362628745-0c100150b504?w=400'
            },
            
            # Bakery
            {
                'name': 'Whole Wheat Bread',
                'description': 'Freshly baked whole wheat bread loaf. Soft and healthy.',
                'price': Decimal('3.99'),
                'compare_price': Decimal('4.99'),
                'sku': 'BREA-001',
                'stock_quantity': 45,
                'category_id': created_categories['Bakery'].id,
                'is_featured': True,
                'dimensions': '12x5x5 inches',
                'image_url': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400'
            },
            {
                'name': 'Croissants 6-pack',
                'description': 'Buttery, flaky French croissants. Perfect for breakfast.',
                'price': Decimal('6.99'),
                'compare_price': Decimal('8.99'),
                'sku': 'CROI-001',
                'stock_quantity': 30,
                'category_id': created_categories['Bakery'].id,
                'image_url': 'https://images.unsplash.com/photo-1555507036-ab1f4038808a?w=400'
            },
            
            # Dairy
            {
                'name': 'Whole Milk 1L',
                'description': 'Fresh farm whole milk, rich and creamy.',
                'price': Decimal('3.49'),
                'sku': 'MILK-001',
                'stock_quantity': 100,
                'category_id': created_categories['Dairy'].id,
                'weight': Decimal('1.03'),
                'image_url': 'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400'
            },
            {
                'name': 'Greek Yogurt 500g',
                'description': 'Thick and creamy Greek-style yogurt. High in protein.',
                'price': Decimal('4.99'),
                'sku': 'YOGU-001',
                'stock_quantity': 75,
                'category_id': created_categories['Dairy'].id,
                'weight': Decimal('0.5'),
                'image_url': 'https://images.unsplash.com/photo-1488477181946-6428a0291777?w=400'
            },
            {
                'name': 'Cheddar Cheese 200g',
                'description': 'Aged cheddar cheese, sharp flavor. Great for sandwiches.',
                'price': Decimal('5.99'),
                'compare_price': Decimal('7.99'),
                'sku': 'CHED-001',
                'stock_quantity': 50,
                'category_id': created_categories['Dairy'].id,
                'is_featured': True,
                'weight': Decimal('0.2'),
                'image_url': 'https://images.unsplash.com/photo-1618164436241-4473940d1f5c?w=400'
            },
        ]
        
        for prod_data in products:
            prod = ProductRepository.create(**prod_data)
            featured = " ⭐" if prod.is_featured else ""
            discount = f" (💰 {prod.discount_percentage}% off)" if prod.discount_percentage > 0 else ""
            print(f"   ✅ {prod.name} - ${prod.price}{featured}{discount}")
        
        db.session.commit()
        
        print(f"\n{'='*60}")
        print("✅ Database seeding completed successfully!")
        print(f"{'='*60}\n")
        
        # Print summary
        print("📊 Summary:")
        print(f"   • Users: 4 (1 admin, 1 manager, 1 cashier, 1 customer)")
        print(f"   • Categories: {len(categories_data)}")
        print(f"   • Products: {len(products)}")
        print()
        
        # Print login credentials for frontend testing
        print("🔐 Frontend Test Credentials:")
        print("="*60)
        print("👔 MANAGER (Can Add/Edit/Delete Products):")
        print("   Email:    manager@test.com")
        print("   Password: manager123")
        print()
        print("👤 CUSTOMER (View Only):")
        print("   Email:    customer@test.com")
        print("   Password: customer123")
        print()
        print("👨‍💼 ADMIN (Full Access):")
        print("   Email:    admin@supermarket.com")
        print("   Password: admin123")
        print()
        print("💵 CASHIER (Limited Access):")
        print("   Email:    cashier@supermarket.com")
        print("   Password: cashier123")
        print("="*60)
        print()

if __name__ == '__main__':
    seed_database()
