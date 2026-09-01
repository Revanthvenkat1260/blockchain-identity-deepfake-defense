import os
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import cv2
import numpy as np
from PIL import Image
import json
from datetime import datetime
import uuid


class ImageEncryptor:
    """
    Handles AES-256 encryption/decryption of images with pixel signature generation
    """

    def __init__(self, master_key: bytes):
        """
        Initialize with master key for key derivation
        
        Args:
            master_key: 32-byte master key (or will be derived from user's private key)
        """
        if len(master_key) != 32:
            raise ValueError("Master key must be 32 bytes for AES-256")
        self.master_key = master_key
        self.backend = default_backend()

    def derive_key(self, salt: bytes, info: str = "image") -> bytes:
        """
        Derive a unique key for each image using PBKDF2
        
        Args:
            salt: Random salt for key derivation
            info: Additional context (default: "image")
            
        Returns:
            32-byte derived key
        """
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=self.backend
        )
        return kdf.derive(self.master_key + info.encode())

    def generate_pixel_signature(self, image_data: np.ndarray) -> str:
        """
        Generate cryptographic signature of pixel values for integrity verification
        
        Args:
            image_data: Numpy array of image pixels
            
        Returns:
            Hex string of SHA-256 hash of pixels
        """
        # Flatten image to 1D array for hashing
        flat_pixels = image_data.flatten().tobytes()
        
        # Create double hash (SHA-256 + BLAKE2)
        sha256_hash = hashlib.sha256(flat_pixels).digest()
        blake2_hash = hashlib.blake2b(sha256_hash).hexdigest()
        
        return blake2_hash

    def embed_steganographic_watermark(self, image_data: np.ndarray, 
                                       watermark_data: str) -> np.ndarray:
        """
        Embed invisible watermark in LSB (Least Significant Bits) of image
        
        Args:
            image_data: Numpy array of image
            watermark_data: Data to embed (JSON string)
            
        Returns:
            Modified image array with embedded watermark
        """
        # Convert watermark to binary
        watermark_binary = ''.join(format(ord(c), '08b') for c in watermark_data)
        
        # Ensure watermark fits in image
        max_watermark_bits = image_data.size * 2  # 2 LSBs per pixel
        if len(watermark_binary) > max_watermark_bits:
            raise ValueError("Watermark too large for image")
        
        # Embed watermark in LSBs
        modified_image = image_data.copy().flatten()
        for i, bit in enumerate(watermark_binary):
            # Modify 2 LSBs
            byte_index = i // 4
            bit_position = (i % 4) * 2
            
            if byte_index < len(modified_image):
                if bit == '1':
                    modified_image[byte_index] |= (1 << bit_position)
                else:
                    modified_image[byte_index] &= ~(1 << bit_position)
        
        return modified_image.reshape(image_data.shape).astype(np.uint8)

    def extract_steganographic_watermark(self, image_data: np.ndarray, 
                                        watermark_length: int) -> str:
        """
        Extract embedded watermark from image
        
        Args:
            image_data: Numpy array of potentially watermarked image
            watermark_length: Length of watermark in bytes
            
        Returns:
            Extracted watermark string
        """
        flat_image = image_data.flatten()
        watermark_binary = ''
        
        # Extract bits from LSBs
        for i in range(watermark_length * 8):
            byte_index = i // 4
            bit_position = (i % 4) * 2
            
            if byte_index < len(flat_image):
                bit = (flat_image[byte_index] >> bit_position) & 1
                watermark_binary += str(bit)
        
        # Convert binary to string
        watermark = ''.join(
            chr(int(watermark_binary[i:i+8], 2)) 
            for i in range(0, len(watermark_binary), 8)
        )
        return watermark

    def encrypt_image(self, image_path: str, did: str) -> dict:
        """
        Encrypt image with AES-256 and generate metadata
        
        Args:
            image_path: Path to original image
            did: Owner's decentralized identifier
            
        Returns:
            Dictionary with encrypted image, salt, IV, and metadata
        """
        # Read image
        img = Image.open(image_path)
        image_array = np.array(img)
        original_format = img.format or 'PNG'
        
        # Generate random salt and IV
        salt = os.urandom(16)
        iv = os.urandom(16)
        
        # Derive unique key for this image
        image_key = self.derive_key(salt, info="image")
        
        # Generate pixel signature before encryption
        pixel_signature = self.generate_pixel_signature(image_array)
        
        # Convert image to bytes
        image_bytes = image_array.tobytes()
        
        # Encrypt image bytes
        cipher = Cipher(
            algorithms.AES(image_key),
            modes.CBC(iv),
            backend=self.backend
        )
        encryptor = cipher.encryptor()
        
        # Add PKCS7 padding
        padding_length = 16 - (len(image_bytes) % 16)
        padded_image = image_bytes + bytes([padding_length] * padding_length)
        
        encrypted_image = encryptor.update(padded_image) + encryptor.finalize()
        
        # Generate metadata
        metadata = {
            "owner_did": did,
            "timestamp": datetime.utcnow().isoformat(),
            "encryption_id": str(uuid.uuid4()),
            "original_format": original_format,
            "pixel_signature": pixel_signature,
            "image_shape": list(image_array.shape),
            "encryption_algorithm": "AES-256-CBC",
            "salt": salt.hex(),
            "iv": iv.hex(),
            "privacy_level": "strict",  # Can be: strict, moderate, open
            "hash_algorithm": "SHA256+BLAKE2"
        }
        
        # Embed watermark in original image (invisible)
        watermarked_image = self.embed_steganographic_watermark(
            image_array,
            json.dumps(metadata)
        )
        
        return {
            "encrypted_data": encrypted_image,
            "watermarked_image": watermarked_image,
            "metadata": metadata,
            "salt": salt,
            "iv": iv
        }

    def decrypt_image(self, encrypted_data: bytes, metadata: dict, 
                     image_key: bytes) -> np.ndarray:
        """
        Decrypt image from encrypted bytes
        
        Args:
            encrypted_data: Encrypted image bytes
            metadata: Metadata dictionary with IV and shape
            image_key: Decryption key
            
        Returns:
            Decrypted image as numpy array
        """
        iv = bytes.fromhex(metadata['iv'])
        
        # Decrypt
        cipher = Cipher(
            algorithms.AES(image_key),
            modes.CBC(iv),
            backend=self.backend
        )
        decryptor = cipher.decryptor()
        decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()
        
        # Remove PKCS7 padding
        padding_length = decrypted_padded[-1]
        decrypted_bytes = decrypted_padded[:-padding_length]
        
        # Reshape to original image dimensions
        image_array = np.frombuffer(decrypted_bytes, dtype=np.uint8)
        image_array = image_array.reshape(metadata['image_shape'])
        
        return image_array

    def verify_pixel_integrity(self, image_array: np.ndarray, 
                              original_signature: str) -> bool:
        """
        Verify image hasn't been tampered with using pixel signature
        
        Args:
            image_array: Current image array
            original_signature: Original pixel signature from metadata
            
        Returns:
            True if signature matches, False otherwise
        """
        current_signature = self.generate_pixel_signature(image_array)
        return current_signature == original_signature
