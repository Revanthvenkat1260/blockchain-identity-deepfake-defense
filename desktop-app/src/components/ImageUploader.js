import React, { useState } from 'react';
import './ImageUploader.css';

function ImageUploader({ onImageSelected }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file) => {
    if (file.type.startsWith('image/')) {
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreview(e.target.result);
        onImageSelected({ file, preview: e.target.result });
      };
      reader.readAsDataURL(file);
    } else {
      alert('Please select an image file');
    }
  };

  return (
    <div className="image-uploader">
      <div
        className={`upload-area ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="file-input"
          accept="image/*"
          onChange={handleChange}
          style={{ display: 'none' }}
        />
        <label htmlFor="file-input" className="upload-label">
          <div className="upload-icon">📸</div>
          <h3>Drag and drop your image here</h3>
          <p>or click to browse</p>
        </label>
      </div>

      {preview && (
        <div className="preview-container">
          <h3>Preview</h3>
          <img src={preview} alt="Preview" className="preview-image" />
          <p>File: {selectedFile.name}</p>
          <p>Size: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
        </div>
      )}
    </div>
  );
}

export default ImageUploader;
