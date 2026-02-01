"""Product Routes – list, search, CRUD, and image upload."""
from flask import Blueprint, request, jsonify, current_app
from app.services.product_service import ProductService
from PIL import Image
import logging
import os
import uuid

logger = logging.getLogger(__name__)

product_bp = Blueprint('products', __name__, url_prefix='/api/products')

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def _allowed_file(filename: str) -> bool:
    """Return True when *filename* ends with an allowed image extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ---------------------------------------------------------------------------
# Routes
#   GET    /api/products              – list / search
#   POST   /api/products/upload-image – upload one image, get its URL back
#   POST   /api/products/add          – create a product
#   PUT    /api/products/<id>         – update a product
#   DELETE /api/products/<id>         – soft-delete a product
# ---------------------------------------------------------------------------


@product_bp.route('', methods=['GET'])
def get_products():
    """
    UNIFIED ENDPOINT: Handles all product retrieval and search operations.

    Query Parameters:
        - page (int): Page number (default: 1)
        - per_page (int): Items per page (default: 20, max: 100)
        - category_id (int): Filter by category
        - featured (bool): Only featured products
        - search_type (str): 'id' | 'sku' | 'slug' | 'barcode' | 'category_id' | 'name'
        - search_value (str/int): Value to search for
        
    Examples:
        GET /api/products                                           # All products
        GET /api/products?page=2&per_page=20                       # Pagination
        GET /api/products?category_id=5                            # By category
        GET /api/products?featured=true                            # Featured only
        GET /api/products?search_type=id&search_value=42           # By ID
        GET /api/products?search_type=sku&search_value=SKU-123     # By SKU
        GET /api/products?search_type=slug&search_value=laptop-hp  # By slug
        GET /api/products?search_type=barcode&search_value=789     # By barcode
        GET /api/products?search_type=name&search_value=laptop     # By name
    """
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Build filters dictionary
        filters = {}
        
        # Category filter
        if request.args.get('category_id'):
            filters['category_id'] = request.args.get('category_id', type=int)
        
        # Featured filter
        if request.args.get('featured'):
            filters['featured'] = request.args.get('featured', type=bool)
        
        # Unified search
        if request.args.get('search_type'):
            filters['search_type'] = request.args.get('search_type', type=str)
            filters['search_value'] = request.args.get('search_value', type=str)
        
        # Get products
        result = ProductService.get_all_products(
            page=page,
            per_page=per_page,
            filters=filters
        )
        
        return jsonify(result), 200
        
    except ValueError as e:
        logger.warning(f"Validation error in get_products: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error in get_products: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@product_bp.route('/upload-image', methods=['POST'])
def upload_image():
    """
    Upload a single product image, validate it with Pillow, and return its URL.

    Request
        Content-Type : multipart/form-data
        Field        : file   (the image)

    Response  201
        { "url": "/static/uploads/products/<uuid>.<ext>" }

    Security flow
        1. Extension whitelist – rejects anything that isn't png/jpg/jpeg/gif/webp.
        2. Size check          – rejects files larger than MAX_CONTENT_LENGTH (5 MB).
        3. Pillow verify()     – opens the stream and confirms it is a real image;
                                 raises an exception if the bytes don't match a
                                 known image format (catches renamed executables, etc.).
        4. Pillow re-save()    – re-encodes the image from scratch through Pillow.
                                 This strips embedded scripts, EXIF payloads, and
                                 any other metadata that could be weaponised.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if not file or file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # --- 1. Extension whitelist ----------------------------------------------
    if not _allowed_file(file.filename):
        return jsonify({
            'error': f'Invalid file type. Allowed: {", ".join(sorted(ALLOWED_EXTENSIONS))}'
        }), 400

    # --- 2. Size check (before any disk I/O) ---------------------------------
    file.seek(0, 2)                 # seek to end
    file_size = file.tell()
    file.seek(0)                    # reset for Pillow

    max_size = current_app.config.get('MAX_CONTENT_LENGTH', 5 * 1024 * 1024)
    if file_size > max_size:
        return jsonify({
            'error': f'File too large. Max allowed: {max_size / (1024 * 1024):.0f} MB'
        }), 400

    # --- 3 & 4. Pillow verify -> re-save --------------------------------------
    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"

    upload_dir = os.path.join(current_app.static_folder, 'uploads', 'products')
    os.makedirs(upload_dir, exist_ok=True)
    save_path = os.path.join(upload_dir, unique_name)

    try:
        # verify() reads the whole file and raises if it isn't a valid image.
        # It also invalidates the Image object, so we must re-open afterwards.
        img = Image.open(file)
        img.verify()

        # Re-open from the original stream and let Pillow re-encode.
        # This is the step that actually strips dangerous metadata.
        file.seek(0)
        img = Image.open(file)
        img.save(save_path)

        logger.info(f"Product image uploaded: {unique_name} ({file_size} bytes)")
        return jsonify({'url': f'/static/uploads/products/{unique_name}'}), 201

    except Exception as e:
        # Any Pillow error here means the file is not a legitimate image.
        logger.warning(f"Invalid image upload rejected: {e}")
        return jsonify({'error': 'Invalid or corrupted image file'}), 400


@product_bp.route('/add', methods=['POST'])
def create_product():
    """Create a new product."""
    try:
        data = request.get_json()
        product = ProductService.create_product(**data)
        return jsonify(product.to_dict(include_category=True)), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error creating product: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@product_bp.route('/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update a product."""
    try:
        data = request.get_json()
        product = ProductService.update_product(product_id, **data)
        return jsonify(product.to_dict(include_category=True)), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@product_bp.route('/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Soft delete a product."""
    try:
        ProductService.delete_product(product_id)
        return jsonify({'message': 'Product deleted successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {e}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500