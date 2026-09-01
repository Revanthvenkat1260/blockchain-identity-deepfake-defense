import React, { useState } from 'react';
import axios from 'axios';
import './EncryptionStatus.css';

function EncryptionStatus({ image, onComplete }) {
  const [status, setStatus] = useState('ready');
  const [result, setResult] = useState(null);
  const [progress, setProgress] = useState(0);

  const handleEncrypt = async () => {
    setStatus('encrypting');
    setProgress(0);

    try {
      const formData = new FormData();
      formData.append('image', image.file);
      formData.append('did', 'did:polygon:example');

      // Simulate encryption progress
      const interval = setInterval(() => {
        setProgress(prev => (prev < 90 ? prev + 10 : prev));
      }, 200);

      const response = await axios.post(
        'http://localhost:5000/api/v1/images/encrypt',
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );

      clearInterval(interval);
      setProgress(100);
      setStatus('complete');
      setResult(response.data);
      onComplete(response.data);
    } catch (error) {
      console.error('Encryption failed:', error);
      setStatus('error');
      setResult({ error: error.message });
    }
  };

  return (
    <div className="encryption-status">
      <h3>Encryption Process</h3>
      
      <div className="status-info">
        <div className="status-step">
          <span className="step-icon">✓</span>
          <span>Image Loaded</span>
        </div>
        <div className="status-step">
          <span className={`step-icon ${status === 'encrypting' ? 'active' : ''}`}>🔐</span>
          <span>Encrypting with AES-256</span>
        </div>
        <div className="status-step">
          <span className={`step-icon ${status === 'complete' ? 'active' : ''}`}>⛓️</span>
          <span>Minting NFT on Blockchain</span>
        </div>
      </div>

      {status === 'encrypting' && (
        <div className="progress-container">
          <div className="progress-bar" style={{ width: `${progress}%` }}></div>
          <p>{progress}%</p>
        </div>
      )}

      {status === 'complete' && result && (
        <div className="result-container success">
          <h4>✓ Encryption Successful!</h4>
          <p><strong>Encryption ID:</strong> {result.encryption_id}</p>
          <p><strong>Pixel Signature:</strong> {result.pixel_signature.substring(0, 32)}...</p>
          <button className="primary-btn" onClick={() => window.location.href = '/verify'}>
            Verify Image
          </button>
        </div>
      )}

      {status === 'error' && result && (
        <div className="result-container error">
          <h4>✗ Encryption Failed</h4>
          <p>{result.error}</p>
        </div>
      )}

      {status === 'ready' && (
        <button className="primary-btn" onClick={handleEncrypt}>
          Start Encryption
        </button>
      )}
    </div>
  );
}

export default EncryptionStatus;
