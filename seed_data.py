"""
Seed data script for E-Commerce 4-Role API
Creates sample data for all models with complete address information.
"""

from app import create_app, db
from app.models.user import User
from app.models.customer import Customer
from app.models.employee import Employee
from app.models.category import Category
from app.models.product import Product
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.order import Order
from app.models.order_item import OrderItem
from datetime import datetime, timedelta
import random

def clear_data():
    """Clear all existing data from database safely."""
    print("🗑️  Clearing existing data...")
    
    # Check if tables exist first
    inspector = db.inspect(db.engine)
    existing_tables = inspector.get_table_names()
    
    # Order matters due to foreign key constraints
    # Only delete from tables that exist
    if 'order_items' in existing_tables:
        db.session.query(OrderItem).delete()
    if 'orders' in existing_tables:
        db.session.query(Order).delete()
    if 'cart_items' in existing_tables:
        db.session.query(CartItem).delete()
    if 'carts' in existing_tables:
        db.session.query(Cart).delete()
    if 'products' in existing_tables:
        db.session.query(Product).delete()
    if 'categories' in existing_tables:
        db.session.query(Category).delete()
    if 'employees' in existing_tables:
        db.session.query(Employee).delete()
    if 'customers' in existing_tables:
        db.session.query(Customer).delete()
    if 'users' in existing_tables:
        db.session.query(User).delete()
    
    db.session.commit()
    print("✅ All data cleared!")

def seed_users():
    """Create users with all roles."""
    print("\n👥 Creating users...")
    
    users_data = [
        # Admins
        {
            'email': 'admin@ecommerce.com',
            'username': 'admin',
            'password': 'Admin123!',
            'role': 'admin'
        },
        {
            'email': 'superadmin@ecommerce.com',
            'username': 'superadmin',
            'password': 'Admin123!',
            'role': 'admin'
        },
        
        # Managers
        {
            'email': 'manager@ecommerce.com',
            'username': 'manager',
            'password': 'Manager123!',
            'role': 'manager',
            'profile': {
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'phone': '(555) 101-2001',
                'address_line1': '100 Business Park Drive',
                'address_line2': 'Suite 500',
                'city': 'New York',
                'state': 'NY',
                'postal_code': '10001',
                'country': 'USA',
                'employee_id': 'MGR-001',
                'salary': 75000.00,
                'hire_date': datetime.now() - timedelta(days=730)
            }
        },
        {
            'email': 'manager2@ecommerce.com',
            'username': 'manager2',
            'password': 'Manager123!',
            'role': 'manager',
            'profile': {
                'first_name': 'Michael',
                'last_name': 'Chen',
                'phone': '(555) 101-2002',
                'address_line1': '200 Corporate Blvd',
                'city': 'Los Angeles',
                'state': 'CA',
                'postal_code': '90001',
                'country': 'USA',
                'employee_id': 'MGR-002',
                'salary': 72000.00,
                'hire_date': datetime.now() - timedelta(days=550)
            }
        },
        
        # Cashiers
        {
            'email': 'cashier@ecommerce.com',
            'username': 'cashier',
            'password': 'Cashier123!',
            'role': 'cashier',
            'profile': {
                'first_name': 'Emma',
                'last_name': 'Davis',
                'phone': '(555) 201-3001',
                'address_line1': '456 Oak Street',
                'address_line2': 'Apt 12',
                'city': 'Chicago',
                'state': 'IL',
                'postal_code': '60601',
                'country': 'USA',
                'employee_id': 'CASH-001',
                'salary': 35000.00,
                'hire_date': datetime.now() - timedelta(days=365)
            }
        },
        {
            'email': 'cashier2@ecommerce.com',
            'username': 'cashier2',
            'password': 'Cashier123!',
            'role': 'cashier',
            'profile': {
                'first_name': 'James',
                'last_name': 'Wilson',
                'phone': '(555) 201-3002',
                'address_line1': '789 Pine Avenue',
                'city': 'Houston',
                'state': 'TX',
                'postal_code': '77001',
                'country': 'USA',
                'employee_id': 'CASH-002',
                'salary': 33000.00,
                'hire_date': datetime.now() - timedelta(days=200)
            }
        },
        {
            'email': 'cashier3@ecommerce.com',
            'username': 'cashier3',
            'password': 'Cashier123!',
            'role': 'cashier',
            'profile': {
                'first_name': 'Maria',
                'last_name': 'Garcia',
                'phone': '(555) 201-3003',
                'address_line1': '321 Elm Street',
                'city': 'Phoenix',
                'state': 'AZ',
                'postal_code': '85001',
                'country': 'USA',
                'employee_id': 'CASH-003',
                'salary': 34000.00,
                'hire_date': datetime.now() - timedelta(days=150)
            }
        },
        
        # Customers
        {
            'email': 'customer1@example.com',
            'username': 'customer1',
            'password': 'Customer123!',
            'role': 'customer',
            'profile': {
                'first_name': 'John',
                'last_name': 'Smith',
                'phone': '(555) 301-4001',
                'address_line1': '123 Main Street',
                'city': 'Seattle',
                'state': 'WA',
                'postal_code': '98101',
                'country': 'USA'
            }
        },
        {
            'email': 'customer2@example.com',
            'username': 'customer2',
            'password': 'Customer123!',
            'role': 'customer',
            'profile': {
                'first_name': 'Alice',
                'last_name': 'Brown',
                'phone': '(555) 301-4002',
                'address_line1': '456 Park Avenue',
                'address_line2': 'Apt 5B',
                'city': 'Boston',
                'state': 'MA',
                'postal_code': '02101',
                'country': 'USA'
            }
        },
        {
            'email': 'customer3@example.com',
            'username': 'customer3',
            'password': 'Customer123!',
            'role': 'customer',
            'profile': {
                'first_name': 'Robert',
                'last_name': 'Taylor',
                'phone': '(555) 301-4003',
                'address_line1': '789 Broadway',
                'city': 'Miami',
                'state': 'FL',
                'postal_code': '33101',
                'country': 'USA'
            }
        },
        {
            'email': 'customer4@example.com',
            'username': 'customer4',
            'password': 'Customer123!',
            'role': 'customer',
            'profile': {
                'first_name': 'Jennifer',
                'last_name': 'Martinez',
                'phone': '(555) 301-4004',
                'address_line1': '321 Lake Drive',
                'city': 'Denver',
                'state': 'CO',
                'postal_code': '80201',
                'country': 'USA'
            }
        },
        {
            'email': 'customer5@example.com',
            'username': 'customer5',
            'password': 'Customer123!',
            'role': 'customer',
            'profile': {
                'first_name': 'David',
                'last_name': 'Anderson',
                'phone': '(555) 301-4005',
                'address_line1': '654 Valley Road',
                'city': 'Portland',
                'state': 'OR',
                'postal_code': '97201',
                'country': 'USA'
            }
        }
    ]
    
    users = []
    for user_data in users_data:
        # Create user
        user = User(
            email=user_data['email'],
            username=user_data['username'],
            role=user_data['role']
        )
        user.set_password(user_data['password'])
        db.session.add(user)
        db.session.flush()  # Get user.id
        
        # Create profile if data provided
        if 'profile' in user_data:
            profile_data = user_data['profile']
            
            if user_data['role'] == 'customer':
                profile = Customer(
                    user_id=user.id,
                    first_name=profile_data.get('first_name'),
                    last_name=profile_data.get('last_name'),
                    phone=profile_data.get('phone'),
                    address_line1=profile_data.get('address_line1'),
                    address_line2=profile_data.get('address_line2'),
                    city=profile_data.get('city'),
                    state=profile_data.get('state'),
                    postal_code=profile_data.get('postal_code'),
                    country=profile_data.get('country')
                )
            elif user_data['role'] in ['manager', 'cashier']:
                profile = Employee(
                    user_id=user.id,
                    first_name=profile_data.get('first_name'),
                    last_name=profile_data.get('last_name'),
                    phone=profile_data.get('phone'),
                    address_line1=profile_data.get('address_line1'),
                    address_line2=profile_data.get('address_line2'),
                    city=profile_data.get('city'),
                    state=profile_data.get('state'),
                    postal_code=profile_data.get('postal_code'),
                    country=profile_data.get('country'),
                    employee_id=profile_data.get('employee_id'),
                    salary=profile_data.get('salary'),
                    hire_date=profile_data.get('hire_date', datetime.now())
                )
            
            db.session.add(profile)
        
        users.append(user)
    
    db.session.commit()
    print(f"✅ Created {len(users)} users!")
    return users

def seed_categories():
    """Create product categories."""
    print("\n📁 Creating categories...")
    
    categories_data = [
        {
            'name': 'Electronics',
            'description': 'Electronic devices and accessories',
            'subcategories': [
                {'name': 'Smartphones', 'description': 'Mobile phones and accessories'},
                {'name': 'Laptops', 'description': 'Portable computers'},
                {'name': 'Tablets', 'description': 'Tablet devices'},
                {'name': 'Audio', 'description': 'Headphones, speakers, and audio equipment'}
            ]
        },
        {
            'name': 'Clothing',
            'description': 'Apparel and fashion',
            'subcategories': [
                {'name': 'Men\'s Clothing', 'description': 'Clothing for men'},
                {'name': 'Women\'s Clothing', 'description': 'Clothing for women'},
                {'name': 'Shoes', 'description': 'Footwear for all'}
            ]
        },
        {
            'name': 'Home & Garden',
            'description': 'Home improvement and garden supplies',
            'subcategories': [
                {'name': 'Furniture', 'description': 'Home furniture'},
                {'name': 'Kitchen', 'description': 'Kitchen appliances and tools'},
                {'name': 'Garden Tools', 'description': 'Gardening equipment'}
            ]
        },
        {
            'name': 'Books',
            'description': 'Books and literature',
            'subcategories': [
                {'name': 'Fiction', 'description': 'Fiction books'},
                {'name': 'Non-Fiction', 'description': 'Non-fiction books'},
                {'name': 'Textbooks', 'description': 'Educational textbooks'}
            ]
        },
        {
            'name': 'Sports & Outdoors',
            'description': 'Sports equipment and outdoor gear',
            'subcategories': [
                {'name': 'Fitness', 'description': 'Fitness equipment'},
                {'name': 'Camping', 'description': 'Camping gear'},
                {'name': 'Team Sports', 'description': 'Team sports equipment'}
            ]
        }
    ]
    
    categories = []
    for cat_data in categories_data:
        # Create parent category
        category = Category(
            name=cat_data['name'],
            description=cat_data['description']
        )
        db.session.add(category)
        db.session.flush()
        categories.append(category)
        
        # Create subcategories
        for subcat_data in cat_data.get('subcategories', []):
            subcategory = Category(
                name=subcat_data['name'],
                description=subcat_data['description'],
                parent_id=category.id
            )
            db.session.add(subcategory)
            categories.append(subcategory)
    
    db.session.commit()
    print(f"✅ Created {len(categories)} categories!")
    return categories

def seed_products(categories):
    """Create products."""
    print("\n📦 Creating products...")
    
    # Get subcategories for product assignment
    smartphones = Category.query.filter_by(name='Smartphones').first()
    laptops = Category.query.filter_by(name='Laptops').first()
    tablets = Category.query.filter_by(name='Tablets').first()
    audio = Category.query.filter_by(name='Audio').first()
    mens_clothing = Category.query.filter_by(name='Men\'s Clothing').first()
    womens_clothing = Category.query.filter_by(name='Women\'s Clothing').first()
    shoes = Category.query.filter_by(name='Shoes').first()
    
    products_data = [
        # Electronics
        {
            'name': 'iPhone 15 Pro',
            'description': 'Latest iPhone with A17 Pro chip and titanium design',
            'price': 999.99,
            'compare_price': 1099.99,
            'sku': 'IPHONE-15-PRO',
            'barcode': '1234567890123',
            'stock_quantity': 50,
            'category_id': smartphones.id if smartphones else 1,
            'weight': 0.221,
            'is_featured': True
        },
        {
            'name': 'Samsung Galaxy S24 Ultra',
            'description': 'Premium Android smartphone with S Pen',
            'price': 1199.99,
            'compare_price': 1299.99,
            'sku': 'GALAXY-S24-ULTRA',
            'barcode': '1234567890124',
            'stock_quantity': 40,
            'category_id': smartphones.id if smartphones else 1,
            'weight': 0.233,
            'is_featured': True
        },
        {
            'name': 'MacBook Pro 16"',
            'description': 'Powerful laptop with M3 Max chip',
            'price': 2499.99,
            'compare_price': 2699.99,
            'sku': 'MBP-16-M3',
            'barcode': '1234567890125',
            'stock_quantity': 25,
            'category_id': laptops.id if laptops else 1,
            'weight': 2.1,
            'is_featured': True
        },
        {
            'name': 'Dell XPS 15',
            'description': 'Premium Windows laptop with OLED display',
            'price': 1799.99,
            'sku': 'DELL-XPS-15',
            'barcode': '1234567890126',
            'stock_quantity': 30,
            'category_id': laptops.id if laptops else 1,
            'weight': 1.8,
            'is_featured': False
        },
        {
            'name': 'iPad Pro 12.9"',
            'description': 'Professional tablet with M2 chip',
            'price': 1099.99,
            'sku': 'IPAD-PRO-129',
            'barcode': '1234567890127',
            'stock_quantity': 35,
            'category_id': tablets.id if tablets else 1,
            'weight': 0.682,
            'is_featured': True
        },
        {
            'name': 'Sony WH-1000XM5',
            'description': 'Industry-leading noise canceling headphones',
            'price': 399.99,
            'compare_price': 449.99,
            'sku': 'SONY-WH1000XM5',
            'barcode': '1234567890128',
            'stock_quantity': 60,
            'category_id': audio.id if audio else 1,
            'weight': 0.25,
            'is_featured': True
        },
        {
            'name': 'AirPods Pro 2',
            'description': 'Wireless earbuds with active noise cancellation',
            'price': 249.99,
            'sku': 'AIRPODS-PRO-2',
            'barcode': '1234567890129',
            'stock_quantity': 100,
            'category_id': audio.id if audio else 1,
            'weight': 0.05,
            'is_featured': False
        },
        
        # Clothing
        {
            'name': 'Men\'s Cotton T-Shirt',
            'description': 'Comfortable cotton t-shirt in various colors',
            'price': 29.99,
            'sku': 'MENS-TSHIRT-001',
            'barcode': '1234567890130',
            'stock_quantity': 200,
            'category_id': mens_clothing.id if mens_clothing else 2,
            'weight': 0.2,
            'is_featured': False
        },
        {
            'name': 'Women\'s Summer Dress',
            'description': 'Elegant floral summer dress',
            'price': 79.99,
            'compare_price': 99.99,
            'sku': 'WOMENS-DRESS-001',
            'barcode': '1234567890131',
            'stock_quantity': 80,
            'category_id': womens_clothing.id if womens_clothing else 2,
            'weight': 0.3,
            'is_featured': True
        },
        {
            'name': 'Running Shoes',
            'description': 'High-performance running shoes',
            'price': 129.99,
            'sku': 'SHOES-RUNNING-001',
            'barcode': '1234567890132',
            'stock_quantity': 120,
            'category_id': shoes.id if shoes else 2,
            'weight': 0.6,
            'is_featured': True
        }
    ]
    
    products = []
    for prod_data in products_data:
        product = Product(**prod_data)
        db.session.add(product)
        products.append(product)
    
    db.session.commit()
    print(f"✅ Created {len(products)} products!")
    return products

def seed_carts_and_orders(users, products):
    """Create sample carts and orders."""
    print("\n🛒 Creating carts and orders...")
    
    # Get customers
    customers = [u for u in users if u.role == 'customer']
    
    carts_created = 0
    orders_created = 0
    
    # Create carts for customers
    for customer in customers[:3]:  # First 3 customers get carts
        cart = Cart(customer_id=customer.customer.id)
        db.session.add(cart)
        db.session.flush()
        
        # Add 2-3 random UNIQUE products to cart
        num_items = random.randint(2, 3)
        selected_products = random.sample(products, min(num_items, len(products)))  # No duplicates!
        
        for product in selected_products:
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=product.id,
                quantity=random.randint(1, 3)
            )
            db.session.add(cart_item)
        
        carts_created += 1
    
    # Create orders for customers
    for customer in customers:
        # Each customer gets 1-2 orders
        num_orders = random.randint(1, 2)
        
        for i in range(num_orders):
            # Order created 1-30 days ago
            days_ago = random.randint(1, 30)
            created_date = datetime.now() - timedelta(days=days_ago)
            
            # Random order status
            statuses = ['pending', 'confirmed', 'processing', 'shipped', 'delivered']
            status = random.choice(statuses)
            
            # Payment status based on order status
            if status in ['delivered', 'shipped']:
                payment_status = 'paid'
            elif status == 'confirmed':
                payment_status = random.choice(['paid', 'pending'])
            else:
                payment_status = 'pending'
            
            # Calculate tax (8%) and shipping
            tax_rate = 0.08
            shipping_cost = 10.00 if random.random() > 0.3 else 0.00  # 70% have shipping
            
            order = Order(
                order_number=f'ORD-{datetime.now().strftime("%Y%m%d")}-{orders_created + 1:04d}',
                customer_id=customer.customer.id,
                status=status,
                subtotal=0,  # Will calculate after adding items
                tax=0,  # Will calculate after adding items
                shipping_cost=shipping_cost,
                total=0,  # Will calculate after adding items
                payment_method=random.choice(['credit_card', 'debit_card', 'paypal']),
                payment_status=payment_status,
                shipping_address_line1=customer.customer.address_line1,
                shipping_address_line2=customer.customer.address_line2,
                shipping_city=customer.customer.city,
                shipping_state=customer.customer.state,
                shipping_postal_code=customer.customer.postal_code,
                shipping_country=customer.customer.country,
                created_at=created_date
            )
            db.session.add(order)
            db.session.flush()
            
            # Add 1-4 random products to order
            num_items = random.randint(1, 4)
            subtotal = 0
            
            for _ in range(num_items):
                product = random.choice(products)
                quantity = random.randint(1, 2)
                
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    product_name=product.name,
                    product_sku=product.sku,
                    unit_price=product.price,
                    quantity=quantity
                )
                db.session.add(order_item)
                subtotal += float(product.price) * quantity
            
            # Calculate final amounts
            tax = subtotal * tax_rate
            total = subtotal + tax + shipping_cost
            
            # Update order with calculated amounts
            order.subtotal = subtotal
            order.tax = tax
            order.total = total
            
            orders_created += 1
    
    db.session.commit()
    print(f"✅ Created {carts_created} carts and {orders_created} orders!")

def main():
    """Main seeding function."""
    app = create_app()
    
    with app.app_context():
        print("🌱 Starting database seeding...")
        print("=" * 50)
        
        # Clear existing data
        clear_data()
        
        # Seed data in order
        users = seed_users()
        categories = seed_categories()
        products = seed_products(categories)
        seed_carts_and_orders(users, products)
        
        print("\n" + "=" * 50)
        print("🎉 Database seeding completed successfully!")
        print("\n📊 Summary:")
        print(f"   Users: {User.query.count()}")
        print(f"   - Admins: {User.query.filter_by(role='admin').count()}")
        print(f"   - Managers: {User.query.filter_by(role='manager').count()}")
        print(f"   - Cashiers: {User.query.filter_by(role='cashier').count()}")
        print(f"   - Customers: {User.query.filter_by(role='customer').count()}")
        print(f"   Categories: {Category.query.count()}")
        print(f"   Products: {Product.query.count()}")
        print(f"   Carts: {Cart.query.count()}")
        print(f"   Orders: {Order.query.count()}")
        print("\n🔑 Login Credentials:")
        print("   Admin:    admin@ecommerce.com / Admin123!")
        print("   Manager:  manager@ecommerce.com / Manager123!")
        print("   Cashier:  cashier@ecommerce.com / Cashier123!")
        print("   Customer: customer1@example.com / Customer123!")

if __name__ == '__main__':
    main()
