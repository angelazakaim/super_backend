import os

from flask_cors import CORS
from app import create_app
from app.extensions import db

app = create_app(os.getenv('FLASK_ENV', 'development'))


    
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
    app.run(debug=True, host='0.0.0.0', port=5000)