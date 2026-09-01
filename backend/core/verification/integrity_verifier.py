import hashlib
import hmac
from typing import Dict, Tuple
import json
from datetime import datetime
import logging


class IntegrityVerifier:
    """
    Verifies image integrity and ownership through multiple verification layers
    """

    def __init__(self, blockchain_provider=None):
        """
        Initialize integrity verifier
        
        Args:
            blockchain_provider: Provider for blockchain verification
        """
        self.logger = logging.getLogger(__name__)
        self.blockchain = blockchain_provider
        self.verification_cache = {}

    def verify_image_authenticity(self, image_data: bytes,
                                 metadata: Dict,
                                 original_signature: str) -> Dict:
        """
        Verify complete image authenticity
        
        Args:
            image_data: Image bytes
            metadata: Image metadata
            original_signature: Original pixel signature
            
        Returns:
            Verification results
        """
        verification_results = {}
        
        # Step 1: Pixel signature verification
        pixel_sig_result = self._verify_pixel_signature(
            image_data,
            original_signature
        )
        verification_results['pixel_signature'] = pixel_sig_result
        
        # Step 2: Metadata verification
        metadata_result = self._verify_metadata(metadata)
        verification_results['metadata'] = metadata_result
        
        # Step 3: Blockchain verification (if available)
        if self.blockchain:
            blockchain_result = self._verify_blockchain_record(
                metadata.get('owner_did'),
                metadata.get('encryption_id')
            )
            verification_results['blockchain'] = blockchain_result
        
        # Step 4: Timestamp verification
        timestamp_result = self._verify_timestamp(metadata)
        verification_results['timestamp'] = timestamp_result
        
        # Overall result
        all_passed = all(r.get('verified', False) for r in verification_results.values())
        
        return {
            'authentic': all_passed,
            'verification_details': verification_results,
            'overall_confidence': self._calculate_overall_confidence(verification_results),
            'verification_timestamp': datetime.utcnow().isoformat()
        }

    def _verify_pixel_signature(self, image_data: bytes,
                               original_signature: str) -> Dict:
        """
        Verify pixel-level signature
        
        Args:
            image_data: Image bytes
            original_signature: Original signature to compare
            
        Returns:
            Verification result
        """
        # Generate current signature
        current_signature = hashlib.sha256(image_data).hexdigest()
        blake2_hash = hashlib.blake2b(image_data).hexdigest()
        
        verified = current_signature == original_signature or blake2_hash == original_signature
        
        return {
            'verified': verified,
            'current_signature': current_signature[:16] + '...',  # Truncate for display
            'expected_signature': original_signature[:16] + '...',
            'hash_type': 'SHA256+BLAKE2' if not verified else 'MATCH'
        }

    def _verify_metadata(self, metadata: Dict) -> Dict:
        """
        Verify metadata integrity
        
        Args:
            metadata: Metadata dictionary
            
        Returns:
            Verification result
        """
        required_fields = [
            'owner_did',
            'timestamp',
            'encryption_id',
            'pixel_signature',
            'encryption_algorithm'
        ]
        
        # Check all required fields present
        missing_fields = [f for f in required_fields if f not in metadata]
        
        # Verify encryption algorithm is supported
        supported_algorithms = ['AES-256-CBC', 'AES-256-GCM']
        valid_algorithm = metadata.get('encryption_algorithm', '') in supported_algorithms
        
        verified = len(missing_fields) == 0 and valid_algorithm
        
        return {
            'verified': verified,
            'missing_fields': missing_fields,
            'algorithm_valid': valid_algorithm,
            'fields_checked': len(required_fields),
            'fields_present': len(required_fields) - len(missing_fields)
        }

    def _verify_blockchain_record(self, owner_did: str,
                                 encryption_id: str) -> Dict:
        """
        Verify record exists on blockchain
        
        Args:
            owner_did: Owner's DID
            encryption_id: Unique encryption ID
            
        Returns:
            Verification result
        """
        if not self.blockchain:
            return {'verified': False, 'reason': 'Blockchain provider not available'}
        
        try:
            # Check if NFT exists and is linked to owner
            nft_record = self.blockchain.get_asset_record(encryption_id)
            
            if not nft_record:
                return {
                    'verified': False,
                    'reason': 'NFT not found on blockchain'
                }
            
            # Verify ownership
            owner_matches = nft_record.get('owner_did') == owner_did
            
            return {
                'verified': owner_matches,
                'nft_exists': True,
                'owner_matches': owner_matches,
                'blockchain_timestamp': nft_record.get('created_at'),
                'transaction_hash': nft_record.get('tx_hash', '')[:16] + '...'
            }
        except Exception as e:
            self.logger.error(f"Blockchain verification error: {e}")
            return {'verified': False, 'error': str(e)}

    def _verify_timestamp(self, metadata: Dict) -> Dict:
        """
        Verify timestamp is reasonable
        
        Args:
            metadata: Metadata dictionary
            
        Returns:
            Verification result
        """
        try:
            timestamp_str = metadata.get('timestamp')
            if not timestamp_str:
                return {'verified': False, 'reason': 'No timestamp provided'}
            
            # Parse timestamp
            timestamp = datetime.fromisoformat(timestamp_str)
            now = datetime.utcnow()
            
            # Check timestamp is in reasonable range (not future, not too old)
            time_diff = (now - timestamp).total_seconds()
            
            valid = -3600 < time_diff < 315360000  # -1 hour to +10 years
            
            return {
                'verified': valid,
                'timestamp_valid': valid,
                'age_days': time_diff / 86400,
                'is_future': time_diff < 0
            }
        except Exception as e:
            return {'verified': False, 'error': str(e)}

    def _calculate_overall_confidence(self, results: Dict) -> float:
        """
        Calculate overall verification confidence
        
        Args:
            results: Verification results dictionary
            
        Returns:
            Confidence score (0.0-1.0)
        """
        verified_checks = sum(1 for r in results.values() if r.get('verified', False))
        total_checks = len(results)
        
        return verified_checks / total_checks if total_checks > 0 else 0.0

    def generate_verification_report(self, verification_result: Dict) -> str:
        """
        Generate human-readable verification report
        
        Args:
            verification_result: Verification results
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 60)
        report.append("IMAGE AUTHENTICITY VERIFICATION REPORT")
        report.append("=" * 60)
        report.append(f"\nStatus: {'AUTHENTIC' if verification_result['authentic'] else 'NOT AUTHENTIC'}")
        report.append(f"Confidence: {verification_result['overall_confidence']:.1%}")
        report.append(f"Verified: {verification_result['verification_timestamp']}")
        
        report.append("\nDetailed Results:")
        for check_name, check_result in verification_result['verification_details'].items():
            status = "✓ PASS" if check_result.get('verified', False) else "✗ FAIL"
            report.append(f"\n  {check_name.upper()}: {status}")
            for key, value in check_result.items():
                if key != 'verified':
                    report.append(f"    - {key}: {value}")
        
        report.append("\n" + "=" * 60)
        return "\n".join(report)
