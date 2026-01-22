"""
Script to seed the database with sample data for development and testing.

Development: python seed_data.py
Production: Set FLASK_ENV=production before running
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
        
        # Admin
        admin = UserRepository.create(
            email='admin@example.com',
            username='admin',
            password='Admin123!',
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
        print(f"   ✅ Admin: {admin.email}")

        # Regular Customer
        customer = UserRepository.create(
            email='customer@example.com',
            username='customer1',
            password='Customer123!',
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
        print(f"   ✅ Customer: {customer.email}")

        # Manager
        manager_user = UserRepository.create(
            email='manager@supermarket.com',
            username='manager1',
            password='Manager123!',
            role='manager'
        )
        manager_emp = Employee(
            user_id=manager_user.id,
            employee_id='EMP001',
            salary=5500.0,
            hire_date=datetime.utcnow()
        )
        db.session.add(manager_emp)
        print(f"   ✅ Manager: {manager_user.username}")

        # Cashier
        cashier_user = UserRepository.create(
            email='cashier@supermarket.com',
            username='cashier1',
            password='Cashier123!',
            role='cashier'
        )
        cashier_emp = Employee(
            user_id=cashier_user.id,
            employee_id='EMP002',
            salary=3200.0,
            shift_start=time(8, 0),
            shift_end=time(16, 0)
        )
        db.session.add(cashier_emp)
        print(f"   ✅ Cashier: {cashier_user.username}\n")

        # 2. Create Categories
        print("📁 Creating Categories...")
        categories_data = [
            {'name': 'Electronics', 'description': 'Electronic devices and gadgets'},
            {'name': 'Dairy', 'description': 'Milk, cheese, yogurt, and eggs'},
            {'name': 'Produce', 'description': 'Fresh fruits and vegetables'},
            {'name': 'Bakery', 'description': 'Fresh bread, pastries, and baked goods'},
            {'name': 'Beverages', 'description': 'Drinks, juices, and soft drinks'},
            {'name': 'Meat & Seafood', 'description': 'Fresh and frozen meat and seafood'},
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
            # Dairy
            {
                'name': 'Whole Milk 1L',             
                'description': 'Fresh farm whole milk, rich and creamy',
                'price': Decimal('5.99'),
                'sku': 'DAI-MILK-001',
                'stock_quantity': 100,
                'category_id': created_categories['Dairy'].id,
                'is_featured': True,
                'weight': Decimal('1.03')
            },
            {
                'name': 'Greek Yogurt 500g',
                'description': 'Thick and creamy Greek-style yogurt',
                'price': Decimal('7.50'),
                'sku': 'DAI-YOG-001',
                'stock_quantity': 75,
                'category_id': created_categories['Dairy'].id,
                'weight': Decimal('0.5')
            },
            {
                'name': 'Cheddar Cheese 200g',
                'description': 'Aged cheddar cheese, sharp flavor',
                'price': Decimal('8.99'),
                'compare_price': Decimal('10.99'),
                'sku': 'DAI-CHE-001',
                'stock_quantity': 50,
                'category_id': created_categories['Dairy'].id,
                'is_featured': True,
                'weight': Decimal('0.2')
            },
            # Produce
            {
                'name': 'Organic Bananas',
                'description': 'Fresh organic bananas, sold by kg',
                'price': Decimal('2.50'),
                'sku': 'PRO-BAN-001',
                'stock_quantity': 150,
                'category_id': created_categories['Produce'].id
            },
            {
                'name': 'Fresh Tomatoes',
                'description': 'Ripe red tomatoes, perfect for salads',
                'price': Decimal('4.99'),
                'sku': 'PRO-TOM-001',
                'stock_quantity': 80,
                'category_id': created_categories['Produce'].id
            },
            {
                'name': 'Baby Spinach 250g',
                'description': 'Fresh baby spinach leaves',
                'price': Decimal('3.99'),
                'sku': 'PRO-SPI-001',
                'stock_quantity': 60,
                'category_id': created_categories['Produce'].id,
                'weight': Decimal('0.25')
            },
            # Bakery
            {
                'name': 'Whole Wheat Bread',
                'description': 'Freshly baked whole wheat bread loaf',
                'price': Decimal('4.50'),
                'sku': 'BAK-BRE-001',
                'stock_quantity': 40,
                'category_id': created_categories['Bakery'].id,
                'is_featured': True
            },
            {
                'name': 'Croissants 6-pack',
                'description': 'Buttery, flaky French croissants',
                'price': Decimal('9.99'),
                'compare_price': Decimal('11.99'),
                'sku': 'BAK-CRO-001',
                'stock_quantity': 30,
                'category_id': created_categories['Bakery'].id
            },
            # Beverages
            {
                'name': 'Orange Juice 1L',
                'description': '100% pure orange juice, no added sugar',
                'price': Decimal('6.99'),
                'sku': 'BEV-JUI-001',
                'stock_quantity': 90,
                'category_id': created_categories['Beverages'].id,
                'weight': Decimal('1.05')
            },
            {
                'name': 'Sparkling Water 500ml',
                'description': 'Refreshing sparkling mineral water',
                'price': Decimal('2.99'),
                'sku': 'BEV-WAT-001',
                'stock_quantity': 200,
                'category_id': created_categories['Beverages'].id,
                'weight': Decimal('0.5')
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
        # print("📊 Summary:")
        # print(f"   • Users: {UserRepository.get_all().count()}")
        # print(f"   • Categories: {CategoryRepository.get_all().count()}")
        # print(f"   • Products: {ProductRepository.get_all().count()}")
        # print()
        # .count() → SQLAlchemy Query
        # .paginate() → Pagination object
        # Pagination uses .total, not .count()
        print("📊 Summary:")
        print(f"   • Users: {UserRepository.get_all().total}")
        print(f"   • Categories: {CategoryRepository.get_all()}")
        print(f"   • Products: {ProductRepository.get_all()}")

        
        # Print login credentials
        print("🔐 Login Credentials:")
        print("   Admin:    admin@example.com / Admin123!")
        print("   Customer: customer@example.com / Customer123!")
        print("   Manager:  manager@supermarket.com / Manager123!")
        print("   Cashier:  cashier@supermarket.com / Cashier123!")
        print()

if __name__ == '__main__':
    seed_database()