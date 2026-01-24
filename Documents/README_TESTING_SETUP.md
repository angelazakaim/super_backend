# 🚀 Complete Testing Setup - Seed Data & Postman Collection v2.0

## 📦 What's New in v2.0

### ✅ Updated Files:
1. **seed_data.py** - Complete seed data with addresses for ALL users
2. **employee_FINAL.py** - Employee model with full address fields
3. **auth_routes_FINAL.py** - Registration routes supporting address for employees
4. **Postman Collection v2** - Updated collection with address testing

### 🆕 Key Changes:
- **Employee model** now includes:
  - first_name, last_name, phone
  - address_line1, address_line2
  - city, state, postal_code, country
  
- **All roles** (Customer, Cashier, Manager) have consistent fields
- **Seed data** includes realistic addresses for all users
- **Postman tests** verify address data

---

## 🎯 Quick Start Guide

### Step 1: Apply Database Changes

```bash
# Update model
cp employee_FINAL.py app/models/employee.py

# Update routes
cp auth_routes_FINAL.py app/routes/auth_routes.py

# Create migration
flask db migrate -m "Add address fields to Employee model"

# Apply migration
flask db upgrade
```

### Step 2: Seed Database

```bash
# Run seed script
python seed_data.py
```

**Output:**
```
🌱 Starting database seeding...
🗑️  Clearing existing data...
✅ All data cleared!

👥 Creating users...
✅ Created 11 users!

📁 Creating categories...
✅ Created 19 categories!

📦 Creating products...
✅ Created 10 products!

🛒 Creating carts and orders...
✅ Created 3 carts and 10 orders!

🎉 Database seeding completed successfully!

📊 Summary:
   Users: 11
   - Admins: 2
   - Managers: 2
   - Cashiers: 3
   - Customers: 5
   Categories: 19
   Products: 10
   Carts: 3
   Orders: 10

🔑 Login Credentials:
   Admin:    admin@ecommerce.com / Admin123!
   Manager:  manager@ecommerce.com / Manager123!
   Cashier:  cashier@ecommerce.com / Cashier123!
   Customer: customer1@example.com / Customer123!
```

### Step 3: Import Postman Collection

1. Open Postman
2. Click **Import**
3. Select `E-Commerce_API_v2_Complete.postman_collection.json`
4. Collection imported! ✅

### Step 4: Test API

Run folders in order:
1. **1. Authentication** - Login all users
2. **2. Categories** - Test category CRUD
3. **3. Products** - Test product management
4. **4. Cart** - Test shopping cart
5. **5. Orders** - Test order processing
6. **6. User Management** - Test admin operations
7. **7. Permission Tests** - Verify RBAC

---

## 📊 Seed Data Details

### Users Created

#### 👑 Admins (2)
```
admin@ecommerce.com / Admin123!
superadmin@ecommerce.com / Admin123!
```

#### 📊 Managers (2)
```
manager@ecommerce.com / Manager123!
- Name: Sarah Johnson
- Phone: (555) 101-2001
- Address: 100 Business Park Drive, Suite 500, New York, NY 10001
- Employee ID: MGR-001
- Salary: $75,000

manager2@ecommerce.com / Manager123!
- Name: Michael Chen
- Phone: (555) 101-2002
- Address: 200 Corporate Blvd, Los Angeles, CA 90001
- Employee ID: MGR-002
- Salary: $72,000
```

#### 💵 Cashiers (3)
```
cashier@ecommerce.com / Cashier123!
- Name: Emma Davis
- Phone: (555) 201-3001
- Address: 456 Oak Street, Apt 12, Chicago, IL 60601
- Employee ID: CASH-001
- Salary: $35,000

cashier2@ecommerce.com / Cashier123!
- Name: James Wilson
- Phone: (555) 201-3002
- Address: 789 Pine Avenue, Houston, TX 77001
- Employee ID: CASH-002
- Salary: $33,000

cashier3@ecommerce.com / Cashier123!
- Name: Maria Garcia
- Phone: (555) 201-3003
- Address: 321 Elm Street, Phoenix, AZ 85001
- Employee ID: CASH-003
- Salary: $34,000
```

#### 👤 Customers (5)
```
customer1@example.com / Customer123!
- Name: John Smith
- Phone: (555) 301-4001
- Address: 123 Main Street, Seattle, WA 98101

customer2@example.com / Customer123!
- Name: Alice Brown
- Phone: (555) 301-4002
- Address: 456 Park Avenue, Apt 5B, Boston, MA 02101

customer3@example.com / Customer123!
- Name: Robert Taylor
- Phone: (555) 301-4003
- Address: 789 Broadway, Miami, FL 33101

customer4@example.com / Customer123!
- Name: Jennifer Martinez
- Phone: (555) 301-4004
- Address: 321 Lake Drive, Denver, CO 80201

customer5@example.com / Customer123!
- Name: David Anderson
- Phone: (555) 301-4005
- Address: 654 Valley Road, Portland, OR 97201
```

---

### Categories Created (19 total)

**5 Parent Categories with Subcategories:**

1. **Electronics**
   - Smartphones
   - Laptops
   - Tablets
   - Audio

2. **Clothing**
   - Men's Clothing
   - Women's Clothing
   - Shoes

3. **Home & Garden**
   - Furniture
   - Kitchen
   - Garden Tools

4. **Books**
   - Fiction
   - Non-Fiction
   - Textbooks

5. **Sports & Outdoors**
   - Fitness
   - Camping
   - Team Sports

---

### Products Created (10)

**Electronics:**
1. iPhone 15 Pro - $999.99 (Featured)
2. Samsung Galaxy S24 Ultra - $1,199.99 (Featured)
3. MacBook Pro 16" - $2,499.99 (Featured)
4. Dell XPS 15 - $1,799.99
5. iPad Pro 12.9" - $1,099.99 (Featured)
6. Sony WH-1000XM5 - $399.99 (Featured)
7. AirPods Pro 2 - $249.99

**Clothing:**
8. Men's Cotton T-Shirt - $29.99
9. Women's Summer Dress - $79.99 (Featured)
10. Running Shoes - $129.99 (Featured)

---

### Orders Created (10)

- Random orders for all 5 customers
- Various statuses: pending, confirmed, processing, shipped, delivered
- Created over last 30 days
- 1-4 products per order

---

### Carts Created (3)

- First 3 customers have active carts
- 2-3 products per cart
- Ready for checkout testing

---

## 🧪 Postman Collection v2.0

### Collection Contents (80+ Requests)

#### 1. Authentication & Registration (9 requests)
- ✅ Register Customer with full address
- ✅ Register Cashier with full address
- ✅ Register Manager with full address
- ✅ Register Admin
- ✅ Login Admin (auto-saves token)
- ✅ Login Manager (auto-saves token)
- ✅ Login Cashier (auto-saves token)
- ✅ Login Customer (auto-saves token)
- ✅ Get Current User (Me)

#### 2. Categories (7 requests)
- Create category (Admin)
- Create category (Manager - should fail)
- Get all categories (Public)
- Get category by ID
- Create subcategory (Manager)
- Update category (Manager)
- Delete category (Admin)

#### 3. Products (14 requests)
- Create product (Manager)
- Create product (Cashier - should fail)
- Get all products (Public)
- Get product by ID
- Search by SKU (Staff)
- Search by barcode (Staff)
- Update product (Manager)
- Update price (Manager - should fail)
- Update price (Admin)
- Update stock (Manager)
- Check stock (Staff)
- Get low stock (Manager)
- Soft delete (Manager)
- Restore product (Manager)

#### 4. Cart (6 requests)
- Get cart
- Add to cart
- Update cart item
- Validate cart
- Remove from cart
- Clear cart

#### 5. Orders (14 requests)
- Create order (Customer)
- Get customer orders
- Get order by ID
- Get today's orders (Staff)
- Search by number (Staff)
- Update status (Cashier)
- Update to delivered (Cashier - should fail)
- Update payment status (Staff)
- Mark as shipped (Staff)
- Get all orders (Manager - 30 days)
- Get all orders (Admin - all time)
- Add notes (Manager)
- Process refund (Admin)
- Cancel order (Customer)

#### 6. User Management (13 requests)
- Get own profile
- Update own profile
- Get all customers (Manager)
- Get all users (Admin)
- Get user by ID (Admin)
- Create user (Admin)
- Update user (Admin)
- Change user role (Admin)
- Ban user (Admin)
- Reset password (Admin)
- Get user stats (Admin)
- Delete user (Admin)

#### 7. Permission Tests (4 requests)
- Customer creates product (should fail - 403)
- Manager changes price (should fail - 403)
- Cashier processes refund (should fail - 403)
- Manager deletes category (should fail - 403)

---

## 📝 Updated Request Examples

### Register Cashier with Address

```json
POST /api/auth/register

{
  "email": "newcashier@test.com",
  "username": "newcashier",
  "password": "Cashier123!",
  "role": "cashier",
  "first_name": "Emma",
  "last_name": "Davis",
  "phone": "(555) 201-3001",
  "address_line1": "456 Oak Street",
  "address_line2": "Apt 12",
  "city": "Chicago",
  "state": "IL",
  "postal_code": "60601",
  "country": "USA",
  "employee_id": "CASH-001",
  "salary": 35000
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "newcashier@test.com",
    "username": "newcashier",
    "role": "cashier",
    "is_active": true
  },
  "profile": {
    "id": 1,
    "user_id": 1,
    "first_name": "Emma",
    "last_name": "Davis",
    "full_name": "Emma Davis",
    "phone": "(555) 201-3001",
    "address": {
      "line1": "456 Oak Street",
      "line2": "Apt 12",
      "city": "Chicago",
      "state": "IL",
      "postal_code": "60601",
      "country": "USA"
    },
    "employee_id": "CASH-001",
    "hire_date": "2024-01-24T10:30:00"
  }
}
```

---

### Register Manager with Address

```json
POST /api/auth/register

{
  "email": "newmanager@test.com",
  "username": "newmanager",
  "password": "Manager123!",
  "role": "manager",
  "first_name": "Sarah",
  "last_name": "Johnson",
  "phone": "(555) 111-2222",
  "address_line1": "100 Business Park Drive",
  "address_line2": "Suite 500",
  "city": "New York",
  "state": "NY",
  "postal_code": "10001",
  "country": "USA",
  "employee_id": "MGR-003",
  "salary": 75000
}
```

---

## ✅ Testing Checklist

After seeding and importing collection:

### Database Verification
- [ ] 11 users created (2 admin, 2 manager, 3 cashier, 5 customer)
- [ ] All employees have addresses
- [ ] All customers have addresses
- [ ] 19 categories created
- [ ] 10 products created
- [ ] 3 carts with items
- [ ] 10 orders created

### Postman Testing
- [ ] Can login as all 4 roles
- [ ] Tokens auto-save correctly
- [ ] Customer registration includes address
- [ ] Cashier registration includes address
- [ ] Manager registration includes address
- [ ] GET /api/auth/me shows profile with address
- [ ] All CRUD operations work
- [ ] Permission tests return 403 as expected

---

## 🎯 Complete Testing Flow

### 1. Setup (5 minutes)
```bash
# Update models and routes
cp employee_FINAL.py app/models/employee.py
cp auth_routes_FINAL.py app/routes/auth_routes.py

# Migrate database
flask db migrate -m "Add address to Employee"
flask db upgrade

# Seed data
python seed_data.py
```

### 2. Import Postman (1 minute)
- Import collection v2
- Verify {{base_url}} = http://localhost:5000

### 3. Test Authentication (5 minutes)
- Run all 9 authentication requests
- Verify all tokens saved
- Check GET /me includes addresses

### 4. Test CRUD Operations (15 minutes)
- Categories: Create, read, update, delete
- Products: Full product management
- Cart: Add items, checkout
- Orders: Create and process orders

### 5. Test Permissions (5 minutes)
- Run permission test folder
- All should return 403 Forbidden

### 6. Verify Data (5 minutes)
```bash
flask shell
```
```python
from app.models import *
from app.extensions import db

# Check employee addresses
employee = Employee.query.first()
print(employee.full_name)
print(employee.full_address)

# Check customer addresses
customer = Customer.query.first()
print(customer.full_name)
print(f"{customer.address_line1}, {customer.city}")

# Verify counts
print(f"Users: {User.query.count()}")
print(f"Products: {Product.query.count()}")
print(f"Orders: {Order.query.count()}")
```

---

## 🎉 Success Criteria

✅ **Database:**
- All 11 users have complete profiles
- All employees have addresses
- Categories and products created
- Sample orders exist

✅ **API:**
- All authentication endpoints work
- Registration includes address validation
- GET /me returns profile with address
- All CRUD operations successful

✅ **Permissions:**
- RBAC working correctly
- Permission tests return 403
- Role-specific operations enforced

---

## 📚 Additional Resources

### Files Included:
1. `seed_data.py` - Database seeding script
2. `employee_FINAL.py` - Updated Employee model
3. `auth_routes_FINAL.py` - Updated authentication routes
4. `E-Commerce_API_v2_Complete.postman_collection.json` - Test collection
5. `README_TESTING_SETUP.md` - This file

### Documentation:
- DATABASE_DESIGN_ANALYSIS.md - Design decisions
- MIGRATION_GUIDE_EMPLOYEE_FIELDS.md - Migration instructions
- POSTMAN_TESTING_GUIDE.md - Testing guide

---

## 🚀 You're Ready to Test!

Everything is set up for comprehensive API testing with realistic seed data and complete address information for all user types.

**Happy Testing!** 🎊
