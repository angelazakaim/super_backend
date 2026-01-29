"""Enhanced seed data for demonstrating pagination behavior."""
import random
from datetime import datetime, timezone, timedelta
from decimal import Decimal

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.customer import Customer
from app.models.employee import Employee
from app.models.category import Category
from app.models.product import Product
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.enums import UserRole, OrderStatus, PaymentStatus, PaymentMethod


def clear_data():
    """Clear all existing data from the database."""
    print("🗑️  Clearing existing data...")
    
    # Order matters due to foreign key constraints
    OrderItem.query.delete()
    Order.query.delete()
    CartItem.query.delete()
    Cart.query.delete()
    Product.query.delete()
    Category.query.delete()
    Customer.query.delete()
    Employee.query.delete()
    User.query.delete()
    
    db.session.commit()
    print("✅ All data cleared!")


def create_users():
    """Create many test users to demonstrate pagination."""
    print("\n👥 Creating users for pagination testing...")
    
    users = []
    
    # 1. Admin User
    admin = User(
        email='admin@ecommerce.com',
        username='admin',
        role=UserRole.ADMIN.value,
        is_active=True
    )
    admin.set_password('Admin123!')
    users.append(admin)
    
    # 2. Manager User
    manager = User(
        email='manager@ecommerce.com',
        username='manager',
        role=UserRole.MANAGER.value,
        is_active=True
    )
    manager.set_password('Manager123!')
    users.append(manager)
    
    # 3. Cashier User
    cashier = User(
        email='cashier@ecommerce.com',
        username='cashier',
        role=UserRole.CASHIER.value,
        is_active=True
    )
    cashier.set_password('Cashier123!')
    users.append(cashier)
    
    # 4-53. Create 50 Customer Users (to demonstrate pagination!)
    print("  📊 Creating 50 customers for pagination testing...")
    first_names = ['John', 'Jane', 'Bob', 'Alice', 'Charlie', 'Diana', 'Eve', 'Frank', 
                   'Grace', 'Henry', 'Ivy', 'Jack', 'Kate', 'Leo', 'Mary', 'Nick', 
                   'Olivia', 'Paul', 'Quinn', 'Rachel', 'Sam', 'Tina', 'Uma', 'Victor', 'Wendy']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 
                  'Davis', 'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 
                  'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin']
    
    for i in range(1, 51):  # 50 customers
        first = random.choice(first_names)
        last = random.choice(last_names)
        customer_user = User(
            email=f'customer{i}@email.com',
            username=f'customer{i}',
            role=UserRole.CUSTOMER.value,
            is_active=True
        )
        customer_user.set_password('Customer123!')
        users.append(customer_user)
    
    db.session.add_all(users)
    db.session.commit()
    
    print(f"✅ Created {len(users)} users (3 staff + 50 customers)")
    return users


def create_employee_profiles(users):
    """Create employee profiles."""
    print("\n👔 Creating employee profiles...")
    
    employees = []
    manager = next(u for u in users if u.role == UserRole.MANAGER.value)
    cashier = next(u for u in users if u.role == UserRole.CASHIER.value)
    
    manager_profile = Employee(
        user_id=manager.id,
        first_name='Sarah',
        last_name='Johnson',
        phone='555-0201',
        employee_id='MGR-001',
        hire_date=datetime.now(timezone.utc) - timedelta(days=730),
        salary=75000.00
    )
    employees.append(manager_profile)
    
    cashier_profile = Employee(
        user_id=cashier.id,
        first_name='Mike',
        last_name='Anderson',
        phone='555-0202',
        employee_id='CSH-001',
        hire_date=datetime.now(timezone.utc) - timedelta(days=365),
        salary=45000.00
    )
    employees.append(cashier_profile)
    
    db.session.add_all(employees)
    db.session.commit()
    
    print(f"✅ Created {len(employees)} employee profiles")
    return employees


def create_customer_profiles(users):
    """Create many customer profiles for pagination."""
    print("\n🛍️  Creating 50 customer profiles...")
    
    customers = []
    customer_users = [u for u in users if u.role == UserRole.CUSTOMER.value]
    
    cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 
              'San Antonio', 'San Diego', 'Dallas', 'San Jose']
    states = ['NY', 'CA', 'IL', 'TX', 'AZ', 'PA', 'TX', 'CA', 'TX', 'CA']
    
    for i, user in enumerate(customer_users):
        city_idx = i % len(cities)
        customer = Customer(
            user_id=user.id,
            first_name=f'Customer{i+1}',
            last_name='User',
            phone=f'555-{1000+i:04d}',
            address_line1=f'{100+i} Main St',
            city=cities[city_idx],
            state=states[city_idx],
            postal_code=f'{10000+i:05d}',
            country='USA'
        )
        customers.append(customer)
    
    db.session.add_all(customers)
    db.session.commit()
    
    print(f"✅ Created {len(customers)} customer profiles")
    return customers


def create_categories():
    """Create product categories."""
    print("\n📂 Creating categories...")
    
    categories = []
    
    # Root categories
    electronics = Category(name='Electronics', description='Electronic devices and accessories', is_active=True)
    clothing = Category(name='Clothing', description='Apparel and fashion', is_active=True)
    home = Category(name='Home & Garden', description='Home improvement', is_active=True)
    sports = Category(name='Sports', description='Sports equipment', is_active=True)
    books = Category(name='Books', description='Books and literature', is_active=True)
    toys = Category(name='Toys', description='Toys and games', is_active=True)
    beauty = Category(name='Beauty', description='Beauty and personal care', is_active=True)
    automotive = Category(name='Automotive', description='Car parts and accessories', is_active=True)
    
    categories.extend([electronics, clothing, home, sports, books, toys, beauty, automotive])
    
    db.session.add_all(categories)
    db.session.commit()
    
    # Subcategories
    computers = Category(name='Computers', parent_id=electronics.id, is_active=True)
    phones = Category(name='Smartphones', parent_id=electronics.id, is_active=True)
    audio = Category(name='Audio', parent_id=electronics.id, is_active=True)
    mens = Category(name="Men's Clothing", parent_id=clothing.id, is_active=True)
    womens = Category(name="Women's Clothing", parent_id=clothing.id, is_active=True)
    
    subcategories = [computers, phones, audio, mens, womens]
    db.session.add_all(subcategories)
    db.session.commit()
    
    all_categories = categories + subcategories
    print(f"✅ Created {len(all_categories)} categories")
    return all_categories


def create_many_products(categories):
    
    
    """Create 100+ products to demonstrate pagination."""
    print("\n📦 Creating 150 products for pagination testing...")
    
    products = []
    
    # Get leaf categories (ones that can have products)
    # leaf_categories = [c for c in categories if not c.children]
    leaf_categories = [c for c in categories if c.children.count() == 0]
    
    # Product name templates
    product_templates = [
        ('Laptop', 'High-performance laptop', 800, 1500),
        ('Phone', 'Smartphone with camera', 400, 1200),
        ('Headphones', 'Wireless headphones', 50, 400),
        ('Mouse', 'Ergonomic mouse', 15, 100),
        ('Keyboard', 'Mechanical keyboard', 60, 200),
        ('Monitor', 'LED monitor', 150, 800),
        ('Tablet', 'Tablet device', 200, 900),
        ('Speaker', 'Bluetooth speaker', 30, 300),
        ('Camera', 'Digital camera', 300, 2000),
        ('Smartwatch', 'Fitness smartwatch', 100, 500),
        ('T-Shirt', 'Cotton t-shirt', 15, 50),
        ('Jeans', 'Denim jeans', 40, 150),
        ('Shoes', 'Running shoes', 50, 200),
        ('Jacket', 'Winter jacket', 80, 300),
        ('Dress', 'Summer dress', 40, 200),
        ('Chair', 'Office chair', 100, 500),
        ('Desk', 'Standing desk', 200, 800),
        ('Lamp', 'LED desk lamp', 25, 150),
        ('Bike', 'Mountain bike', 300, 2000),
        ('Yoga Mat', 'Exercise mat', 20, 80),
    ]
    
    brands = ['Premium', 'Elite', 'Pro', 'Ultra', 'Max', 'Plus', 'Lite', 'Standard']
    
    # Create 150 products
    for i in range(150):
        template = product_templates[i % len(product_templates)]
        brand = brands[i % len(brands)]
        category = leaf_categories[i % len(leaf_categories)]
        
        name = f'{brand} {template[0]} {i+1}'
        description = f'{template[1]} - Model {i+1}'
        min_price, max_price = template[2], template[3]
        price = Decimal(str(random.uniform(min_price, max_price)))
        
        # Some products have compare_price (was $X, now $Y)
        compare_price = None
        if random.random() > 0.7:  # 30% have compare price
            compare_price = price * Decimal('1.3')
        
        # Stock varies
        stock = random.choice([0, 5, 10, 25, 50, 100, 200, 500])
        
        # Some products are featured
        is_featured = random.random() > 0.85  # 15% featured
        
        # Some products are inactive
        is_active = random.random() > 0.1  # 90% active
        
        # Created at various times (for sorting tests)
        days_ago = random.randint(0, 365)
        created_at = datetime.now(timezone.utc) - timedelta(days=days_ago)
        
        product = Product(
            name=name,
            description=description,
            price=round(price, 2),
            compare_price=round(compare_price, 2) if compare_price else None,
            sku=f'SKU-{i+1:05d}',
            barcode=f'{1234567890000 + i}',
            stock_quantity=stock,
            category_id=category.id,
            weight=Decimal(str(random.uniform(0.1, 10.0))),
            is_active=is_active,
            is_featured=is_featured,
            
        )
        products.append(product)
    
    db.session.add_all(products)
    db.session.commit()
    
    print(f"✅ Created {len(products)} products")
    print(f"   - Active: {sum(1 for p in products if p.is_active)}")
    print(f"   - Featured: {sum(1 for p in products if p.is_featured)}")
    print(f"   - In stock: {sum(1 for p in products if p.stock_quantity > 0)}")
    print(f"   - Low stock (<10): {sum(1 for p in products if 0 < p.stock_quantity < 10)}")
    print(f"   - Out of stock: {sum(1 for p in products if p.stock_quantity == 0)}")
    
    return products


def create_many_orders(customers, products):
    """Create 100+ orders to demonstrate pagination."""
    print("\n📋 Creating 100 orders for pagination testing...")
    
    orders = []
    order_items = []
    order_number_counter = 1000
    
    # Create 100 orders
    for i in range(100):
        order_number_counter += 1
        customer = random.choice(customers)
        
        # Random order status (weighted)
        status_choices = [
            OrderStatus.DELIVERED.value,  # 40%
            OrderStatus.DELIVERED.value,
            OrderStatus.SHIPPED.value,     # 20%
            OrderStatus.PROCESSING.value,  # 15%
            OrderStatus.CONFIRMED.value,   # 15%
            OrderStatus.PENDING.value,     # 5%
            OrderStatus.CANCELLED.value,   # 5%
        ]
        status = random.choice(status_choices)
        
        # Payment status
        if status == OrderStatus.CANCELLED.value:
            payment_status = PaymentStatus.REFUNDED.value
        elif status in [OrderStatus.PENDING.value, OrderStatus.CONFIRMED.value]:
            payment_status = random.choice([PaymentStatus.PENDING.value, PaymentStatus.PAID.value])
        else:
            payment_status = PaymentStatus.PAID.value
        
        # Order date
        if status == OrderStatus.DELIVERED.value:
            days_ago = random.randint(7, 90)
        elif status == OrderStatus.SHIPPED.value:
            days_ago = random.randint(3, 7)
        elif status == OrderStatus.PROCESSING.value:
            days_ago = random.randint(1, 3)
        else:
            days_ago = random.randint(0, 2)
        
        created_at = datetime.now(timezone.utc) - timedelta(days=days_ago)
        
        # Select products
        num_products = random.randint(1, 5)
        order_products = random.sample(products, min(num_products, len(products)))
        
        # Calculate totals
        subtotal = Decimal('0.00')
        for product in order_products:
            quantity = random.randint(1, 3)
            subtotal += product.price * quantity
        
        tax = subtotal * Decimal('0.1')
        shipping_cost = Decimal('10.00') if subtotal < 100 else Decimal('0.00')
        total = subtotal + tax + shipping_cost
        
        # Create order
        order = Order(
            order_number=f'ORD-{order_number_counter:06d}',
            customer_id=customer.id,
            status=status,
            payment_status=payment_status,
            payment_method=random.choice(PaymentMethod.values()),
            subtotal=subtotal,
            tax=tax,
            shipping_cost=shipping_cost,
            total=total,
            shipping_address_line1=customer.address_line1,
            shipping_city=customer.city,
            shipping_state=customer.state,
            shipping_postal_code=customer.postal_code,
            shipping_country=customer.country,
            created_at=created_at
        )
        
        # Set status timestamps
        if status in [OrderStatus.CONFIRMED.value, OrderStatus.PROCESSING.value, 
                      OrderStatus.SHIPPED.value, OrderStatus.DELIVERED.value]:
            order.confirmed_at = created_at + timedelta(hours=2)
        
        if status in [OrderStatus.SHIPPED.value, OrderStatus.DELIVERED.value]:
            order.shipped_at = created_at + timedelta(days=2)
        
        if status == OrderStatus.DELIVERED.value:
            order.delivered_at = created_at + timedelta(days=5)
        
        orders.append(order)
        db.session.add(order)
        db.session.commit()
        
        # Create order items
        for product in order_products:
            quantity = random.randint(1, 3)
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                product_sku=product.sku,
                unit_price=product.price,
                quantity=quantity
            )
            order_items.append(order_item)
            db.session.add(order_item)
        
        db.session.commit()
    
    print(f"✅ Created {len(orders)} orders with {len(order_items)} items")
    
    # Status breakdown
    status_counts = {}
    for order in orders:
        status_counts[order.status] = status_counts.get(order.status, 0) + 1
    
    print("\n   📊 Order Status Distribution:")
    for status, count in sorted(status_counts.items()):
        print(f"      - {status.capitalize()}: {count}")
    
    return orders


def seed_database():
    """Main function to seed database with pagination-friendly data."""
    print("=" * 70)
    print("🌱 SEEDING DATABASE FOR PAGINATION TESTING")
    print("=" * 70)
    
    clear_data()
    
    users = create_users()
    employees = create_employee_profiles(users)
    customers = create_customer_profiles(users)
    categories = create_categories()
    products = create_many_products(categories)
    orders = create_many_orders(customers, products)
    
    print("\n" + "=" * 70)
    print("✅ DATABASE SEEDING COMPLETE!")
    print("=" * 70)
    print("\n📊 Final Summary:")
    print(f"   Users: {User.query.count()}")
    print(f"   Customers: {Customer.query.count()}")
    print(f"   Employees: {Employee.query.count()}")
    print(f"   Categories: {Category.query.count()}")
    print(f"   Products: {Product.query.count()}")
    print(f"   Orders: {Order.query.count()}")
    print(f"   Order Items: {OrderItem.query.count()}")
    
    print("\n🔑 Test Accounts:")
    print("   Admin:    admin@ecommerce.com / Admin123!")
    print("   Manager:  manager@ecommerce.com / Manager123!")
    print("   Cashier:  cashier@ecommerce.com / Cashier123!")
    print("   Customer: customer1@email.com / Customer123!")
    print("   Customer: customer2@email.com / Customer123!")
    print("   ... (50 customers total)")
    
    print("\n📄 Pagination Testing Guide:")
    print("=" * 70)
    print("\n1️⃣  TEST PRODUCT PAGINATION (150 products):")
    print("   GET /api/products?page=1&per_page=20")
    print("   → Should return products 1-20 of 150")
    print("   → has_next: true, has_prev: false, pages: 8")
    print()
    print("   GET /api/products?page=2&per_page=20")
    print("   → Should return products 21-40 of 150")
    print("   → has_next: true, has_prev: true")
    print()
    print("   GET /api/products?page=8&per_page=20")
    print("   → Should return products 141-150 (last 10 items)")
    print("   → has_next: false, has_prev: true")
    print()
    print("2️⃣  TEST ORDER PAGINATION (100 orders):")
    print("   GET /api/orders?page=1&per_page=10")
    print("   → Should return 10 orders, pages: 10")
    print()
    print("   GET /api/orders?page=5&per_page=10")
    print("   → Should return orders 41-50")
    print()
    print("3️⃣  TEST USER PAGINATION (53 users):")
    print("   GET /api/users?page=1&per_page=25")
    print("   → Should return 25 users, pages: 3")
    print()
    print("4️⃣  TEST DIFFERENT PAGE SIZES:")
    print("   GET /api/products?page=1&per_page=10  (15 pages)")
    print("   GET /api/products?page=1&per_page=50  (3 pages)")
    print("   GET /api/products?page=1&per_page=100 (2 pages)")
    print()
    print("5️⃣  TEST FILTERED PAGINATION:")
    print("   GET /api/products?page=1&per_page=20&category_id=1")
    print("   GET /api/products?page=1&per_page=20&search=laptop")
    print("   GET /api/products?page=1&per_page=20&featured=true")
    print()
    print("6️⃣  TEST EDGE CASES:")
    print("   GET /api/products?page=999&per_page=20")
    print("   → Should return empty list (page doesn't exist)")
    print()
    print("   GET /api/products?page=1&per_page=1000")
    print("   → Should be capped at max (100 items)")
    
    print("\n" + "=" * 70)
    print("🎯 Try these in Postman to see pagination in action!")
    print("=" * 70)


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_database()
