import numpy as np
import cv2
import logging
from typing import Dict, Tuple
import hashlib
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest


class PixelAnalyzer:
    """
    Analyzes pixel-level changes to detect deepfake attempts and tampering
    """

    def __init__(self, sensitivity: float = 0.7):
        """
        Initialize pixel analyzer
        
        Args:
            sensitivity: Detection sensitivity (0.0-1.0), higher = more sensitive
        """
        self.logger = logging.getLogger(__name__)
        self.sensitivity = sensitivity
        self.anomaly_detector = IsolationForest(
            contamination=1 - sensitivity,
            random_state=42
        )

    def detect_pixel_modifications(self, original_pixels: np.ndarray,
                                  modified_pixels: np.ndarray) -> Dict:
        """
        Detect if pixels have been modified (deepfaked)
        
        Args:
            original_pixels: Original image array
            modified_pixels: Potentially modified image array
            
        Returns:
            Dictionary with detection results
        """
        if original_pixels.shape != modified_pixels.shape:
            return {
                'tampered': True,
                'confidence': 0.95,
                'reason': 'Image dimensions changed',
                'modifications': []
            }

        # Calculate pixel differences
        diff = np.abs(original_pixels.astype(float) - modified_pixels.astype(float))
        
        # Find pixels that changed
        changed_pixels = np.where(diff > 0)
        
        if len(changed_pixels[0]) == 0:
            return {
                'tampered': False,
                'confidence': 0.0,
                'reason': 'No pixel changes detected',
                'modifications': []
            }
        
        # Calculate modification statistics
        modification_percentage = (len(changed_pixels[0]) / original_pixels.size) * 100
        avg_change = np.mean(diff[changed_pixels])
        max_change = np.max(diff[changed_pixels])
        
        # Analyze change patterns
        change_patterns = self._analyze_change_patterns(diff, changed_pixels)
        
        # Detect if changes match deepfake patterns
        is_deepfake = self._detect_deepfake_patterns(diff, change_patterns)
        
        confidence = self._calculate_confidence(
            modification_percentage,
            avg_change,
            change_patterns,
            is_deepfake
        )
        
        return {
            'tampered': confidence > 0.5,
            'confidence': confidence,
            'modification_percentage': modification_percentage,
            'average_change': float(avg_change),
            'maximum_change': float(max_change),
            'patterns': change_patterns,
            'is_deepfake': is_deepfake,
            'reason': self._generate_reason(confidence, change_patterns)
        }

    def _analyze_change_patterns(self, diff: np.ndarray, 
                                changed_pixels: Tuple) -> Dict:
        """
        Analyze patterns in pixel changes
        
        Args:
            diff: Difference array
            changed_pixels: Indices of changed pixels
            
        Returns:
            Dictionary with pattern analysis
        """
        patterns = {
            'clustered': False,
            'distributed': False,
            'facial_regions': False,
            'edges_modified': False,
            'clustering_score': 0.0
        }
        
        # Check if changes are clustered (typical of AI manipulation)
        if len(changed_pixels[0]) > 0:
            y_coords = changed_pixels[0]
            x_coords = changed_pixels[1]
            
            # Calculate spatial distribution
            coord_variance = np.var(np.column_stack([y_coords, x_coords]), axis=0)
            clustering_score = 1 - (np.mean(coord_variance) / (diff.shape[0] * diff.shape[1]))
            
            patterns['clustering_score'] = float(clustering_score)
            patterns['clustered'] = clustering_score > 0.6
            patterns['distributed'] = clustering_score < 0.3
        
        # Detect if changes are in facial regions
        if len(diff.shape) >= 2:
            patterns['facial_regions'] = self._detect_facial_modifications(diff)
        
        # Detect edge modifications
        patterns['edges_modified'] = self._detect_edge_modifications(diff)
        
        return patterns

    def _detect_deepfake_patterns(self, diff: np.ndarray, 
                                 patterns: Dict) -> bool:
        """
        Check if change patterns match known deepfake indicators
        
        Args:
            diff: Difference array
            patterns: Pattern analysis results
            
        Returns:
            True if deepfake patterns detected
        """
        deepfake_indicators = 0
        
        # Indicator 1: Clustering in specific regions
        if patterns['clustered']:
            deepfake_indicators += 2
        
        # Indicator 2: Facial region modifications
        if patterns['facial_regions']:
            deepfake_indicators += 2
        
        # Indicator 3: Smooth edges (typical of AI generation)
        if patterns['edges_modified']:
            deepfake_indicators += 1
        
        # Indicator 4: Frequency domain analysis
        if self._analyze_frequency_domain(diff):
            deepfake_indicators += 2
        
        return deepfake_indicators >= 4

    def _detect_facial_modifications(self, diff: np.ndarray) -> bool:
        """
        Detect if changes are in facial regions using face detection
        
        Args:
            diff: Difference array
            
        Returns:
            True if facial regions modified
        """
        try:
            # Use Haar Cascade to detect faces
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            # Convert diff to 8-bit for detection
            diff_8bit = np.clip(diff, 0, 255).astype(np.uint8)
            
            faces = face_cascade.detectMultiScale(diff_8bit, 1.3, 5)
            
            if len(faces) > 0:
                # Check if detected faces have modifications
                for (x, y, w, h) in faces:
                    face_region = diff[y:y+h, x:x+w]
                    if np.mean(face_region) > 5:  # Threshold for significant change
                        return True
            
            return False
        except Exception as e:
            self.logger.warning(f"Face detection error: {e}")
            return False

    def _detect_edge_modifications(self, diff: np.ndarray) -> bool:
        """
        Detect if edges have been smoothed (typical of AI interpolation)
        
        Args:
            diff: Difference array
            
        Returns:
            True if edges modified
        """
        try:
            # Apply edge detection
            edges = cv2.Canny(diff.astype(np.uint8), 50, 150)
            
            # Analyze edge consistency
            edge_ratio = np.sum(edges > 0) / edges.size
            
            # AI-generated images often have very smooth edges (low ratio)
            return edge_ratio < 0.05
        except Exception as e:
            self.logger.warning(f"Edge detection error: {e}")
            return False

    def _analyze_frequency_domain(self, diff: np.ndarray) -> bool:
        """
        Analyze frequency domain for deepfake artifacts
        
        Args:
            diff: Difference array
            
        Returns:
            True if suspicious frequency patterns detected
        """
        try:
            # Convert to grayscale if needed
            if len(diff.shape) == 3:
                gray_diff = cv2.cvtColor(diff.astype(np.uint8), cv2.COLOR_BGR2GRAY)
            else:
                gray_diff = diff.astype(np.uint8)
            
            # Compute FFT
            f_transform = np.fft.fft2(gray_diff)
            f_shift = np.fft.fftshift(f_transform)
            magnitude_spectrum = np.abs(f_shift)
            
            # Analyze frequency components
            # AI-generated content often has specific frequency signatures
            low_freq_ratio = np.sum(magnitude_spectrum[:10, :10]) / np.sum(magnitude_spectrum)
            
            # Suspicious if low frequencies are dominant
            return low_freq_ratio > 0.3
        except Exception as e:
            self.logger.warning(f"Frequency analysis error: {e}")
            return False

    def _calculate_confidence(self, modification_percentage: float,
                             avg_change: float,
                             patterns: Dict,
                             is_deepfake: bool) -> float:
        """
        Calculate overall tampering confidence score
        
        Args:
            modification_percentage: Percentage of pixels modified
            avg_change: Average pixel value change
            patterns: Pattern analysis results
            is_deepfake: Whether deepfake patterns detected
            
        Returns:
            Confidence score (0.0-1.0)
        """
        confidence = 0.0
        
        # Factor 1: Modification percentage
        if modification_percentage > 50:
            confidence += 0.3
        elif modification_percentage > 10:
            confidence += 0.15
        
        # Factor 2: Average change magnitude
        if avg_change > 50:
            confidence += 0.2
        elif avg_change > 20:
            confidence += 0.1
        
        # Factor 3: Deepfake patterns
        if is_deepfake:
            confidence += 0.35
        
        # Factor 4: Clustering pattern (suspicious)
        if patterns['clustered']:
            confidence += 0.15
        
        # Apply sensitivity multiplier
        confidence *= self.sensitivity
        
        return min(confidence, 1.0)

    def _generate_reason(self, confidence: float, patterns: Dict) -> str:
        """
        Generate human-readable reason for detection
        
        Args:
            confidence: Confidence score
            patterns: Pattern analysis results
            
        Returns:
            Reason string
        """
        if confidence < 0.3:
            return "Image integrity verified"
        elif confidence < 0.5:
            return "Slight modifications detected"
        elif patterns['is_deepfake']:
            return "Deepfake artifacts detected - AI manipulation suspected"
        elif patterns['facial_regions']:
            return "Face region modifications detected"
        elif patterns['clustered']:
            return "Clustered pixel modifications detected - suspicious pattern"
        else:
            return f"Image tampering detected (confidence: {confidence:.1%})"

    def detect_lsb_watermark(self, image: np.ndarray) -> Dict:
        """
        Detect LSB steganographic watermark
        
        Args:
            image: Image array
            
        Returns:
            Dictionary with watermark detection results
        """
        try:
            flat_image = image.flatten()
            lsb_pattern = flat_image & 1  # Extract LSBs
            
            # Analyze LSB pattern entropy
            unique_lsb = len(np.unique(lsb_pattern))
            entropy = -np.sum((np.bincount(lsb_pattern) / len(lsb_pattern)) * 
                             np.log2(np.bincount(lsb_pattern) / len(lsb_pattern) + 1e-10))
            
            return {
                'watermark_detected': entropy < 0.5,
                'entropy': float(entropy),
                'confidence': max(0, (1 - entropy) * 100) if entropy < 1 else 0
            }
        except Exception as e:
            self.logger.warning(f"Watermark detection error: {e}")
            return {'watermark_detected': False, 'error': str(e)}
