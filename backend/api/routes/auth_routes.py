from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import os
from datetime import datetime, timedelta
import logging

bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')
logger = logging.getLogger(__name__)

SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')


@bp.route('/register', methods=['POST'])
def register():
    """
    Register new user with DID
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing required fields'}), 400
        
        email = data.get('email')
        password = data.get('password')
        public_key = data.get('public_key')
        
        # Hash password
        password_hash = generate_password_hash(password)
        
        # Generate DID (simplified - in production, use proper DID library)
        did = f"did:polygon:{email}:{datetime.utcnow().timestamp()}"
        
        # Create user (in production, save to database)
        user = {
            'email': email,
            'did': did,
            'public_key': public_key,
            'password_hash': password_hash,
            'created_at': datetime.utcnow().isoformat(),
            'role': 'USER'
        }
        
        return jsonify({
            'message': 'User registered successfully',
            'user': {
                'email': email,
                'did': did,
                'role': 'USER'
            }
        }), 201
    
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500


@bp.route('/login', methods=['POST'])
def login():
    """
    Login user and return JWT token
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing credentials'}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        # Verify credentials (in production, check against database)
        # This is simplified for demonstration
        
        # Generate JWT token
        payload = {
            'email': email,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'expires_in': 86400
        }), 200
    
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500


@bp.route('/verify-token', methods=['POST'])
def verify_token():
    """
    Verify JWT token validity
    """
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not token:
            return jsonify({'error': 'No token provided'}), 401
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        
        return jsonify({
            'valid': True,
            'email': payload.get('email'),
            'expires_at': payload.get('exp')
        }), 200
    
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return jsonify({'error': 'Verification failed'}), 500
