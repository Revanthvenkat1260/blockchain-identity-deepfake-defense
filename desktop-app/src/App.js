import React, { useState } from 'react';
import './App.css';
import ImageUploader from './components/ImageUploader';
import EncryptionStatus from './components/EncryptionStatus';
import DeepfakeDetector from './components/DeepfakeDetector';
import Navigation from './components/Navigation';

function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [selectedImage, setSelectedImage] = useState(null);
  const [encryptionResult, setEncryptionResult] = useState(null);

  const handleImageSelected = (image) => {
    setSelectedImage(image);
  };

  const handleEncryptionComplete = (result) => {
    setEncryptionResult(result);
  };

  return (
    <div className="App">
      <Navigation currentPage={currentPage} setCurrentPage={setCurrentPage} />
      
      <div className="container">
        {currentPage === 'home' && (
          <div className="page home-page">
            <h1>🛡️ Deepfake Defense Platform</h1>
            <p>Protect your identity with blockchain-based image authentication</p>
            <div className="features">
              <div className="feature-card">
                <h3>🔐 Encryption</h3>
                <p>Military-grade AES-256 encryption for your images</p>
              </div>
              <div className="feature-card">
                <h3>🧠 AI Detection</h3>
                <p>Advanced ML models to detect deepfakes and tampering</p>
              </div>
              <div className="feature-card">
                <h3>⛓️ Blockchain</h3>
                <p>Immutable ownership records on Polygon blockchain</p>
              </div>
            </div>
            <button onClick={() => setCurrentPage('encrypt')} className="primary-btn">
              Get Started
            </button>
          </div>
        )}

        {currentPage === 'encrypt' && (
          <div className="page encrypt-page">
            <h2>Encrypt & Protect Your Image</h2>
            <ImageUploader onImageSelected={handleImageSelected} />
            {selectedImage && (
              <EncryptionStatus 
                image={selectedImage}
                onComplete={handleEncryptionComplete}
              />
            )}
          </div>
        )}

        {currentPage === 'verify' && (
          <div className="page verify-page">
            <h2>Verify Image Authenticity</h2>
            <DeepfakeDetector />
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
