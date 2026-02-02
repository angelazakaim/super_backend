# Flask E-commerce API

A full-featured e-commerce REST API built with Flask, featuring JWT authentication, role-based access control, shopping cart, and order management.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Authentication](#authentication)
- [Role-Based Access Control](#role-based-access-control)
- [Testing with Postman](#testing-with-postman)
- [Project Structure](#project-structure)

## ✨ Features

- **User Management**: Registration, authentication with JWT tokens
- **Role-Based Access**: Admin, Manager, Cashier, and Customer roles
- **Product Catalog**: Full CRUD operations with categories, search, and filtering
- **Shopping Cart**: Add, update, remove items with automatic total calculations
- **Order Management**: Create orders from cart, track status, manage payments
- **Image Upload**: Secure product image upload with validation
- **Security**: Password hashing, JWT tokens, role-based permissions

## 🛠 Tech Stack

- **Framework**: Flask 3.0.0
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: Flask-JWT-Extended
- **Validation**: Marshmallow
- **Image Processing**: Pillow
- **CORS**: Flask-CORS
- **Rate Limiting**: Flask-Limiter

## 📦 Installation

### Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd flask-ecommerce-api
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL Database

```sql
CREATE DATABASE ecommerce_db;
CREATE USER ecommerce_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ecommerce_db TO ecommerce_user;
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Flask Configuration
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here-change-in-production

# Database Configuration
DATABASE_URL=postgresql://ecommerce_user:your_password@localhost:5432/ecommerce_db

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-here
JWT_ACCESS_TOKEN_EXPIRES=3600  # 1 hour
JWT_REFRESH_TOKEN_EXPIRES=2592000  # 30 days

# File Upload Configuration
MAX_CONTENT_LENGTH=5242880  # 5MB in bytes
UPLOAD_FOLDER=app/static/uploads

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### Initialize Database

```bash
# Create database tables
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# (Optional) Seed database with sample data
python seed_data_go2market.py
```

## 🚀 Running the Application

### Development Server

```bash
python run.py
```

The API will be available at `http://localhost:5000`

### Production Server (with Gunicorn)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## 📚 API Documentation

### Base URL

```
http://localhost:5000/api
```

### Response Format

All responses follow this structure:

**Success:**
```json
{
  "message": "Success message",
  "data": { ... }
}
```

**Error:**
```json
{
  "error": "Error message",
  "details": { ... }
}
```

---

## 🔐 Authentication

### 1. Register User

**POST** `/api/auth/register`

Create a new user account.

**Request Body:**
```json
{
  "email": "customer@example.com",
  "username": "customer1",
  "password": "password123",
  "role": "customer",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "address_line1": "123 Main St",
  "city": "New York",
  "state": "NY",
  "postal_code": "10001",
  "country": "USA"
}
```

**Response (201):**
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "customer@example.com",
    "username": "customer1",
    "role": "customer"
  },
  "profile": {
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890"
  }
}
```

### 2. Login

**POST** `/api/auth/login`

Authenticate and receive JWT tokens.

**Request Body:**
```json
{
  "email_or_username": "customer@example.com",
  "password": "password123"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "customer@example.com",
    "role": "customer"
  }
}
```

### 3. Refresh Token

**POST** `/api/auth/refresh`

Get new access token using refresh token.

**Headers:**
```
Authorization: Bearer <refresh_token>
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 4. Get Current User

**GET** `/api/auth/me`

Get current authenticated user information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "user": {
    "id": 1,
    "email": "customer@example.com",
    "username": "customer1",
    "role": "customer"
  },
  "profile": {
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890"
  }
}
```

---

## 🛍️ Products

### 1. Get All Products

**GET** `/api/products`

Retrieve products with pagination and filters.

**Query Parameters:**
- `page` (int, default: 1)
- `per_page` (int, default: 20, max: 100)
- `category_id` (int, optional)
- `featured` (boolean, optional)

**Example:**
```
GET /api/products?page=1&per_page=20&category_id=1
```

**Response (200):**
```json
{
  "products": [
    {
      "id": 1,
      "name": "Product Name",
      "slug": "product-name",
      "description": "Product description",
      "price": 99.99,
      "compare_price": 129.99,
      "discount_percentage": 23.08,
      "sku": "SKU-001",
      "stock_quantity": 50,
      "is_in_stock": true,
      "category_id": 1,
      "image_url": "/static/uploads/products/image.jpg",
      "is_featured": true
    }
  ],
  "total": 100,
  "pages": 5,
  "current_page": 1,
  "per_page": 20
}
```

### 2. Search Products

Search by ID, SKU, slug, barcode, or name.

**GET** `/api/products?search_type=<type>&search_value=<value>`

**Search Types:**
- `id` - Search by product ID
- `sku` - Search by SKU
- `slug` - Search by URL slug
- `barcode` - Search by barcode
- `name` - Search by product name

**Examples:**
```
GET /api/products?search_type=sku&search_value=SKU-001
GET /api/products?search_type=name&search_value=laptop
GET /api/products?search_type=slug&search_value=gaming-laptop
```

### 3. Upload Product Image

**POST** `/api/products/upload-image`

Upload a product image. Returns image URL.

**Content-Type:** `multipart/form-data`

**Form Data:**
- `file` - Image file (png, jpg, jpeg, gif, webp, max 5MB)

**Response (201):**
```json
{
  "url": "/static/uploads/products/abc123.jpg"
}
```

### 4. Create Product

**POST** `/api/products/add`

Create a new product.

**Request Body:**
```json
{
  "name": "New Product",
  "description": "Product description",
  "price": 99.99,
  "compare_price": 129.99,
  "sku": "SKU-NEW-001",
  "barcode": "1234567890",
  "stock_quantity": 100,
  "category_id": 1,
  "weight": 1.5,
  "dimensions": "10x20x30 cm",
  "image_url": "/static/uploads/products/image.jpg",
  "is_active": true,
  "is_featured": false
}
```

### 5. Update Product

**PUT** `/api/products/:id`

Update an existing product.

**Request Body:** (partial updates allowed)
```json
{
  "name": "Updated Product Name",
  "price": 79.99,
  "stock_quantity": 50
}
```

### 6. Delete Product

**DELETE** `/api/products/:id`

Soft delete a product (sets is_active=false).

---

## 📁 Categories

### 1. Get All Categories

**GET** `/api/categories`

Get all categories with hierarchy.

**Query Parameters:**
- `parent_only` (boolean) - Only return top-level categories

**Response (200):**
```json
{
  "categories": [
    {
      "id": 1,
      "name": "Electronics",
      "slug": "electronics",
      "description": "Electronic devices",
      "parent_id": null,
      "children": [
        {
          "id": 2,
          "name": "Computers",
          "slug": "computers",
          "parent_id": 1
        }
      ],
      "products_count": 50
    }
  ]
}
```

### 2. Get Category by ID

**GET** `/api/categories/:id`

Get single category with children and products.

### 3. Get Category by Slug

**GET** `/api/categories/slug/:slug`

Get category by URL slug.

**Example:**
```
GET /api/categories/slug/electronics
```

### 4. Create Category (Admin Only)

**POST** `/api/categories`

Create a top-level category.

**Headers:**
```
Authorization: Bearer <admin_access_token>
```

**Request Body:**
```json
{
  "name": "New Category",
  "description": "Category description"
}
```

### 5. Create Subcategory (Manager+)

**POST** `/api/categories/:parent_id/subcategory`

Create a subcategory under existing category.

**Headers:**
```
Authorization: Bearer <manager_or_admin_token>
```

**Request Body:**
```json
{
  "name": "Subcategory Name",
  "description": "Subcategory description"
}
```

### 6. Update Category (Manager+)

**PUT** `/api/categories/:id`

Update category name/description.

### 7. Delete Category (Admin Only)

**DELETE** `/api/categories/:id`

Delete category (checks for products and children first).

---

## 🛒 Shopping Cart

All cart endpoints require authentication.

### 1. Get Cart

**GET** `/api/cart`

Get current user's shopping cart.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": 1,
  "customer_id": 1,
  "total_items": 5,
  "subtotal": 499.95,
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "product": {
        "id": 1,
        "name": "Product Name",
        "price": 99.99,
        "image_url": "/static/uploads/products/image.jpg"
      },
      "quantity": 2,
      "unit_price": 99.99,
      "total_price": 199.98
    }
  ]
}
```

### 2. Add to Cart

**POST** `/api/cart/items`

Add product to cart.

**Request Body:**
```json
{
  "product_id": 1,
  "quantity": 2
}
```

**Response (200):**
```json
{
  "message": "Item added to cart",
  "cart": { ... }
}
```

### 3. Update Cart Item

**PUT** `/api/cart/items/:product_id`

Update quantity of cart item.

**Request Body:**
```json
{
  "quantity": 5
}
```

### 4. Remove from Cart

**DELETE** `/api/cart/items/:product_id`

Remove item from cart.

**Response (200):**
```json
{
  "message": "Item removed from cart",
  "cart": { ... }
}
```

### 5. Clear Cart

**POST** `/api/cart/clear`

Remove all items from cart.

### 6. Validate Cart

**GET** `/api/cart/validate`

Validate cart is ready for checkout.

**Response (200):**
```json
{
  "valid": true,
  "message": "Cart is valid for checkout"
}
```

---

## 📦 Orders

### Customer Endpoints

#### 1. Create Order from Cart

**POST** `/api/orders`

Create order from cart items.

**Headers:**
```
Authorization: Bearer <customer_token>
```

**Request Body:**
```json
{
  "shipping_address": {
    "line1": "123 Main St",
    "line2": "Apt 4B",
    "city": "New York",
    "state": "NY",
    "postal_code": "10001",
    "country": "USA"
  },
  "payment_method": "credit_card",
  "customer_notes": "Please deliver after 6 PM"
}
```

**Response (201):**
```json
{
  "message": "Order created successfully",
  "order": {
    "id": 1,
    "order_number": "ORD-20240101-001",
    "status": "pending",
    "payment_status": "pending",
    "subtotal": 199.98,
    "tax": 15.99,
    "shipping_cost": 10.00,
    "total": 225.97,
    "items": [ ... ]
  }
}
```

#### 2. Get My Orders

**GET** `/api/orders?page=1&per_page=20`

Get current user's orders with pagination.

**Response (200):**
```json
{
  "orders": [ ... ],
  "total": 10,
  "pages": 1,
  "current_page": 1,
  "per_page": 20
}
```

#### 3. Get Order by ID

**GET** `/api/orders/:id`

Get order details. Customers can only see their own orders.

#### 4. Cancel Order

**POST** `/api/orders/:id/cancel`

Cancel own order (if status allows).

**Response (200):**
```json
{
  "message": "Order cancelled successfully",
  "order": { ... }
}
```

### Staff Endpoints (Cashier, Manager, Admin)

#### 1. Get Today's Orders

**GET** `/api/orders/today`

Get all orders placed today for daily operations.

**Headers:**
```
Authorization: Bearer <staff_token>
```

#### 2. Search Order by Number

**GET** `/api/orders/search?number=ORD-20240101-001`

Quick order lookup by order number.

#### 3. Update Order Status

**POST** `/api/orders/:id/status`

Update order status.

**Request Body:**
```json
{
  "status": "confirmed"
}
```

**Valid Statuses:**
- `pending`
- `confirmed`
- `processing`
- `shipped`
- `delivered`
- `cancelled`

#### 4. Update Payment Status

**POST** `/api/orders/:id/payment-status`

Update payment status.

**Request Body:**
```json
{
  "payment_status": "paid"
}
```

**Valid Statuses:**
- `pending`
- `paid`
- `failed`
- `refunded` (admin only)

#### 5. Mark as Shipped

**POST** `/api/orders/:id/ship`

Mark order as shipped with optional tracking.

**Request Body:**
```json
{
  "tracking_number": "TRACK123456789"
}
```

### Manager Endpoints (Manager, Admin)

#### 1. Get All Orders

**GET** `/api/orders/admin?page=1&per_page=20&status=pending`

View all orders with filters.

**Access:**
- **Manager**: Last 30 days only
- **Admin**: All orders, no time limit

**Query Parameters:**
- `page` (int)
- `per_page` (int)
- `status` (string, optional)

#### 2. Add Order Notes

**POST** `/api/orders/:id/notes`

Add internal notes to order.

**Request Body:**
```json
{
  "notes": "Customer requested expedited shipping"
}
```

### Admin Endpoints

#### 1. Process Refund

**POST** `/api/orders/:id/refund`

Process refund for order. Admin only.

**Request Body:**
```json
{
  "reason": "Product defect"
}
```

#### 2. Delete Order

**DELETE** `/api/orders/:id`

Permanently delete order. Cannot be undone!

---

## 👥 User Management

### Profile Endpoints (Authenticated Users)

#### 1. Get My Profile

**GET** `/api/users/profile`

Get current user's full profile.

#### 2. Update My Profile

**PUT** `/api/users/profile`

Update own profile information.

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "address_line1": "456 New St",
  "city": "Boston",
  "state": "MA",
  "postal_code": "02101"
}
```

### Manager Endpoints

#### 1. Get All Customers

**GET** `/api/users/customers?page=1&per_page=25`

View all customers with pagination.

#### 2. Get All Employees

**GET** `/api/users/employees?page=1&per_page=25&role=manager`

View all employees with optional role filter.

### Admin Endpoints

#### 1. Get All Users

**GET** `/api/users?page=1&per_page=25&role=customer`

Get all users with optional role filter.

#### 2. Get User by ID

**GET** `/api/users/:id`

Get specific user details.

#### 3. Update User

**PUT** `/api/users/:id`

Update user account.

**Request Body:**
```json
{
  "email": "newemail@example.com",
  "username": "newusername",
  "is_active": true
}
```

#### 4. Ban User

**POST** `/api/users/:id/ban`

Disable user account (sets is_active=false).

#### 5. Unban User

**POST** `/api/users/:id/unban`

Re-enable user account.

#### 6. Change User Role

**PUT** `/api/users/:id/role`

Change user role and create appropriate profile.

**Request Body:**
```json
{
  "role": "manager",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890",
  "employee_id": "EMP-001",
  "salary": 60000
}
```

**Valid Roles:**
- `admin`
- `customer`
- `manager`
- `cashier`

#### 7. Reset User Password

**POST** `/api/users/:id/password-reset`

Admin reset user password.

**Request Body:**
```json
{
  "new_password": "newpassword123"
}
```

#### 8. Delete User

**DELETE** `/api/users/:id`

Permanently delete user. Cannot undo!

#### 9. Get User Statistics

**GET** `/api/users/statistics`

Get user counts and analytics.

**Response (200):**
```json
{
  "total_users": 1000,
  "active_users": 950,
  "by_role": {
    "customer": 900,
    "cashier": 30,
    "manager": 10,
    "admin": 5
  }
}
```

---

## 🔒 Role-Based Access Control

### Roles Hierarchy

```
Admin (Full Access)
  ↓
Manager (Manage operations, view reports)
  ↓
Cashier (Process orders, view today's data)
  ↓
Customer (Shopping, cart, own orders)
```

### Permission Matrix

| Endpoint | Customer | Cashier | Manager | Admin |
|----------|----------|---------|---------|-------|
| **Products** |
| View Products | ✓ | ✓ | ✓ | ✓ |
| Create Product | ✗ | ✗ | ✗ | ✗ |
| Update Product | ✗ | ✗ | ✗ | ✗ |
| Delete Product | ✗ | ✗ | ✗ | ✗ |
| **Categories** |
| View Categories | ✓ | ✓ | ✓ | ✓ |
| Create Top Category | ✗ | ✗ | ✗ | ✓ |
| Create Subcategory | ✗ | ✗ | ✓ | ✓ |
| Update Category | ✗ | ✗ | ✓ | ✓ |
| Delete Category | ✗ | ✗ | ✗ | ✓ |
| **Cart** |
| Manage Own Cart | ✓ | ✓ | ✓ | ✓ |
| **Orders** |
| Create Order | ✓ | ✓ | ✓ | ✓ |
| View Own Orders | ✓ | ✗ | ✗ | ✗ |
| Cancel Own Order | ✓ | ✗ | ✗ | ✗ |
| View Today's Orders | ✗ | ✓ | ✓ | ✓ |
| Update Order Status | ✗ | ✓ | ✓ | ✓ |
| View All Orders | ✗ | ✗ | ✓* | ✓ |
| Process Refund | ✗ | ✗ | ✗ | ✓ |
| Delete Order | ✗ | ✗ | ✗ | ✓ |
| **Users** |
| View Own Profile | ✓ | ✓ | ✓ | ✓ |
| Update Own Profile | ✓ | ✓ | ✓ | ✓ |
| View Customers | ✗ | ✗ | ✓ | ✓ |
| View Employees | ✗ | ✗ | ✓ | ✓ |
| Manage Users | ✗ | ✗ | ✗ | ✓ |
| Change Roles | ✗ | ✗ | ✗ | ✓ |

*Manager can view last 30 days only

---

## 🧪 Testing with Postman

### 1. Import Collection

1. Download `Flask_Ecommerce_API.postman_collection.json`
2. Open Postman
3. Click **Import** → Select file
4. Collection will be imported with all endpoints

### 2. Set Up Environment

The collection includes these variables:
- `base_url` - API base URL (default: http://localhost:5000)
- `access_token` - JWT access token (auto-set on login)
- `refresh_token` - JWT refresh token (auto-set on login)

### 3. Quick Start Testing

**Step 1: Register a User**
```
POST /api/auth/register
```
Create accounts for different roles (customer, manager, cashier).

**Step 2: Login**
```
POST /api/auth/login
```
Login saves tokens automatically to environment variables.

**Step 3: Test Endpoints**

All subsequent requests will use the saved access token automatically.

### 4. Test Different Roles

To test role-based permissions:

1. Register/login as customer → Test customer endpoints
2. Register/login as cashier → Test staff endpoints
3. Login as manager → Test manager endpoints
4. Login as admin → Test admin endpoints

### 5. Auto-Token Refresh

The collection includes a test script in the Login request that automatically saves tokens:

```javascript
if (pm.response.code === 200) {
    const response = pm.response.json();
    pm.environment.set('access_token', response.access_token);
    pm.environment.set('refresh_token', response.refresh_token);
}
```

---

## 📂 Project Structure

```
flask-ecommerce-api/
├── app/
│   ├── __init__.py          # App factory
│   ├── extensions.py        # Flask extensions
│   ├── enums.py            # Enums (roles, statuses)
│   ├── models/             # Database models
│   │   ├── user.py
│   │   ├── customer.py
│   │   ├── employee.py
│   │   ├── product.py
│   │   ├── category.py
│   │   ├── cart.py
│   │   ├── cart_item.py
│   │   ├── order.py
│   │   └── order_item.py
│   ├── routes/             # API routes
│   │   ├── auth_routes.py
│   │   ├── user_routes.py
│   │   ├── product_routes.py
│   │   ├── category_routes.py
│   │   ├── cart_routes.py
│   │   └── order_routes.py
│   ├── services/           # Business logic
│   ├── repositories/       # Database operations
│   ├── schemas/            # Marshmallow schemas
│   ├── utils/              # Utilities & decorators
│   └── static/             # Static files
│       └── uploads/        # Uploaded images
├── migrations/             # Database migrations
├── .env                    # Environment variables
├── requirements.txt        # Dependencies
├── run.py                 # Application entry point
└── seed_new.py            # Database seeder
```

---

## 🔧 Common Issues & Solutions

### Issue: Database Connection Error

**Error:** `OperationalError: could not connect to server`

**Solution:**
1. Check PostgreSQL is running: `sudo service postgresql status`
2. Verify database credentials in `.env`
3. Ensure database exists: `psql -U postgres -c "\l"`

### Issue: JWT Token Expired

**Error:** `401 Unauthorized - Token has expired`

**Solution:**
Use the refresh token endpoint to get a new access token:
```
POST /api/auth/refresh
Authorization: Bearer <refresh_token>
```

### Issue: Image Upload Fails

**Error:** `413 Request Entity Too Large`

**Solution:**
Check `MAX_CONTENT_LENGTH` in `.env` (default: 5MB)

### Issue: Permission Denied

**Error:** `403 Forbidden - Insufficient permissions`

**Solution:**
- Verify you're logged in with correct role
- Check role permissions in documentation
- Admin account may be required

---

## 📝 API Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Authentication required or failed |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 500 | Internal Server Error | Server error occurred |

---

## 🔐 Security Best Practices

1. **Environment Variables**: Never commit `.env` file to version control
2. **JWT Secrets**: Use strong, random secrets in production
3. **Password Policy**: Enforce minimum 8 characters
4. **HTTPS**: Always use HTTPS in production
5. **CORS**: Configure allowed origins properly
6. **Rate Limiting**: Implement rate limiting on sensitive endpoints
7. **Input Validation**: All inputs are validated using Marshmallow schemas
8. **SQL Injection**: Protected by SQLAlchemy ORM
9. **Image Upload**: Files validated for type and size

---

## 📊 Database Schema

### Users & Profiles
- `users` - User accounts with authentication
- `customers` - Customer profiles (extends users)
- `employees` - Employee profiles (extends users)

### Products
- `categories` - Product categories (hierarchical)
- `products` - Product catalog

### Shopping
- `carts` - Shopping carts
- `cart_items` - Items in carts

### Orders
- `orders` - Order headers
- `order_items` - Order line items

---

## 🚀 Deployment

### Environment Variables for Production

```env
FLASK_ENV=production
SECRET_KEY=<strong-random-key>
JWT_SECRET_KEY=<strong-random-key>
DATABASE_URL=postgresql://user:password@host:5432/database
```

### Using Docker (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

Build and run:
```bash
docker build -t flask-ecommerce .
docker run -p 5000:5000 --env-file .env flask-ecommerce
```

---

## 📞 Support

For issues or questions:
1. Check this README
2. Review API documentation above
3. Test with Postman collection
4. Check application logs

---

## 📄 License

[Your License Here]

---

## 👥 Contributors

[Your Name/Team]

---

**Last Updated:** February 2026
