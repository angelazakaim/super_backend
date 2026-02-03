import os
from flask import Flask, jsonify
from flask_cors import CORS
from app.extensions import db, migrate, cors, jwt
from config import config_by_name
from app.utils.logger import setup_logger
from app.utils.middleware import setup_middleware

def create_app(config_name=None):
    """Application factory pattern."""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    # serving static files as well
    app = Flask(__name__, static_folder='static')
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))
    
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": app.config['CORS_ORIGINS'],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    }, supports_credentials=True)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Setup logging and middleware
    setup_logger(app)
    setup_middleware(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Error handlers
    register_error_handlers(app)
    
    # JWT callbacks
    register_jwt_callbacks(app)
    
    # =========================================================================
    # ROOT AND HEALTH ENDPOINTS
    # =========================================================================
    
    @app.route('/')
    def index():
        """Root endpoint - API information."""
        return jsonify({
            'name': 'Flask E-commerce API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'health': '/health',
                'api_docs': '/api',
                'auth': '/api/auth',
                'products': '/api/products',
                'categories': '/api/categories',
                'cart': '/api/cart',
                'orders': '/api/orders',
                'users': '/api/users'
            },
            'documentation': 'See README.md for full API documentation'
        }), 200
    
    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        return jsonify({'status': 'healthy'}), 200
    
    @app.route('/api')
    def api_info():
        """API information endpoint."""
        return jsonify({
            'message': 'Welcome to the E-commerce API',
            'version': '1.0.0',
            'endpoints': {
                'auth': {
                    'register': 'POST /api/auth/register',
                    'login': 'POST /api/auth/login',
                    'refresh': 'POST /api/auth/refresh',
                    'me': 'GET /api/auth/me',
                    'change_password': 'POST /api/auth/change-password'
                },
                'products': {
                    'list': 'GET /api/products',
                    'create': 'POST /api/products/add',
                    'update': 'PUT /api/products/<id>',
                    'delete': 'DELETE /api/products/<id>',
                    'upload_image': 'POST /api/products/upload-image'
                },
                'categories': {
                    'list': 'GET /api/categories',
                    'get': 'GET /api/categories/<id>',
                    'create': 'POST /api/categories',
                    'update': 'PUT /api/categories/<id>',
                    'delete': 'DELETE /api/categories/<id>'
                },
                'cart': {
                    'get': 'GET /api/cart',
                    'add_item': 'POST /api/cart/items',
                    'update_item': 'PUT /api/cart/items/<product_id>',
                    'remove_item': 'DELETE /api/cart/items/<product_id>',
                    'clear': 'POST /api/cart/clear'
                },
                'orders': {
                    'list': 'GET /api/orders',
                    'get': 'GET /api/orders/<id>',
                    'create': 'POST /api/orders',
                    'update_status': 'PUT /api/orders/<id>/status'
                },
                'users': {
                    'profile': 'GET /api/users/profile',
                    'update_profile': 'PUT /api/users/profile',
                    'list': 'GET /api/users (admin only)',
                    'customers': 'GET /api/users/customers',
                    'employees': 'GET /api/users/employees'
                }
            }
        }), 200
    
    return app

def register_blueprints(app):
    """Register Flask blueprints."""
    from app.routes.auth_routes import auth_bp
    from app.routes.product_routes import product_bp
    from app.routes.category_routes import category_bp
    from app.routes.cart_routes import cart_bp
    from app.routes.order_routes import order_bp
    from app.routes.user_routes import user_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(user_bp)

def register_error_handlers(app):
    """Register error handlers."""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400

def register_jwt_callbacks(app):
    """Register JWT callbacks."""
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired'}), 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'error': 'Invalid token'}), 401
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error):
        return jsonify({'error': 'Missing authorization token'}), 401