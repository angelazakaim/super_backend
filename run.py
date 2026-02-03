import os

from app import create_app
from app.extensions import db

# 1. FIX DATABASE URL
# Handle different database URL formats:
# - Render provides 'postgres://', but SQLAlchemy 1.4+ requires 'postgresql://'
# - SQL Server uses 'mssql+pyodbc://' (no conversion needed)
uri = os.getenv("DATABASE_URL")

if uri:
    # Only convert PostgreSQL URLs
    if uri.startswith("postgres://") and not uri.startswith("postgresql://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
        os.environ["DATABASE_URL"] = uri
    # SQL Server URLs (mssql+pyodbc://) don't need conversion
    # SQLite URLs (sqlite:///) don't need conversion

# 2. INITIALIZE APP
# Defaulting to 'production' if no environment is specified
env = os.getenv('FLASK_ENV', 'production')
app = create_app(env)

# Explicitly ensure the app configuration uses the corrected URI
if uri:
    app.config["SQLALCHEMY_DATABASE_URI"] = uri


@app.shell_context_processor
def make_shell_context():
    """Create shell context for flask shell command."""
    from app.models import User, Customer, Category, Product, Cart, CartItem, Order, OrderItem
    return {
        'db': db,
        'User': User,
        'Customer': Customer,
        'Category': Category,
        'Product': Product,
        'Cart': Cart,
        'CartItem': CartItem,
        'Order': Order,
        'OrderItem': OrderItem
    }

if __name__ == '__main__':
    # For development and local testing
    port = int(os.getenv("PORT", 5000))
    # In production, this block is bypassed by Gunicorn
    app.run(host='0.0.0.0', port=port, debug=(env == 'development'))
