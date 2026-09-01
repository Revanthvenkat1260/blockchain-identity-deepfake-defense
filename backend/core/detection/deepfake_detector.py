import torch
import torch.nn.functional as F
from torchvision import models, transforms
import cv2
import numpy as np
import logging
from typing import Dict, List, Tuple
from pathlib import Path
import json


class DeepfakeDetector:
    """
    Machine learning-based deepfake detection using multiple models
    """

    def __init__(self, model_path: str = None, device: str = 'cpu'):
        """
        Initialize deepfake detector
        
        Args:
            model_path: Path to pre-trained model weights
            device: 'cpu' or 'cuda'
        """
        self.logger = logging.getLogger(__name__)
        self.device = torch.device(device if torch.cuda.is_available() else 'cpu')
        self.model_path = model_path
        self.models = {}
        self._initialize_models()
        
        # Image preprocessing
        self.transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def _initialize_models(self):
        """
        Initialize pre-trained neural network models
        """
        try:
            # EfficientNet-B0 for binary classification
            self.models['efficientnet'] = models.efficientnet_b0(pretrained=True)
            self.models['efficientnet'].classifier[1] = torch.nn.Linear(1280, 2)
            self.models['efficientnet'].to(self.device)
            self.models['efficientnet'].eval()
            
            # ResNet50 for multi-frame analysis
            self.models['resnet50'] = models.resnet50(pretrained=True)
            self.models['resnet50'].fc = torch.nn.Linear(2048, 2)
            self.models['resnet50'].to(self.device)
            self.models['resnet50'].eval()
            
            self.logger.info(f"Models initialized on device: {self.device}")
        except Exception as e:
            self.logger.error(f"Model initialization error: {e}")

    def detect_deepfake(self, image_path: str) -> Dict:
        """
        Detect deepfake in a single image
        
        Args:
            image_path: Path to image file
            
        Returns:
            Detection results dictionary
        """
        try:
            # Load and preprocess image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Cannot load image: {image_path}")
            
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Run multiple models
            results = {}
            
            # EfficientNet detection
            efficientnet_result = self._detect_with_model(
                image_rgb,
                'efficientnet'
            )
            results['efficientnet'] = efficientnet_result
            
            # ResNet50 detection
            resnet_result = self._detect_with_model(
                image_rgb,
                'resnet50'
            )
            results['resnet50'] = resnet_result
            
            # Frequency domain analysis
            freq_result = self._frequency_analysis(image_rgb)
            results['frequency_analysis'] = freq_result
            
            # Ensemble decision
            ensemble_result = self._ensemble_decision(results)
            
            return {
                'is_deepfake': ensemble_result['is_deepfake'],
                'confidence': ensemble_result['confidence'],
                'model_results': results,
                'recommendation': ensemble_result['recommendation']
            }
        except Exception as e:
            self.logger.error(f"Deepfake detection error: {e}")
            return {
                'is_deepfake': False,
                'error': str(e),
                'confidence': 0.0
            }

    def _detect_with_model(self, image: np.ndarray, model_name: str) -> Dict:
        """
        Detect deepfake using specific model
        
        Args:
            image: Image array (RGB)
            model_name: Name of model to use
            
        Returns:
            Detection results
        """
        try:
            model = self.models[model_name]
            
            # Preprocess
            tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            # Forward pass
            with torch.no_grad():
                output = model(tensor)
                probabilities = F.softmax(output, dim=1)
            
            fake_prob = probabilities[0, 1].item()  # Probability of fake
            
            return {
                'model': model_name,
                'is_deepfake': fake_prob > 0.5,
                'confidence': fake_prob
            }
        except Exception as e:
            self.logger.warning(f"Error with {model_name}: {e}")
            return {'model': model_name, 'error': str(e)}

    def _frequency_analysis(self, image: np.ndarray) -> Dict:
        """
        Analyze frequency domain characteristics
        
        Args:
            image: Image array
            
        Returns:
            Frequency analysis results
        """
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Compute FFT
            f_transform = np.fft.fft2(gray)
            f_shift = np.fft.fftshift(f_transform)
            magnitude = np.abs(f_shift)
            
            # Analyze frequency components
            center_y, center_x = gray.shape[0] // 2, gray.shape[1] // 2
            center_region = magnitude[
                center_y-50:center_y+50,
                center_x-50:center_x+50
            ]
            outer_region = np.concatenate([
                magnitude[:center_y-50, :],
                magnitude[center_y+50:, :]
            ])
            
            center_energy = np.sum(center_region ** 2)
            total_energy = np.sum(magnitude ** 2)
            frequency_ratio = center_energy / (total_energy + 1e-10)
            
            # AI-generated images often have different frequency signatures
            is_suspicious = frequency_ratio > 0.7 or frequency_ratio < 0.2
            
            return {
                'frequency_ratio': float(frequency_ratio),
                'is_suspicious': is_suspicious,
                'confidence': abs(frequency_ratio - 0.45) * 2  # Distance from normal
            }
        except Exception as e:
            self.logger.warning(f"Frequency analysis error: {e}")
            return {'error': str(e)}

    def _ensemble_decision(self, results: Dict) -> Dict:
        """
        Combine multiple model predictions
        
        Args:
            results: Results from all models
            
        Returns:
            Ensemble decision
        """
        votes_deepfake = 0
        total_votes = 0
        confidence_scores = []
        
        # Collect votes from models
        if 'efficientnet' in results and 'is_deepfake' in results['efficientnet']:
            votes_deepfake += 1 if results['efficientnet']['is_deepfake'] else 0
            total_votes += 1
            confidence_scores.append(results['efficientnet']['confidence'])
        
        if 'resnet50' in results and 'is_deepfake' in results['resnet50']:
            votes_deepfake += 1 if results['resnet50']['is_deepfake'] else 0
            total_votes += 1
            confidence_scores.append(results['resnet50']['confidence'])
        
        if 'frequency_analysis' in results and 'is_suspicious' in results['frequency_analysis']:
            votes_deepfake += 1 if results['frequency_analysis']['is_suspicious'] else 0
            total_votes += 1
            confidence_scores.append(results['frequency_analysis']['confidence'])
        
        # Ensemble decision (majority vote)
        is_deepfake = votes_deepfake > (total_votes / 2)
        avg_confidence = np.mean(confidence_scores) if confidence_scores else 0.0
        
        # Generate recommendation
        if is_deepfake and avg_confidence > 0.8:
            recommendation = "REJECT - High confidence deepfake detected"
        elif is_deepfake and avg_confidence > 0.6:
            recommendation = "WARN - Medium confidence deepfake detected"
        elif avg_confidence > 0.5:
            recommendation = "REVIEW - Low confidence anomaly detected"
        else:
            recommendation = "ACCEPT - Image appears authentic"
        
        return {
            'is_deepfake': is_deepfake,
            'confidence': float(avg_confidence),
            'votes': votes_deepfake,
            'total_votes': total_votes,
            'recommendation': recommendation
        }

    def detect_deepfake_video(self, video_path: str, 
                             sample_frames: int = 10) -> Dict:
        """
        Detect deepfake in video (sample frames)
        
        Args:
            video_path: Path to video file
            sample_frames: Number of frames to analyze
            
        Returns:
            Detection results for video
        """
        try:
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if total_frames == 0:
                raise ValueError(f"Cannot read video: {video_path}")
            
            frame_interval = max(1, total_frames // sample_frames)
            detections = []
            
            for i in range(0, total_frames, frame_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Detect deepfake in frame
                detection = self._detect_with_model(frame_rgb, 'efficientnet')
                detections.append({
                    'frame_number': i,
                    **detection
                })
            
            cap.release()
            
            # Aggregate results
            deepfake_frames = sum(1 for d in detections if d.get('is_deepfake', False))
            avg_confidence = np.mean([d.get('confidence', 0) for d in detections])
            
            return {
                'is_deepfake': deepfake_frames > len(detections) / 2,
                'deepfake_frame_count': deepfake_frames,
                'total_frames_analyzed': len(detections),
                'average_confidence': float(avg_confidence),
                'frame_detections': detections
            }
        except Exception as e:
            self.logger.error(f"Video deepfake detection error: {e}")
            return {'error': str(e)}
