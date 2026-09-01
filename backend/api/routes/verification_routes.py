from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from ..core import PixelAnalyzer, DeepfakeDetector, IntegrityVerifier
import os
import tempfile

bp = Blueprint('verification', __name__, url_prefix='/api/v1/verify')
logger = logging.getLogger(__name__)


@bp.route('/integrity', methods=['POST'])
def verify_integrity():
    """
    Verify image integrity using pixel analysis
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('image_data') or not data.get('metadata'):
            return jsonify({'error': 'Missing required fields'}), 400
        
        image_data = data.get('image_data')  # Base64 encoded
        metadata = data.get('metadata')
        original_signature = data.get('pixel_signature')
        
        # Initialize verifier
        verifier = IntegrityVerifier()
        
        # Decode image data
        import base64
        image_bytes = base64.b64decode(image_data)
        
        # Verify authenticity
        result = verifier.verify_image_authenticity(image_bytes, metadata, original_signature)
        
        return jsonify({
            'authentic': result['authentic'],
            'confidence': result['overall_confidence'],
            'details': result['verification_details'],
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Integrity verification error: {e}")
        return jsonify({'error': 'Verification failed', 'details': str(e)}), 500


@bp.route('/deepfake', methods=['POST'])
def detect_deepfake():
    """
    Detect deepfake using ML models
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        
        if not file or file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as tmp:
            file.save(tmp.name)
            temp_path = tmp.name
        
        try:
            # Initialize detector
            detector = DeepfakeDetector(device='cpu')  # Use GPU if available
            
            # Detect deepfake
            result = detector.detect_deepfake(temp_path)
            
            return jsonify({
                'is_deepfake': result['is_deepfake'],
                'confidence': result['confidence'],
                'models': result['model_results'],
                'recommendation': result['recommendation'],
                'timestamp': datetime.utcnow().isoformat()
            }), 200
        
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        logger.error(f"Deepfake detection error: {e}")
        return jsonify({'error': 'Detection failed', 'details': str(e)}), 500


@bp.route('/pixels', methods=['POST'])
def analyze_pixels():
    """
    Analyze pixel modifications to detect tampering
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('original') or not data.get('current'):
            return jsonify({'error': 'Missing image data'}), 400
        
        # Decode images
        import base64
        import numpy as np
        from PIL import Image
        import io
        
        original_img = Image.open(io.BytesIO(base64.b64decode(data['original'])))
        current_img = Image.open(io.BytesIO(base64.b64decode(data['current'])))
        
        original_array = np.array(original_img)
        current_array = np.array(current_img)
        
        # Initialize analyzer
        analyzer = PixelAnalyzer(sensitivity=data.get('sensitivity', 0.7))
        
        # Detect modifications
        result = analyzer.detect_pixel_modifications(original_array, current_array)
        
        return jsonify({
            'tampered': result['tampered'],
            'confidence': result['confidence'],
            'modification_percentage': result['modification_percentage'],
            'analysis': result,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Pixel analysis error: {e}")
        return jsonify({'error': 'Analysis failed', 'details': str(e)}), 500


@bp.route('/report/<verification_id>', methods=['GET'])
def get_verification_report(verification_id):
    """
    Get detailed verification report
    """
    try:
        # In production, retrieve from database
        return jsonify({
            'report': 'Verification report would be retrieved from database',
            'verification_id': verification_id
        }), 200
    
    except Exception as e:
        logger.error(f"Report retrieval error: {e}")
        return jsonify({'error': 'Failed to retrieve report'}), 500
