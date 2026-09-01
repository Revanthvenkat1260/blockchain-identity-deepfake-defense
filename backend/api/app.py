from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'postgresql://localhost/deepfake_defense'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False

# Initialize extensions
db = SQLAlchemy(app)
CORS(app)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import routes
from .routes import auth_routes, image_routes, verification_routes, blockchain_routes, admin_routes

# Register blueprints
app.register_blueprint(auth_routes.bp)
app.register_blueprint(image_routes.bp)
app.register_blueprint(verification_routes.bp)
app.register_blueprint(blockchain_routes.bp)
app.register_blueprint(admin_routes.bp)

# Error handlers
@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request', 'message': str(error)}), 400

@app.errorhandler(401)
def unauthorized(error):
    return jsonify({'error': 'Unauthorized', 'message': 'Invalid credentials'}), 401

@app.errorhandler(403)
def forbidden(error):
    return jsonify({'error': 'Forbidden', 'message': 'Insufficient permissions'}), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'message': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'blockchain-identity-deepfake-defense'
    }), 200

@app.route('/api/v1', methods=['GET'])
def api_info():
    return jsonify({
        'name': 'Blockchain Identity Deepfake Defense API',
        'version': '1.0.0',
        'description': 'API for secure identity management and deepfake prevention',
        'endpoints': {
            'auth': '/api/v1/auth',
            'images': '/api/v1/images',
            'verification': '/api/v1/verify',
            'blockchain': '/api/v1/blockchain',
            'admin': '/api/v1/admin'
        }
    }), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=os.getenv('FLASK_ENV') == 'development', host='0.0.0.0', port=5000)
