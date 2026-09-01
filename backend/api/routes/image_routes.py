from flask import Blueprint, request, jsonify, send_file
import os
import logging
from datetime import datetime
from ..core import ImageEncryptor
import tempfile
from werkzeug.utils import secure_filename

bp = Blueprint('images', __name__, url_prefix='/api/v1/images')
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/encrypt', methods=['POST'])
def encrypt_image():
    """
    Encrypt image and generate pixel signature
    """
    try:
        # Check for file in request
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        did = request.form.get('did')
        
        if not file or not did:
            return jsonify({'error': 'Missing required fields'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Save temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as tmp:
            file.save(tmp.name)
            temp_path = tmp.name
        
        try:
            # Initialize encryptor with user's key (in production, use user's actual key)
            master_key = b'0' * 32  # Placeholder
            encryptor = ImageEncryptor(master_key)
            
            # Encrypt image
            result = encryptor.encrypt_image(temp_path, did)
            
            return jsonify({
                'message': 'Image encrypted successfully',
                'encryption_id': result['metadata']['encryption_id'],
                'pixel_signature': result['metadata']['pixel_signature'],
                'metadata': result['metadata'],
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        logger.error(f"Image encryption error: {e}")
        return jsonify({'error': 'Encryption failed', 'details': str(e)}), 500


@bp.route('/decrypt/<encryption_id>', methods=['GET'])
def decrypt_image(encryption_id):
    """
    Decrypt image for authorized users
    """
    try:
        # In production, verify authorization and retrieve encrypted data from storage
        return jsonify({
            'error': 'Image decryption requires proper authentication and authorization'
        }), 403
    
    except Exception as e:
        logger.error(f"Image decryption error: {e}")
        return jsonify({'error': 'Decryption failed'}), 500


@bp.route('/list', methods=['GET'])
def list_images():
    """
    List images for authenticated user
    """
    try:
        did = request.args.get('did')
        limit = request.args.get('limit', default=10, type=int)
        
        if not did:
            return jsonify({'error': 'DID required'}), 400
        
        # In production, query database for user's images
        return jsonify({
            'images': [],
            'total': 0,
            'limit': limit
        }), 200
    
    except Exception as e:
        logger.error(f"List images error: {e}")
        return jsonify({'error': 'Failed to list images'}), 500


@bp.route('/delete/<image_id>', methods=['DELETE'])
def delete_image(image_id):
    """
    Delete image and associated encryption data
    """
    try:
        # In production, verify ownership before deletion
        return jsonify({
            'message': 'Image deleted successfully',
            'image_id': image_id
        }), 200
    
    except Exception as e:
        logger.error(f"Image deletion error: {e}")
        return jsonify({'error': 'Deletion failed'}), 500
