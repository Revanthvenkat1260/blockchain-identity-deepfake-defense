import React, { useState } from 'react';
import axios from 'axios';
import './DeepfakeDetector.css';

function DeepfakeDetector() {
  const [image, setImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [detecting, setDetecting] = useState(false);
  const [result, setResult] = useState(null);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(file);
      const reader = new FileReader();
      reader.onload = (event) => {
        setPreview(event.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleDetect = async () => {
    if (!image) return;

    setDetecting(true);
    const formData = new FormData();
    formData.append('image', image);

    try {
      const response = await axios.post(
        'http://localhost:5000/api/v1/verify/deepfake',
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      );

      setResult(response.data);
    } catch (error) {
      console.error('Detection failed:', error);
      setResult({ error: error.message });
    } finally {
      setDetecting(false);
    }
  };

  return (
    <div className="deepfake-detector">
      <div className="detector-input">
        <input
          type="file"
          accept="image/*"
          onChange={handleImageChange}
          disabled={detecting}
        />
      </div>

      {preview && (
        <div className="detector-preview">
          <img src={preview} alt="Verification image" />
        </div>
      )}

      {preview && !detecting && (
        <button className="primary-btn" onClick={handleDetect}>
          Analyze Image
        </button>
      )}

      {detecting && (
        <div className="detector-loading">
          <div className="spinner"></div>
          <p>Analyzing image for deepfake artifacts...</p>
        </div>
      )}

      {result && (
        <div className={`detector-result ${result.is_deepfake ? 'deepfake' : 'authentic'}`}>
          <h3>{result.is_deepfake ? '⚠️ Deepfake Detected' : '✓ Image Authentic'}</h3>
          <p><strong>Confidence:</strong> {(result.confidence * 100).toFixed(1)}%</p>
          <p><strong>Recommendation:</strong> {result.recommendation}</p>
          
          <div className="model-results">
            <h4>Model Analysis:</h4>
            {Object.entries(result.models).map(([model, details]) => (
              <div key={model} className="model-item">
                <span>{model}</span>
                <span className={details.is_deepfake ? 'fake' : 'authentic'}>
                  {details.is_deepfake ? 'FAKE' : 'AUTHENTIC'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default DeepfakeDetector;
