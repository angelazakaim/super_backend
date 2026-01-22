# E-Commerce Backend API

A comprehensive Flask-based e-commerce backend with JWT authentication, ORM models, and RESTful API endpoints.

## 📋 Features

- **Authentication & Authorization**: JWT-based auth with role-based access control (admin/customer)
- **User Management**: User registration, login, password management
- **Product Management**: CRUD operations for products with categories
- **Shopping Cart**: Add, update, remove items with stock validation
- **Order Processing**: Create orders from cart, track order status
- **Category System**: Hierarchical category structure
- **Middleware**: CORS, logging, authentication, security headers
- **Database**: Fully configurable PostgreSQL or SQLite with migrations

## 🏗️ Architecture

### Clean Architecture Pattern

```
app/
├── models/          # Database models (ORM entities)
├── repositories/    # Data access layer
├── services/        # Business logic layer
├── routes/          # API endpoints (controllers)
├── utils/           # Utilities and decorators
├── config.py        # Configuration management
└── extensions.py    # Flask extensions
```

### Models

1. **User** - Authentication and user management
2. **Customer** - Customer profiles with addresses
3. **Category** - Product categories (hierarchical)
4. **Product** - Products with pricing, stock, images
5. **Cart & CartItem** - Shopping cart functionality
6. **Order & OrderItem** - Order management and history

### Key Design Principles

- **Repository Pattern**: Abstracts database operations
- **Service Layer**: Encapsulates business logic
- **Dependency Injection**: Loose coupling between layers
- **Configuration Management**: Environment-based configs
- **Error Handling**: Comprehensive error responses

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+ (or SQLite for development)
- pip or poetry

### Installation

1. **Clone and setup virtual environment**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix/MacOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

2. **Configure environment**

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
nano .env
```

3. **Initialize database**

```bash
# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

4. **Run the application**

```bash
# Development mode
python run.py

# Or using Flask CLI
flask run
```

The API will be available at `http://localhost:5000`

### Docker Setup

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run migrations in container
docker-compose exec app flask db upgrade
```

## 📚 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1234567890"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email_or_username": "user@example.com",
  "password": "SecurePass123"
}

Response:
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "user": {...}
}
```

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer {access_token}
```

#### Refresh Token
```http
POST /api/auth/refresh
Authorization: Bearer {refresh_token}
```

### Product Endpoints

#### Get All Products
```http
GET /api/products?page=1&per_page=20&category_id=1&featured=true&search=laptop
```

#### Get Single Product
```http
GET /api/products/1
GET /api/products/slug/laptop-pro-15
```

#### Create Product (Admin)
```http
POST /api/products
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "Laptop Pro 15",
  "slug": "laptop-pro-15",
  "description": "High-performance laptop",
  "price": 1299.99,
  "compare_price": 1499.99,
  "sku": "LAP-PRO-15",
  "stock_quantity": 50,
  "category_id": 1,
  "is_featured": true
}
```

### Category Endpoints

#### Get All Categories
```http
GET /api/categories?parent_only=true
```

#### Get Category by ID
```http
GET /api/categories/1
GET /api/categories/slug/electronics
```

### Cart Endpoints

#### Get Cart
```http
GET /api/cart
Authorization: Bearer {access_token}
```

#### Add to Cart
```http
POST /api/cart/items
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "product_id": 1,
  "quantity": 2
}
```

#### Update Cart Item
```http
PUT /api/cart/items/1
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "quantity": 3
}
```

#### Remove from Cart
```http
DELETE /api/cart/items/1
Authorization: Bearer {access_token}
```

### Order Endpoints

#### Create Order
```http
POST /api/orders
Authorization: Bearer {access_token}
Content-Type: application/json

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
  "customer_notes": "Please deliver after 5 PM"
}
```

#### Get My Orders
```http
GET /api/orders?page=1&per_page=20
Authorization: Bearer {access_token}
```

#### Get Order Details
```http
GET /api/orders/1
Authorization: Bearer {access_token}
```

#### Update Order Status (Admin)
```http
PUT /api/orders/1/status
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "status": "shipped"
}
```

Valid statuses: `pending`, `confirmed`, `processing`, `shipped`, `delivered`, `cancelled`, `refunded`

## 🔐 Authentication & Authorization

### JWT Token Flow

1. User registers or logs in → receives `access_token` and `refresh_token`
2. Include access token in requests: `Authorization: Bearer {access_token}`
3. Access token expires after 1 hour (configurable)
4. Use refresh token to get new access token
5. Refresh token expires after 30 days (configurable)

### Role-Based Access Control

- **Customer**: Can manage their cart and orders, view products
- **Admin**: Full access to all resources, can manage products, categories, and all orders

### Protected Routes

Use decorators to protect routes:

```python
from flask_jwt_extended import jwt_required
from app.utils.decorators import admin_required

@product_bp.route('', methods=['POST'])
@jwt_required()
@admin_required()
def create_product():
    # Only admins can access
    pass
```

## 🗄️ Database Configuration

### PostgreSQL (Production)

```env
DATABASE_URL=postgresql://user:password@localhost:5432/ecommerce_prod
```

### SQLite (Development)

```env
DATABASE_URL=sqlite:///ecommerce.db
```

### Migrations

```bash
# Create new migration after model changes
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback migration
flask db downgrade
```

## 🛠️ Development

### Project Structure

```
SUPER_BACKEND/
├── app/
│   ├── models/              # Database models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── customer.py
│   │   ├── product.py
│   │   ├── category.py
│   │   ├── cart.py
│   │   └── order.py
│   ├── repositories/        # Data access layer
│   │   ├── __init__.py
│   │   ├── user_repository.py
│   │   ├── customer_repository.py
│   │   ├── product_repository.py
│   │   ├── category_repository.py
│   │   ├── cart_repository.py
│   │   └── order_repository.py
│   ├── services/            # Business logic
│   │   ├── auth_service.py
│   │   ├── cart_service.py
│   │   └── order_service.py
│   ├── routes/              # API endpoints
│   │   ├── auth_routes.py
│   │   ├── product_routes.py
│   │   ├── category_routes.py
│   │   ├── cart_routes.py
│   │   └── order_routes.py
│   ├── utils/               # Utilities
│   │   ├── decorators.py
│   │   ├── logger.py
│   │   └── middleware.py
│   ├── __init__.py          # App factory
│   ├── config.py            # Configuration
│   └── extensions.py        # Flask extensions
├── migrations/              # Database migrations
├── logs/                    # Application logs
├── .env                     # Environment variables
├── .env.example             # Example environment file
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
├── docker-compose.yml       # Docker compose config
├── Dockerfile               # Docker image config
└── README.md               # This file
```

### Adding New Models

1. Create model in `app/models/`
2. Create repository in `app/repositories/`
3. Create service in `app/services/` (if needed)
4. Create routes in `app/routes/`
5. Register blueprint in `app/__init__.py`
6. Run migrations

### Creating Admin User

```python
# Using Flask shell
flask shell

>>> from app.repositories.user_repository import UserRepository
>>> from app.repositories.customer_repository import CustomerRepository
>>> user = UserRepository.create(
...     email='admin@example.com',
...     username='admin',
...     password='SecurePassword123',
...     role='admin'
... )
>>> customer = CustomerRepository.create(
...     user_id=user.id,
...     first_name='Admin',
...     last_name='User'
... )
```

## 🧪 Testing

### Manual Testing with cURL

```bash
# Register user
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"Test123"}'

# Login
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email_or_username":"testuser","password":"Test123"}'

# Get products
curl http://localhost:5000/api/products

# Add to cart (requires token)
curl -X POST http://localhost:5000/api/cart/items \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id":1,"quantity":2}'
```

## 🔒 Security Best Practices

1. **Environment Variables**: Never commit `.env` file
2. **Strong Secrets**: Use strong, random SECRET_KEY and JWT_SECRET_KEY
3. **HTTPS**: Always use HTTPS in production
4. **Input Validation**: Validate all user inputs
5. **Rate Limiting**: Implement rate limiting (not included, use Flask-Limiter)
6. **SQL Injection**: Protected by SQLAlchemy ORM
7. **XSS Protection**: Security headers included in middleware
8. **CORS**: Configure allowed origins properly

## 📝 Configuration

### Environment Variables

- `FLASK_ENV`: Environment (development/production/testing)
- `SECRET_KEY`: Flask secret key
- `DATABASE_URL`: Database connection string
- `JWT_SECRET_KEY`: JWT signing key
- `JWT_ACCESS_TOKEN_EXPIRES`: Access token expiry (seconds)
- `JWT_REFRESH_TOKEN_EXPIRES`: Refresh token expiry (seconds)
- `CORS_ORIGINS`: Allowed CORS origins (comma-separated)
- `DEFAULT_PAGE_SIZE`: Default pagination size
- `MAX_PAGE_SIZE`: Maximum pagination size

## 🚀 Deployment

### Production Checklist

- [ ] Set `FLASK_ENV=production`
- [ ] Use strong secret keys
- [ ] Configure PostgreSQL database
- [ ] Set up HTTPS/SSL
- [ ] Configure CORS for your domain
- [ ] Set up logging and monitoring
- [ ] Use production WSGI server (gunicorn, uWSGI)
- [ ] Set up backup strategy
- [ ] Configure firewall rules
- [ ] Enable database connection pooling

### Example Production Setup (Gunicorn)

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app('production')"
```

## 📈 Performance Tips

1. **Database Indexing**: Indexes added on frequently queried fields
2. **Connection Pooling**: Configured in production settings
3. **Pagination**: Implemented on all list endpoints
4. **Lazy Loading**: Used for relationships where appropriate
5. **Caching**: Consider adding Redis for session/cache (not included)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## 📄 License

MIT License

## 🆘 Support

For issues and questions:
- Create an issue on GitHub
- Check documentation
- Review API examples

## 🔄 Changelog

### Version 1.0.0
- Initial release
- User authentication with JWT
- Product and category management
- Shopping cart functionality
- Order processing
- Admin role-based access control