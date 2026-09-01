import threading
import logging
from typing import Callable, List, Dict
from scapy.all import sniff, IP, TCP
import json
from datetime import datetime


class NetworkMonitor:
    """
    Monitors network traffic for AI service API calls and deepfake attempts
    """

    # Known AI service signatures
    AI_SERVICE_SIGNATURES = {
        'openai': {'domains': ['api.openai.com', 'chat.openai.com'], 'ports': [443]},
        'google': {'domains': ['generativelanguage.googleapis.com', 'googleapis.com'], 'ports': [443]},
        'anthropic': {'domains': ['api.anthropic.com'], 'ports': [443]},
        'microsoft': {'domains': ['api.cognitive.microsoft.com'], 'ports': [443]},
        'huggingface': {'domains': ['huggingface.co', 'api-inference.huggingface.co'], 'ports': [443]},
        'replicate': {'domains': ['api.replicate.com'], 'ports': [443]},
        'stability': {'domains': ['api.stability.ai'], 'ports': [443]},
    }

    # Deepfake detection API services
    DEEPFAKE_DETECTION_SERVICES = {
        'tensorflow': {'ports': [6006]},  # TensorFlow serving
        'pytorch': {'ports': [8000, 8080]},  # PyTorch serving
        'onnx': {'ports': [8001]},  # ONNX Runtime
    }

    def __init__(self, alert_callback: Callable = None):
        """
        Initialize network monitor
        
        Args:
            alert_callback: Callback function when AI service detected
        """
        self.logger = logging.getLogger(__name__)
        self.alert_callback = alert_callback
        self.is_monitoring = False
        self.monitor_thread = None
        self.detected_services: List[Dict] = []

    def _check_packet(self, packet):
        """
        Analyze individual packet for AI service signatures
        
        Args:
            packet: Scapy packet object
        """
        try:
            if not packet.haslayer(TCP):
                return

            tcp_layer = packet[TCP]
            ip_layer = packet[IP]

            # Check for suspicious ports
            suspicious_ports = [p for service_ports in self.DEEPFAKE_DETECTION_SERVICES.values() 
                              for p in service_ports['ports']]
            
            if tcp_layer.dport in suspicious_ports or tcp_layer.sport in suspicious_ports:
                self._alert_detection({
                    'type': 'LOCAL_ML_SERVICE',
                    'source_ip': ip_layer.src,
                    'dest_ip': ip_layer.dst,
                    'port': tcp_layer.dport or tcp_layer.sport,
                    'timestamp': datetime.utcnow().isoformat(),
                    'severity': 'HIGH'
                })

        except Exception as e:
            self.logger.warning(f"Error analyzing packet: {e}")

    def _monitor_traffic(self, interface: str = None):
        """
        Capture and analyze network traffic
        
        Args:
            interface: Network interface to monitor (None = all)
        """
        try:
            self.logger.info("Starting network traffic monitoring...")
            sniff(prn=self._check_packet, store=False, stop_filter=lambda x: not self.is_monitoring)
        except Exception as e:
            self.logger.error(f"Network monitoring error: {e}")
            self.is_monitoring = False

    def _alert_detection(self, detection_info: Dict):
        """
        Handle detected suspicious activity
        
        Args:
            detection_info: Information about detected threat
        """
        self.detected_services.append(detection_info)
        self.logger.warning(f"THREAT DETECTED: {json.dumps(detection_info, indent=2)}")
        
        if self.alert_callback:
            self.alert_callback(detection_info)

    def start_monitoring(self, interface: str = None):
        """
        Start monitoring network in background thread
        
        Args:
            interface: Network interface to monitor
        """
        if self.is_monitoring:
            self.logger.warning("Monitoring already running")
            return

        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_traffic,
            args=(interface,),
            daemon=True
        )
        self.monitor_thread.start()
        self.logger.info("Network monitoring started")

    def stop_monitoring(self):
        """
        Stop network monitoring
        """
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("Network monitoring stopped")

    def check_api_endpoint(self, hostname: str, port: int) -> Dict:
        """
        Check if hostname/port matches known AI services
        
        Args:
            hostname: Domain or IP to check
            port: Port number
            
        Returns:
            Dictionary with detection results
        """
        result = {'detected': False, 'services': [], 'is_authorized': False}

        for service_name, config in self.AI_SERVICE_SIGNATURES.items():
            for domain in config['domains']:
                if domain in hostname and port in config['ports']:
                    result['detected'] = True
                    result['services'].append(service_name)

        return result

    def get_detected_services(self) -> List[Dict]:
        """
        Get list of detected suspicious services
        
        Returns:
            List of detection events
        """
        return self.detected_services.copy()

    def clear_detections(self):
        """
        Clear detection history
        """
        self.detected_services.clear()
