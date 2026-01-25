"""
Updated seed data for demonstrating pagination behavior.
Fixed to handle dynamic relationships and model __init__ changes.
"""
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
# Assuming these exist based on your seed script imports
from app.models.cart import Cart
from app.models.cart_item import CartItem
from app.models.order import Order
from app.models.order_item import OrderItem
from app.enums import UserRole, OrderStatus, PaymentStatus, PaymentMethod

def clear_data():
    """Clear all existing data from the database."""
    print("🗑️  Clearing existing data...")
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
    """Create test users."""
    print("\n👥 Creating users...")
    users = []
    
    # Staff
    roles = [
        ('admin@ecommerce.com', 'admin', UserRole.ADMIN.value, 'Admin123!'),
        ('manager@ecommerce.com', 'manager', UserRole.MANAGER.value, 'Manager123!'),
        ('cashier@ecommerce.com', 'cashier', UserRole.CASHIER.value, 'Cashier123!')
    ]
    
    for email, username, role, pwd in roles:
        u = User(email=email, username=username, role=role, is_active=True)
        u.set_password(pwd)
        users.append(u)
    
    # 50 Customers
    for i in range(1, 51):
        u = User(email=f'customer{i}@email.com', username=f'customer{i}', 
                 role=UserRole.CUSTOMER.value, is_active=True)
        u.set_password('Customer123!')
        users.append(u)
    
    db.session.add_all(users)
    db.session.commit()
    return users

def create_categories():
    """Create product categories."""
    print("\n📂 Creating categories...")
    
    # Root categories
    cat_names = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books', 'Toys', 'Beauty', 'Automotive']
    roots = {}
    for name in cat_names:
        cat = Category(name=name, description=f'Quality {name} products')
        db.session.add(cat)
        roots[name] = cat
    
    db.session.commit()
    
    # Subcategories
    subs = [
        ('Computers', roots['Electronics'].id),
        ('Smartphones', roots['Electronics'].id),
        ('Audio', roots['Electronics'].id),
        ("Men's Clothing", roots['Clothing'].id),
        ("Women's Clothing", roots['Clothing'].id)
    ]
    
    all_subs = []
    for name, parent_id in subs:
        sub = Category(name=name, parent_id=parent_id)
        db.session.add(sub)
        all_subs.append(sub)
    
    db.session.commit()
    return list(roots.values()) + all_subs

def create_many_products(categories):
    """Create 150 products."""
    print("\n📦 Creating 150 products...")
    
    # FIX: Correctly identify leaf categories for dynamic relationships
    # We check if the 'children' query returns any results
    leaf_categories = [c for c in categories if c.children.first() is None]
    
    if not leaf_categories:
        print("⚠️ No leaf categories found, using all categories.")
        leaf_categories = categories

    templates = [
        ('Laptop', 800, 1500), ('Phone', 400, 1200), ('Headphones', 50, 400),
        ('Mouse', 15, 100), ('Keyboard', 60, 200), ('Monitor', 150, 800),
        ('T-Shirt', 15, 50), ('Jeans', 40, 150), ('Shoes', 50, 200)
    ]
    
    brands = ['Premium', 'Elite', 'Pro', 'Ultra', 'Max']
    products = []

    for i in range(150):
        brand = brands[i % len(brands)]
        template_name, min_p, max_p = templates[i % len(templates)]
        category = leaf_categories[i % len(leaf_categories)]
        
        price = Decimal(str(round(random.uniform(min_p, max_p), 2)))
        
        # Matching your Product.__init__ signature
        product = Product(
            name=f'{brand} {template_name} {i+1}',
            price=price,
            category_id=category.id,
            sku=f'SKU-{i+1:05d}',
            stock_quantity=random.choice([0, 10, 50, 100]),
            description=f'High quality {template_name} from our {brand} line.',
            barcode=f'729{i:09d}',
            compare_price=price * Decimal('1.2') if random.random() > 0.8 else None,
            is_active=True,
            is_featured=(random.random() > 0.9)
        )
        
        # Set timestamp manually since it's not in __init__
        days_ago = random.randint(0, 365)
        product.created_at = datetime.now(timezone.utc) - timedelta(days=days_ago)
        
        products.append(product)
    
    db.session.add_all(products)
    db.session.commit()
    return products

def create_customer_profiles(users):
    """Create profiles for customer users."""
    print("\n🛍️ Creating customer profiles...")
    customers = []
    customer_users = [u for u in users if u.role == UserRole.CUSTOMER.value]
    
    for i, user in enumerate(customer_users):
        cust = Customer(
            user_id=user.id,
            first_name=f'User{i}',
            last_name='Test',
            phone=f'050-12345{i:02d}',
            address_line1=f'Street {i}',
            city='Tel Aviv',
            state='Center',
            postal_code='12345',
            country='Israel'
        )
        customers.append(cust)
    db.session.add_all(customers)
    db.session.commit()
    return customers

def create_many_orders(customers, products):
    """Create 100 orders."""
    print("\n📋 Creating 100 orders...")
    for i in range(100):
        customer = random.choice(customers)
        status = random.choice(list(OrderStatus))
        
        order = Order(
            order_number=f'ORD-{1000+i}',
            customer_id=customer.id,
            status=status.value,
            payment_status=PaymentStatus.PAID.value if status == OrderStatus.DELIVERED else PaymentStatus.PENDING.value,
            payment_method=PaymentMethod.CREDIT_CARD.value,
            subtotal=Decimal('0.00'),
            tax=Decimal('0.00'),
            shipping_cost=Decimal('0.00'),
            total=Decimal('0.00'),
            shipping_address_line1=customer.address_line1,
            shipping_city=customer.city,
            shipping_state=customer.state,
            shipping_postal_code=customer.postal_code,
            shipping_country=customer.country
        )
        db.session.add(order)
        db.session.flush() # Get order.id

        # Add items
        order_total = Decimal('0.00')
        for _ in range(random.randint(1, 3)):
            p = random.choice(products)
            qty = random.randint(1, 2)
            item = OrderItem(
                order_id=order.id,
                product_id=p.id,
                product_name=p.name,
                product_sku=p.sku,
                unit_price=p.price,
                quantity=qty
            )
            order_total += (p.price * qty)
            db.session.add(item)
        
        order.subtotal = order_total
        order.total = order_total * Decimal('1.17') # Add VAT
    
    db.session.commit()

def seed_database():
    """Main seed execution."""
    print("🌱 STARTING SEED PROCESS")
    clear_data()
    users = create_users()
    customers = create_customer_profiles(users)
    categories = create_categories()
    products = create_many_products(categories)
    create_many_orders(customers, products)
    print("\n✨ SEEDING COMPLETE!")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_database()