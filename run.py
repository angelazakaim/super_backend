import os
from flask_cors import CORS
from app import create_app
from app.extensions import db

# 1. FIX DATABASE URL 
# Render provides 'postgres://', but SQLAlchemy 1.4+ requires 'postgresql://'
uri = os.getenv("DATABASE_URL")
if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

# Set it back into the environment so the create_app factory can access it
if uri:
    os.environ["DATABASE_URL"] = uri

# 2. INITIALIZE APP
# Defaulting to 'production' if no environment is specified
env = os.getenv('FLASK_ENV', 'production')
app = create_app(env)

# Explicitly ensure the app configuration uses the corrected URI
app.config["SQLALCHEMY_DATABASE_URI"] = uri

# 3. CONFIGURE CORS
# Pulls the frontend URL from the environment variable set in render.yaml
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
CORS(app, resources={r"/*": {"origins": cors_origins}})

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
    # Render assigns a dynamic port via the PORT environment variable
    port = int(os.getenv("PORT", 5000))
    # In production, this block is bypassed by Gunicorn
    app.run(host='0.0.0.0', port=port)