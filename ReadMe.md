# Flask E-commerce API

A full-featured e-commerce REST API built with Flask, featuring JWT authentication, role-based access control, shopping cart, and order management.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start with Docker](#-quick-start-with-docker)
- [Local Development Setup](#-local-development-setup)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Authentication](#authentication)
- [Role-Based Access Control](#role-based-access-control)
- [Testing Your Deployment](#-testing-your-deployment)
- [Testing with Postman](#testing-with-postman)
- [Project Structure](#project-structure)
- [Troubleshooting](#-troubleshooting)

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
- **Database**: SQLite (dev) / PostgreSQL (production) / SQL Server (enterprise)
- **Authentication**: Flask-JWT-Extended
- **Validation**: Marshmallow
- **Image Processing**: Pillow
- **CORS**: Flask-CORS
- **Rate Limiting**: Flask-Limiter
- **Containerization**: Docker & Docker Compose

---

## 🐳 Quick Start with Docker

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- Git (to clone the repository)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd AngelaZakaim
```

### Step 2: Clean Up Previous Docker Data (Optional)

If you've run this project before and want a fresh start:

```bash
# Stop and remove all project containers, volumes, and images
docker-compose -f docker-compose.dev.yml down -v --rmi local

# Or for a complete Docker cleanup (removes ALL unused Docker data)
docker system prune -a --volumes -f
```

### Step 3: Update docker-compose.dev.yml

Make sure the `DATABASE_URL` has the correct path (4 slashes for absolute path):

```yaml
environment:
  - DATABASE_URL=sqlite:////app/instance/ecommerce_dev.db
```

### Step 4: Build and Start Containers

```bash
# Build and start all services
docker-compose -f docker-compose.dev.yml up -d --build
```

### Step 5: Verify Containers are Running

```bash
# Check container status
docker ps

# You should see:
# - ecommerce-backend-dev (port 5000)
# - ecommerce-frontend-dev (port 5173)
```

### Step 6: Initialize the Database

```bash
# Initialize Flask-Migrate
docker exec -it ecommerce-backend-dev flask db init

# Create migration files
docker exec -it ecommerce-backend-dev flask db migrate -m "initial_setup"

# Apply migrations to create tables
docker exec -it ecommerce-backend-dev flask db upgrade
```

### Step 7: Seed the Database (Optional but Recommended)

```bash
# Run the seed script to populate with test data
docker exec -it ecommerce-backend-dev python seed_data_go2market.py
```

This creates:
- 53 users (1 admin, 1 manager, 1 cashier, 50 customers)
- 150 products across 13 categories
- 100 sample orders

### Step 8: Access the Application

| Service | URL |
|---------|-----|
| Backend API | http://localhost:5000 |
| Frontend | http://localhost:5173 |
| API Health Check | http://localhost:5000/api/health |

---

## 🔄 Docker Commands Reference

### Starting and Stopping

```bash
# Start containers
docker-compose -f docker-compose.dev.yml up -d

# Stop containers (keeps data)
docker-compose -f docker-compose.dev.yml down

# Stop containers and remove volumes (deletes database)
docker-compose -f docker-compose.dev.yml down -v

# Restart containers
docker-compose -f docker-compose.dev.yml restart
```

### Viewing Logs

```bash
# View all logs
docker-compose -f docker-compose.dev.yml logs

# View backend logs only
docker-compose -f docker-compose.dev.yml logs backend

# Follow logs in real-time
docker-compose -f docker-compose.dev.yml logs -f backend
```

### Executing Commands in Container

```bash
# Open bash shell in backend container
docker exec -it ecommerce-backend-dev bash

# Run Flask shell (for debugging)
docker exec -it ecommerce-backend-dev flask shell

# Run a Python script
docker exec -it ecommerce-backend-dev python your_script.py

# Check environment variables
docker exec -it ecommerce-backend-dev printenv DATABASE_URL
```

### Database Management

```bash
# Create new migration after model changes
docker exec -it ecommerce-backend-dev flask db migrate -m "description of changes"

# Apply migrations
docker exec -it ecommerce-backend-dev flask db upgrade

# Rollback last migration
docker exec -it ecommerce-backend-dev flask db downgrade

# View migration history
docker exec -it ecommerce-backend-dev flask db history
```

### Rebuilding

```bash
# Rebuild after code changes (usually not needed due to volume mount)
docker-compose -f docker-compose.dev.yml up -d --build

# Force rebuild without cache
docker-compose -f docker-compose.dev.yml build --no-cache
docker-compose -f docker-compose.dev.yml up -d
```

### Complete Reset

```bash
# Nuclear option - complete fresh start
docker-compose -f docker-compose.dev.yml down -v
rmdir /s /q azakaim_backend\migrations   # Windows
# rm -rf azakaim_backend/migrations      # Linux/Mac
docker-compose -f docker-compose.dev.yml up -d --build
docker exec -it ecommerce-backend-dev flask db init
docker exec -it ecommerce-backend-dev flask db migrate -m "initial_setup"
docker exec -it ecommerce-backend-dev flask db upgrade
docker exec -it ecommerce-backend-dev python seed_data_go2market.py
```

---

## 🧪 Testing Your Deployment

### Quick Commands to Test Your Docker Environment

#### Step 1: Check Containers are Running

```bash
docker ps
```

You should see `ecommerce-backend-dev` and `ecommerce-frontend-dev` running.

#### Step 2: Check Database URL is Correct

```bash
docker exec -it ecommerce-backend-dev printenv DATABASE_URL
```

Should show: `sqlite:////app/instance/ecommerce_dev.db`

#### Step 3: Test API Health

Open in browser or use curl:

```bash
curl http://localhost:5000/api/health
```

Or just open: **http://localhost:5000/api/products** in your browser.

#### Step 4: Test Login (After Seeding)

```bash
curl -X POST http://localhost:5000/api/auth/login -H "Content-Type: application/json" -d "{\"email_or_username\": \"admin@ecommerce.com\", \"password\": \"Admin123!\"}"
```

If successful, you'll get back an `access_token`.

#### Step 5: Test Products Endpoint

```bash
curl "http://localhost:5000/api/products?page=1&per_page=5"
```

#### Step 6: Check Frontend

Open: **http://localhost:5173** in your browser.

### Quick Summary Table

| Test | Command/URL | Expected Result |
|------|-------------|-----------------|
| Containers running | `docker ps` | 2 containers listed |
| Database URL | `docker exec -it ecommerce-backend-dev printenv DATABASE_URL` | `sqlite:////app/instance/ecommerce_dev.db` |
| Backend API | http://localhost:5000/api/products | JSON with products |
| Frontend | http://localhost:5173 | React app loads |
| Login | POST to /api/auth/login | Returns access_token |

> ✅ **Available Test URLs:**
> - `http://localhost:5000/` - API info and available endpoints
> - `http://localhost:5000/health` - Health check
> - `http://localhost:5000/api` - Detailed API documentation
> - `http://localhost:5000/api/products` - Get products
> - `http://localhost:5000/api/categories` - Get categories
> - `http://localhost:5000/api/auth/login` - Login endpoint

### If Tests Fail

If you get empty results or errors, the database might not be set up yet:

```bash
# Apply migrations
docker exec -it ecommerce-backend-dev flask db upgrade

# Seed the database with test data
docker exec -it ecommerce-backend-dev python seed_data_go2market.py
```

Then test again:

```bash
curl "http://localhost:5000/api/products?page=1&per_page=5"
```

### Test Authentication Flow

#### 1. Register a New User

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "Test123!",
    "role": "customer",
    "first_name": "Test",
    "last_name": "User",
    "phone": "555-1234"
  }'
```

#### 2. Login (Using Seeded Account)

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_username": "admin@ecommerce.com",
    "password": "Admin123!"
  }'
```

Save the `access_token` from the response for subsequent requests.

#### 3. Test Protected Endpoint

```bash
curl http://localhost:5000/api/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

### Test API Endpoints

#### Get Products (Public)

```bash
curl "http://localhost:5000/api/products?page=1&per_page=10"
```

#### Get Categories (Public)

```bash
curl http://localhost:5000/api/categories
```

#### Get Orders (Requires Auth)

```bash
curl http://localhost:5000/api/orders \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

### Test Accounts (After Seeding)

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@ecommerce.com | Admin123! |
| Manager | manager@ecommerce.com | Manager123! |
| Cashier | cashier@ecommerce.com | Cashier123! |
| Customer | customer1@email.com | Customer123! |
| Customer | customer2@email.com | Customer123! |
| ... | customer3-50@email.com | Customer123! |

### Pagination Testing

The seeded database includes 150 products and 100 orders for testing pagination:

```bash
# First page of products
curl "http://localhost:5000/api/products?page=1&per_page=20"

# Second page
curl "http://localhost:5000/api/products?page=2&per_page=20"

# Last page (should have fewer items)
curl "http://localhost:5000/api/products?page=8&per_page=20"

# Test different page sizes
curl "http://localhost:5000/api/products?page=1&per_page=50"
```

### Using Postman

1. Import the Postman collection (if provided)
2. Set environment variable `base_url` = `http://localhost:5000`
3. Run "Login" request first (tokens are auto-saved)
4. Test other endpoints

---

## 💻 Local Development Setup

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### 1. Clone and Setup Virtual Environment

```bash
git clone <repository-url>
cd azakaim_backend

# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# For local development (SQLite, no SQL Server driver)
pip install -r requirements-local.txt

# For full installation (includes PostgreSQL and SQL Server drivers)
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:///instance/ecommerce_dev.db
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600
JWT_REFRESH_TOKEN_EXPIRES=2592000
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 4. Initialize Database

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Seed with test data
python seed_data_go2market.py
```

### 5. Run the Application

```bash
python run.py
```

The API will be available at `http://localhost:5000`

---

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `FLASK_ENV` | Environment (development/production) | development |
| `SECRET_KEY` | Flask secret key | (required) |
| `DATABASE_URL` | Database connection string | sqlite:///instance/ecommerce_dev.db |
| `JWT_SECRET_KEY` | JWT signing key | (required) |
| `JWT_ACCESS_TOKEN_EXPIRES` | Access token TTL (seconds) | 3600 |
| `JWT_REFRESH_TOKEN_EXPIRES` | Refresh token TTL (seconds) | 2592000 |
| `CORS_ORIGINS` | Allowed CORS origins | * |
| `DEFAULT_PAGE_SIZE` | Default pagination size | 20 |
| `MAX_PAGE_SIZE` | Maximum pagination size | 100 |

### Database URL Formats

```bash
# SQLite (Development)
DATABASE_URL=sqlite:////app/instance/ecommerce_dev.db  # Docker (absolute path)
DATABASE_URL=sqlite:///instance/ecommerce_dev.db       # Local (relative path)

# PostgreSQL (Production - Render/Heroku)
DATABASE_URL=postgresql://user:password@host:5432/database

# SQL Server (Enterprise)
DATABASE_URL=mssql+pyodbc://user:password@host:1433/database?driver=ODBC+Driver+18+for+SQL+Server
```

---

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
| Create Product | ✗ | ✗ | ✓ | ✓ |
| Update Product | ✗ | ✗ | ✓ | ✓ |
| Delete Product | ✗ | ✗ | ✗ | ✓ |
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

---

## 📂 Project Structure

```
AngelaZakaim/
├── docker-compose.dev.yml      # Docker development config
├── azakaim_backend/
│   ├── app/
│   │   ├── __init__.py         # App factory
│   │   ├── extensions.py       # Flask extensions
│   │   ├── enums.py            # Enums (roles, statuses)
│   │   ├── models/             # Database models
│   │   │   ├── user.py
│   │   │   ├── customer.py
│   │   │   ├── employee.py
│   │   │   ├── product.py
│   │   │   ├── category.py
│   │   │   ├── cart.py
│   │   │   ├── cart_item.py
│   │   │   ├── order.py
│   │   │   └── order_item.py
│   │   ├── routes/             # API routes
│   │   │   ├── auth_routes.py
│   │   │   ├── user_routes.py
│   │   │   ├── product_routes.py
│   │   │   ├── category_routes.py
│   │   │   ├── cart_routes.py
│   │   │   └── order_routes.py
│   │   ├── services/           # Business logic
│   │   ├── repositories/       # Database operations
│   │   ├── schemas/            # Marshmallow schemas
│   │   ├── utils/              # Utilities & decorators
│   │   └── static/             # Static files
│   │       └── uploads/        # Uploaded images
│   ├── migrations/             # Database migrations (auto-generated)
│   ├── instance/               # SQLite database (Docker volume)
│   ├── .env                    # Environment variables
│   ├── Dockerfile              # Backend Docker image
│   ├── requirements.txt        # Production dependencies
│   ├── requirements-local.txt  # Local dev dependencies
│   ├── config.py               # Flask configuration
│   ├── run.py                  # Application entry point
│   ├── wsgi.py                 # WSGI entry point (production)
│   └── seed_data_go2market.py  # Database seeder
└── azakaim_frontend/
    ├── Dockerfile.dev          # Frontend Docker image
    ├── src/                    # React source code
    └── ...
```

---

## 🔧 Troubleshooting

### Issue: "unable to open database file"

**Cause:** Incorrect DATABASE_URL path

**Solution:**
```yaml
# In docker-compose.dev.yml, use absolute path (4 slashes):
DATABASE_URL=sqlite:////app/instance/ecommerce_dev.db
```

### Issue: "Directory migrations already exists"

**Cause:** Running `flask db init` when migrations folder exists

**Solution:**
```bash
# Skip init and run migrate directly
docker exec -it ecommerce-backend-dev flask db migrate -m "your_message"
docker exec -it ecommerce-backend-dev flask db upgrade

# Or delete and start fresh
docker exec -it ecommerce-backend-dev rm -rf /app/migrations
docker exec -it ecommerce-backend-dev flask db init
```

### Issue: Container won't start

**Solution:**
```bash
# Check logs
docker-compose -f docker-compose.dev.yml logs backend

# Verify environment
docker exec -it ecommerce-backend-dev printenv DATABASE_URL
```

### Issue: Database Connection Error (PostgreSQL)

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

### Issue: Changes not reflecting in container

**Solution:**
```bash
# Volume mounts should auto-sync, but if not:
docker-compose -f docker-compose.dev.yml restart backend

# Or rebuild
docker-compose -f docker-compose.dev.yml up -d --build
```

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

## 🚀 Production Deployment

### Environment Variables for Production

```env
FLASK_ENV=production
SECRET_KEY=<strong-random-key>
JWT_SECRET_KEY=<strong-random-key>
DATABASE_URL=postgresql://user:password@host:5432/database
```

### Deploy to Render/Heroku

1. Push code to GitHub
2. Connect repository to Render/Heroku
3. Set environment variables
4. Deploy

### Using Docker in Production

```bash
# Build production image
docker build -t flask-ecommerce .

# Run with production settings
docker run -p 5000:5000 \
  -e FLASK_ENV=production \
  -e DATABASE_URL=postgresql://... \
  -e SECRET_KEY=your-secret \
  -e JWT_SECRET_KEY=your-jwt-secret \
  flask-ecommerce
```

---

## 📞 Support

For issues or questions:
1. Check this README
2. Review API documentation above
3. Test with Postman collection
4. Check application logs: `docker-compose logs backend`

---

## 📄 License

[Your License Here]

---

## 👥 Contributors

[Your Name/Team]

---

**Last Updated:** February 2026
