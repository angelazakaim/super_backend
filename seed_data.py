"""Seed data for e-commerce database with comprehensive test data."""
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
    """Create test users with different roles."""
    print("\n👥 Creating users...")
    
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
    print("  ✓ Created admin user")
    
    # 2. Manager User + Employee Profile
    manager = User(
        email='manager@ecommerce.com',
        username='manager',
        role=UserRole.MANAGER.value,
        is_active=True
    )
    manager.set_password('Manager123!')
    users.append(manager)
    print("  ✓ Created manager user")
    
    # 3. Cashier User + Employee Profile
    cashier = User(
        email='cashier@ecommerce.com',
        username='cashier',
        role=UserRole.CASHIER.value,
        is_active=True
    )
    cashier.set_password('Cashier123!')
    users.append(cashier)
    print("  ✓ Created cashier user")
    
    # 4-8. Customer Users (5 customers)
    customer_data = [
        ('john.doe@email.com', 'johndoe', 'John', 'Doe', '555-0101'),
        ('jane.smith@email.com', 'janesmith', 'Jane', 'Smith', '555-0102'),
        ('bob.wilson@email.com', 'bobwilson', 'Bob', 'Wilson', '555-0103'),
        ('alice.brown@email.com', 'alicebrown', 'Alice', 'Brown', '555-0104'),
        ('charlie.davis@email.com', 'charliedavis', 'Charlie', 'Davis', '555-0105'),
    ]
    
    for email, username, first, last, phone in customer_data:
        customer_user = User(
            email=email,
            username=username,
            role=UserRole.CUSTOMER.value,
            is_active=True
        )
        customer_user.set_password('Customer123!')
        users.append(customer_user)
    
    print(f"  ✓ Created {len(customer_data)} customer users")
    
    # Add all users to session
    db.session.add_all(users)
    db.session.commit()
    
    print(f"✅ Total users created: {len(users)}")
    return users


def create_employee_profiles(users):
    """Create employee profiles for manager and cashier."""
    print("\n👔 Creating employee profiles...")
    
    employees = []
    
    # Find manager and cashier users
    manager = next(u for u in users if u.role == UserRole.MANAGER.value)
    cashier = next(u for u in users if u.role == UserRole.CASHIER.value)
    
    # Manager profile
    manager_profile = Employee(
        user_id=manager.id,
        first_name='Sarah',
        last_name='Johnson',
        phone='555-0201',
        address_line1='123 Manager Street',
        city='New York',
        state='NY',
        postal_code='10001',
        country='USA',
        employee_id='MGR-001',
        hire_date=datetime.now(timezone.utc) - timedelta(days=730),  # 2 years ago
        salary=75000.00,
        shift_start=datetime.strptime('09:00', '%H:%M').time(),
        shift_end=datetime.strptime('17:00', '%H:%M').time()
    )
    employees.append(manager_profile)
    
    # Cashier profile
    cashier_profile = Employee(
        user_id=cashier.id,
        first_name='Mike',
        last_name='Anderson',
        phone='555-0202',
        address_line1='456 Cashier Avenue',
        city='New York',
        state='NY',
        postal_code='10002',
        country='USA',
        employee_id='CSH-001',
        hire_date=datetime.now(timezone.utc) - timedelta(days=365),  # 1 year ago
        salary=45000.00,
        shift_start=datetime.strptime('10:00', '%H:%M').time(),
        shift_end=datetime.strptime('18:00', '%H:%M').time()
    )
    employees.append(cashier_profile)
    
    db.session.add_all(employees)
    db.session.commit()
    
    print(f"✅ Created {len(employees)} employee profiles")
    return employees


def create_customer_profiles(users):
    """Create customer profiles."""
    print("\n🛍️  Creating customer profiles...")
    
    customers = []
    customer_users = [u for u in users if u.role == UserRole.CUSTOMER.value]
    
    addresses = [
        ('123 Main St', 'Apt 4B', 'New York', 'NY', '10001', 'USA'),
        ('456 Oak Ave', None, 'Los Angeles', 'CA', '90001', 'USA'),
        ('789 Pine Rd', 'Suite 100', 'Chicago', 'IL', '60601', 'USA'),
        ('321 Elm St', None, 'Houston', 'TX', '77001', 'USA'),
        ('654 Maple Dr', 'Unit 5', 'Phoenix', 'AZ', '85001', 'USA'),
    ]
    
    for i, user in enumerate(customer_users):
        # Extract first and last name from username (e.g., 'johndoe' -> 'John', 'Doe')
        username = user.username
        if 'john' in username:
            first, last = 'John', 'Doe'
        elif 'jane' in username:
            first, last = 'Jane', 'Smith'
        elif 'bob' in username:
            first, last = 'Bob', 'Wilson'
        elif 'alice' in username:
            first, last = 'Alice', 'Brown'
        else:
            first, last = 'Charlie', 'Davis'
        
        addr = addresses[i]
        customer = Customer(
            user_id=user.id,
            first_name=first,
            last_name=last,
            phone=f'555-01{i+1:02d}',
            address_line1=addr[0],
            address_line2=addr[1],
            city=addr[2],
            state=addr[3],
            postal_code=addr[4],
            country=addr[5]
        )
        customers.append(customer)
    
    db.session.add_all(customers)
    db.session.commit()
    
    print(f"✅ Created {len(customers)} customer profiles")
    return customers


def create_categories():
    """Create product categories with hierarchy."""
    print("\n📂 Creating categories...")
    
    categories = []
    
    # Root categories
    electronics = Category(name='Electronics', description='Electronic devices and accessories', is_active=True)
    clothing = Category(name='Clothing', description='Apparel and fashion', is_active=True)
    home = Category(name='Home & Garden', description='Home improvement and garden supplies', is_active=True)
    sports = Category(name='Sports & Outdoors', description='Sports equipment and outdoor gear', is_active=True)
    books = Category(name='Books', description='Books and literature', is_active=True)
    
    categories.extend([electronics, clothing, home, sports, books])
    
    db.session.add_all(categories)
    db.session.commit()
    
    # Subcategories - Electronics
    computers = Category(name='Computers', description='Laptops, desktops, and accessories', parent_id=electronics.id, is_active=True)
    phones = Category(name='Smartphones', description='Mobile phones and accessories', parent_id=electronics.id, is_active=True)
    audio = Category(name='Audio', description='Headphones, speakers, and audio equipment', parent_id=electronics.id, is_active=True)
    
    # Subcategories - Clothing
    mens = Category(name="Men's Clothing", description='Clothing for men', parent_id=clothing.id, is_active=True)
    womens = Category(name="Women's Clothing", description='Clothing for women', parent_id=clothing.id, is_active=True)
    
    # Subcategories - Home & Garden
    furniture = Category(name='Furniture', description='Home furniture', parent_id=home.id, is_active=True)
    kitchen = Category(name='Kitchen', description='Kitchen appliances and utensils', parent_id=home.id, is_active=True)
    
    subcategories = [computers, phones, audio, mens, womens, furniture, kitchen]
    
    db.session.add_all(subcategories)
    db.session.commit()
    
    all_categories = categories + subcategories
    print(f"✅ Created {len(all_categories)} categories ({len(categories)} root, {len(subcategories)} subcategories)")
    return all_categories


def create_products(categories):
    """Create sample products."""
    print("\n📦 Creating products...")
    
    products = []
    
    # Get category IDs
    computers_cat = next(c for c in categories if c.name == 'Computers')
    phones_cat = next(c for c in categories if c.name == 'Smartphones')
    audio_cat = next(c for c in categories if c.name == 'Audio')
    mens_cat = next(c for c in categories if c.name == "Men's Clothing")
    womens_cat = next(c for c in categories if c.name == "Women's Clothing")
    furniture_cat = next(c for c in categories if c.name == 'Furniture')
    kitchen_cat = next(c for c in categories if c.name == 'Kitchen')
    
    # Electronics - Computers
    products.extend([
        Product(
            name='Dell XPS 15 Laptop',
            description='15.6" high-performance laptop with Intel Core i7, 16GB RAM, 512GB SSD',
            price=Decimal('1299.99'),
            compare_price=Decimal('1499.99'),
            sku='LAPTOP-DELL-XPS15',
            barcode='1234567890001',
            stock_quantity=25,
            category_id=computers_cat.id,
            weight=Decimal('2.0'),
            is_active=True,
            is_featured=True
        ),
        Product(
            name='MacBook Pro 14"',
            description='Apple MacBook Pro with M3 chip, 18GB RAM, 512GB SSD',
            price=Decimal('1999.99'),
            compare_price=Decimal('2199.99'),
            sku='LAPTOP-APPLE-MBP14',
            barcode='1234567890002',
            stock_quantity=15,
            category_id=computers_cat.id,
            weight=Decimal('1.6'),
            is_active=True,
            is_featured=True
        ),
        Product(
            name='Logitech MX Master 3S Mouse',
            description='Advanced wireless mouse with precision scrolling',
            price=Decimal('99.99'),
            sku='MOUSE-LOGI-MX3S',
            barcode='1234567890003',
            stock_quantity=50,
            category_id=computers_cat.id,
            weight=Decimal('0.14'),
            is_active=True,
            is_featured=False
        ),
    ])
    
    # Electronics - Smartphones
    products.extend([
        Product(
            name='iPhone 15 Pro',
            description='Apple iPhone 15 Pro with A17 Pro chip, 256GB storage',
            price=Decimal('999.99'),
            compare_price=Decimal('1099.99'),
            sku='PHONE-APPLE-IP15PRO',
            barcode='1234567890010',
            stock_quantity=30,
            category_id=phones_cat.id,
            weight=Decimal('0.22'),
            is_active=True,
            is_featured=True
        ),
        Product(
            name='Samsung Galaxy S24 Ultra',
            description='Samsung flagship phone with 512GB storage and S Pen',
            price=Decimal('1199.99'),
            sku='PHONE-SAMSUNG-S24U',
            barcode='1234567890011',
            stock_quantity=20,
            category_id=phones_cat.id,
            weight=Decimal('0.23'),
            is_active=True,
            is_featured=True
        ),
    ])
    
    # Electronics - Audio
    products.extend([
        Product(
            name='Sony WH-1000XM5 Headphones',
            description='Premium noise-canceling wireless headphones',
            price=Decimal('399.99'),
            compare_price=Decimal('449.99'),
            sku='AUDIO-SONY-WH1000XM5',
            barcode='1234567890020',
            stock_quantity=40,
            category_id=audio_cat.id,
            weight=Decimal('0.25'),
            is_active=True,
            is_featured=True
        ),
        Product(
            name='AirPods Pro (2nd Gen)',
            description='Apple wireless earbuds with active noise cancellation',
            price=Decimal('249.99'),
            sku='AUDIO-APPLE-AIRPODSPRO2',
            barcode='1234567890021',
            stock_quantity=60,
            category_id=audio_cat.id,
            weight=Decimal('0.05'),
            is_active=True,
            is_featured=False
        ),
    ])
    
    # Clothing - Men's
    products.extend([
        Product(
            name="Men's Classic Fit Jeans",
            description='Comfortable denim jeans, available in multiple sizes',
            price=Decimal('59.99'),
            sku='CLOTH-MENS-JEANS-001',
            barcode='1234567890030',
            stock_quantity=100,
            category_id=mens_cat.id,
            weight=Decimal('0.60'),
            is_active=True,
            is_featured=False
        ),
        Product(
            name="Men's Premium Cotton T-Shirt",
            description='Soft, breathable cotton t-shirt in various colors',
            price=Decimal('24.99'),
            sku='CLOTH-MENS-TSHIRT-001',
            barcode='1234567890031',
            stock_quantity=150,
            category_id=mens_cat.id,
            weight=Decimal('0.20'),
            is_active=True,
            is_featured=False
        ),
    ])
    
    # Clothing - Women's
    products.extend([
        Product(
            name="Women's Summer Dress",
            description='Elegant floral print dress, perfect for summer',
            price=Decimal('79.99'),
            compare_price=Decimal('99.99'),
            sku='CLOTH-WOMENS-DRESS-001',
            barcode='1234567890040',
            stock_quantity=75,
            category_id=womens_cat.id,
            weight=Decimal('0.30'),
            is_active=True,
            is_featured=True
        ),
        Product(
            name="Women's Yoga Pants",
            description='Comfortable, stretchy yoga pants with moisture-wicking fabric',
            price=Decimal('49.99'),
            sku='CLOTH-WOMENS-YOGA-001',
            barcode='1234567890041',
            stock_quantity=120,
            category_id=womens_cat.id,
            weight=Decimal('0.25'),
            is_active=True,
            is_featured=False
        ),
    ])
    
    # Home & Garden - Furniture
    products.extend([
        Product(
            name='Modern Office Chair',
            description='Ergonomic office chair with lumbar support',
            price=Decimal('299.99'),
            compare_price=Decimal('349.99'),
            sku='FURN-CHAIR-OFFICE-001',
            barcode='1234567890050',
            stock_quantity=35,
            category_id=furniture_cat.id,
            weight=Decimal('15.0'),
            is_active=True,
            is_featured=True
        ),
        Product(
            name='Standing Desk',
            description='Adjustable height standing desk, 60" x 30"',
            price=Decimal('499.99'),
            sku='FURN-DESK-STAND-001',
            barcode='1234567890051',
            stock_quantity=20,
            category_id=furniture_cat.id,
            weight=Decimal('35.0'),
            is_active=True,
            is_featured=True
        ),
    ])
    
    # Home & Garden - Kitchen
    products.extend([
        Product(
            name='KitchenAid Stand Mixer',
            description='Professional 5-quart stand mixer with multiple attachments',
            price=Decimal('399.99'),
            compare_price=Decimal('449.99'),
            sku='KITCHEN-MIXER-KA5Q',
            barcode='1234567890060',
            stock_quantity=30,
            category_id=kitchen_cat.id,
            weight=Decimal('10.0'),
            is_active=True,
            is_featured=True
        ),
        Product(
            name='Ninja Blender Professional',
            description='1000W professional blender with multiple speeds',
            price=Decimal('129.99'),
            sku='KITCHEN-BLEND-NINJA',
            barcode='1234567890061',
            stock_quantity=45,
            category_id=kitchen_cat.id,
            weight=Decimal('4.5'),
            is_active=True,
            is_featured=False
        ),
    ])
    
    # Add a few low-stock items
    products.append(
        Product(
            name='Limited Edition Mechanical Keyboard',
            description='Premium mechanical keyboard with RGB lighting',
            price=Decimal('179.99'),
            sku='KB-MECH-LIMITED',
            barcode='1234567890070',
            stock_quantity=5,  # Low stock!
            category_id=computers_cat.id,
            weight=Decimal('1.2'),
            is_active=True,
            is_featured=True
        )
    )
    
    db.session.add_all(products)
    db.session.commit()
    
    print(f"✅ Created {len(products)} products")
    return products


def create_carts_and_items(customers, products):
    """Create shopping carts with items for some customers."""
    print("\n🛒 Creating shopping carts...")
    
    carts_created = 0
    items_created = 0
    
    # Create carts for first 3 customers
    for i, customer in enumerate(customers[:3]):
        cart = Cart(customer_id=customer.id)
        db.session.add(cart)
        db.session.commit()
        carts_created += 1
        
        # Add 2-4 random products to each cart
        num_items = random.randint(2, 4)
        selected_products = random.sample(products, num_items)
        
        for product in selected_products:
            quantity = random.randint(1, 3)
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=product.id,
                quantity=quantity
            )
            db.session.add(cart_item)
            items_created += 1
        
        db.session.commit()
    
    print(f"✅ Created {carts_created} carts with {items_created} items total")


def create_orders(customers, products):
    """Create sample orders with different statuses."""
    print("\n📋 Creating orders...")
    
    orders = []
    order_items = []
    order_number_counter = 1000
    
    # Create orders for each customer
    for customer in customers:
        # Each customer gets 1-3 orders
        num_orders = random.randint(1, 3)
        
        for _ in range(num_orders):
            order_number_counter += 1
            
            # Random order status (weighted towards completed orders)
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
            
            # Random payment status
            if status == OrderStatus.CANCELLED.value:
                payment_status = PaymentStatus.REFUNDED.value
            elif status in [OrderStatus.PENDING.value, OrderStatus.CONFIRMED.value]:
                payment_status = random.choice([PaymentStatus.PENDING.value, PaymentStatus.PAID.value])
            else:
                payment_status = PaymentStatus.PAID.value
            
            # Calculate order date (older orders are more likely to be delivered)
            if status == OrderStatus.DELIVERED.value:
                days_ago = random.randint(7, 60)
            elif status == OrderStatus.SHIPPED.value:
                days_ago = random.randint(3, 7)
            elif status == OrderStatus.PROCESSING.value:
                days_ago = random.randint(1, 3)
            else:
                days_ago = random.randint(0, 2)
            
            created_at = datetime.now(timezone.utc) - timedelta(days=days_ago)
            
            # Select 1-4 random products
            num_products = random.randint(1, 4)
            order_products = random.sample(products, num_products)
            
            # Calculate totals
            subtotal = Decimal('0.00')
            for product in order_products:
                quantity = random.randint(1, 2)
                subtotal += product.price * quantity
            
            tax = subtotal * Decimal('0.1')  # 10% tax
            shipping_cost = Decimal('10.00') if subtotal < 100 else Decimal('0.00')  # Free shipping over $100
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
                shipping_address_line2=customer.address_line2,
                shipping_city=customer.city,
                shipping_state=customer.state,
                shipping_postal_code=customer.postal_code,
                shipping_country=customer.country,
                created_at=created_at
            )
            
            # Set status timestamps
            if status in [OrderStatus.CONFIRMED.value, OrderStatus.PROCESSING.value, OrderStatus.SHIPPED.value, OrderStatus.DELIVERED.value]:
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
                quantity = random.randint(1, 2)
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
    
    print(f"✅ Created {len(orders)} orders with {len(order_items)} order items")
    print(f"   - Pending: {sum(1 for o in orders if o.status == OrderStatus.PENDING.value)}")
    print(f"   - Confirmed: {sum(1 for o in orders if o.status == OrderStatus.CONFIRMED.value)}")
    print(f"   - Processing: {sum(1 for o in orders if o.status == OrderStatus.PROCESSING.value)}")
    print(f"   - Shipped: {sum(1 for o in orders if o.status == OrderStatus.SHIPPED.value)}")
    print(f"   - Delivered: {sum(1 for o in orders if o.status == OrderStatus.DELIVERED.value)}")
    print(f"   - Cancelled: {sum(1 for o in orders if o.status == OrderStatus.CANCELLED.value)}")
    
    return orders


def seed_database():
    """Main function to seed the database."""
    print("=" * 60)
    print("🌱 SEEDING DATABASE")
    print("=" * 60)
    
    # Clear existing data
    clear_data()
    
    # Create data in order
    users = create_users()
    employees = create_employee_profiles(users)
    customers = create_customer_profiles(users)
    categories = create_categories()
    products = create_products(categories)
    create_carts_and_items(customers, products)
    orders = create_orders(customers, products)
    
    print("\n" + "=" * 60)
    print("✅ DATABASE SEEDING COMPLETE!")
    print("=" * 60)
    print("\n📊 Summary:")
    print(f"   Users: {User.query.count()}")
    print(f"   Customers: {Customer.query.count()}")
    print(f"   Employees: {Employee.query.count()}")
    print(f"   Categories: {Category.query.count()}")
    print(f"   Products: {Product.query.count()}")
    print(f"   Carts: {Cart.query.count()}")
    print(f"   Cart Items: {CartItem.query.count()}")
    print(f"   Orders: {Order.query.count()}")
    print(f"   Order Items: {OrderItem.query.count()}")
    print("\n🔑 Test Accounts:")
    print("   Admin:")
    print("     Email: admin@ecommerce.com")
    print("     Password: Admin123!")
    print("\n   Manager:")
    print("     Email: manager@ecommerce.com")
    print("     Password: Manager123!")
    print("\n   Cashier:")
    print("     Email: cashier@ecommerce.com")
    print("     Password: Cashier123!")
    print("\n   Customer (example):")
    print("     Email: john.doe@email.com")
    print("     Password: Customer123!")
    print("=" * 60)


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_database()
