import React, { useState, useRef } from 'react';

const DocumentUploader = ({ onDocumentsUploaded, documentsCount }) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const fileInputRef = useRef(null);

  const supportedTypes = [
    { ext: '.pdf', type: 'PDF Documents', icon: '📄' },
    { ext: '.docx', type: 'Word Documents', icon: '📝' },
    { ext: '.txt', type: 'Text Files', icon: '📃' },
    { ext: '.csv', type: 'CSV Files', icon: '📊' },
    { ext: '.json', type: 'JSON Files', icon: '🔗' }
  ];

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  };

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files);
    handleFiles(files);
  };

  const handleFiles = async (files) => {
    if (files.length === 0) return;

    // Validate files
    const validFiles = [];
    const invalidFiles = [];

    files.forEach(file => {
      const extension = '.' + file.name.split('.').pop().toLowerCase();
      const isSupported = supportedTypes.some(type => type.ext === extension);
      const isValidSize = file.size <= 10 * 1024 * 1024; // 10MB limit

      if (isSupported && isValidSize) {
        validFiles.push(file);
      } else {
        invalidFiles.push({
          name: file.name,
          issue: !isSupported ? 'Unsupported file type' : 'File too large (max 10MB)'
        });
      }
    });

    if (invalidFiles.length > 0) {
      setError(`Invalid files: ${invalidFiles.map(f => `${f.name} (${f.issue})`).join(', ')}`);
    } else {
      setError('');
    }

    if (validFiles.length > 0) {
      await uploadFiles(validFiles);
    }
  };

  const uploadFiles = async (files) => {
    setIsUploading(true);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      files.forEach(file => {
        formData.append('files', file);
      });

      const response = await fetch('http://localhost:8000/api/upload-documents', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        // Poll for upload status
        pollUploadStatus(data.job_id, files.length);
      } else {
        setError(data.detail || 'Upload failed');
        setIsUploading(false);
      }
    } catch (error) {
      setError('Network error: Could not upload files');
      setIsUploading(false);
    }
  };

  const pollUploadStatus = async (jobId, totalFiles) => {
    try {
      const response = await fetch(`http://localhost:8000/api/ingestion-status/${jobId}`);
      const data = await response.json();

      if (response.ok) {
        setUploadProgress(data.progress || 0);
        
        if (data.status === 'completed') {
          setIsUploading(false);
          setUploadProgress(100);
          setUploadedFiles(prev => [
            ...prev,
            { 
              id: jobId, 
              count: totalFiles, 
              timestamp: new Date().toLocaleTimeString(),
              message: data.message 
            }
          ]);
          onDocumentsUploaded(totalFiles);
          
          // Clear file input
          if (fileInputRef.current) {
            fileInputRef.current.value = '';
          }
        } else if (data.status === 'failed') {
          setError(data.message || 'Upload failed');
          setIsUploading(false);
        } else {
          // Still processing, poll again
          setTimeout(() => pollUploadStatus(jobId, totalFiles), 1000);
        }
      } else {
        setError('Failed to check upload status');
        setIsUploading(false);
      }
    } catch (error) {
      setError('Network error while checking status');
      setIsUploading(false);
    }
  };

  const clearError = () => setError('');

  return (
    <div className="document-uploader">
      <div
        className={`drop-zone ${isDragOver ? 'drag-over' : ''} ${isUploading ? 'uploading' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.txt,.csv,.json"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
          disabled={isUploading}
        />
        
        <div className="drop-zone-content">
          {isUploading ? (
            <div className="uploading-state">
              <div className="upload-spinner"></div>
              <h3>Uploading Documents...</h3>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
              <p>{uploadProgress}% Complete</p>
            </div>
          ) : (
            <div className="idle-state">
              <div className="upload-icon">📁</div>
              <h3>Drop files here or click to browse</h3>
              <p>Upload employee documents for content search</p>
              <div className="supported-formats">
                <span>Supports: PDF, DOCX, TXT, CSV, JSON</span>
                <span className="file-limit">Max file size: 10MB</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="error-message">
          <span>{error}</span>
          <button onClick={clearError} className="close-error">×</button>
        </div>
      )}

      <div className="file-types-grid">
        <h4>📋 Supported File Types</h4>
        <div className="file-types-list">
          {supportedTypes.map((type, index) => (
            <div key={index} className="file-type-item">
              <span className="file-icon">{type.icon}</span>
              <div className="file-info">
                <strong>{type.ext.toUpperCase()}</strong>
                <span>{type.type}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="document-status">
        <h4>📊 Document Status</h4>
        <div className="status-summary">
          <div className="status-item">
            <span className="status-value">{documentsCount}</span>
            <span className="status-label">Documents Indexed</span>
          </div>
          {uploadedFiles.length > 0 && (
            <div className="recent-uploads">
              <h5>Recent Uploads:</h5>
              {uploadedFiles.slice(-3).map((upload, index) => (
                <div key={upload.id} className="upload-item">
                  ✅ {upload.count} files at {upload.timestamp}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <style jsx>{`
        .document-uploader {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
          padding: 1rem;
        }

        .drop-zone {
          border: 2px dashed #d1d5db;
          border-radius: 0.75rem;
          padding: 3rem 2rem;
          text-align: center;
          cursor: pointer;
          transition: all 0.2s;
          background: #f9fafb;
          min-height: 200px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .drop-zone:hover {
          border-color: #3b82f6;
          background: #f0f9ff;
        }

        .drop-zone.drag-over {
          border-color: #3b82f6;
          background: #dbeafe;
        }

        .drop-zone.uploading {
          border-color: #10b981;
          background: #ecfdf5;
          cursor: not-allowed;
        }

        .drop-zone-content {
          width: 100%;
        }

        .idle-state .upload-icon {
          font-size: 3rem;
          margin-bottom: 1rem;
        }

        .idle-state h3 {
          color: #374151;
          margin-bottom: 0.5rem;
          font-size: 1.25rem;
        }

        .idle-state p {
          color: #6b7280;
          margin-bottom: 1rem;
        }

        .supported-formats {
          display: flex;
          flex-direction: column;
          gap: 0.25rem;
          font-size: 0.875rem;
          color: #6b7280;
        }

        .file-limit {
          font-size: 0.75rem;
          color: #9ca3af;
        }

        .uploading-state .upload-spinner {
          width: 40px;
          height: 40px;
          border: 4px solid #e5e7eb;
          border-top: 4px solid #3b82f6;
          border-radius: 50%;
          animation: spin 1s linear infinite;
          margin: 0 auto 1rem auto;
        }

        @keyframes spin {
          to {
            transform: rotate(360deg);
          }
        }

        .uploading-state h3 {
          color: #10b981;
          margin-bottom: 1rem;
          font-size: 1.25rem;
        }

        .progress-bar {
          width: 100%;
          height: 8px;
          background: #e5e7eb;
          border-radius: 4px;
          overflow: hidden;
          margin: 1rem 0;
        }

        .progress-fill {
          height: 100%;
          background: linear-gradient(90deg, #3b82f6, #10b981);
          transition: width 0.3s ease;
        }

        .uploading-state p {
          color: #6b7280;
          font-weight: 500;
        }

        .error-message {
          display: flex;
          justify-content: space-between;
          align-items: center;
          background: #fef2f2;
          color: #dc2626;
          padding: 0.75rem 1rem;
          border-radius: 0.5rem;
          border: 1px solid #fecaca;
        }

        .close-error {
          background: none;
          border: none;
          color: #dc2626;
          cursor: pointer;
          font-size: 1.25rem;
          padding: 0;
          margin-left: 1rem;
        }

        .file-types-grid {
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 0.5rem;
          padding: 1.5rem;
        }

        .file-types-grid h4 {
          margin-bottom: 1rem;
          color: #374151;
        }

        .file-types-list {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 0.75rem;
        }

        .file-type-item {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.75rem;
          background: #f8fafc;
          border-radius: 0.5rem;
          border: 1px solid #e2e8f0;
        }

        .file-icon {
          font-size: 1.5rem;
        }

        .file-info {
          display: flex;
          flex-direction: column;
        }

        .file-info strong {
          color: #374151;
          font-size: 0.875rem;
        }

        .file-info span {
          color: #6b7280;
          font-size: 0.75rem;
        }

        .document-status {
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 0.5rem;
          padding: 1.5rem;
        }

        .document-status h4 {
          margin-bottom: 1rem;
          color: #374151;
        }

        .status-summary {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .status-item {
          text-align: center;
          background: #f0f9ff;
          padding: 1rem;
          border-radius: 0.5rem;
          border: 1px solid #bae6fd;
        }

        .status-value {
          display: block;
          font-size: 2rem;
          font-weight: 700;
          color: #0369a1;
          margin-bottom: 0.25rem;
        }

        .status-label {
          color: #075985;
          font-size: 0.875rem;
          font-weight: 500;
        }

        .recent-uploads {
          background: #f8fafc;
          padding: 1rem;
          border-radius: 0.5rem;
        }

        .recent-uploads h5 {
          color: #374151;
          margin-bottom: 0.5rem;
          font-size: 0.875rem;
        }

        .upload-item {
          font-size: 0.75rem;
          color: #6b7280;
          margin-bottom: 0.25rem;
        }

        @media (max-width: 640px) {
          .drop-zone {
            padding: 2rem 1rem;
          }
          
          .file-types-list {
            grid-template-columns: 1fr;
          }
          
          .drop-zone-content h3 {
            font-size: 1.125rem;
          }
        }
      `}</style>
    </div>
  );
};

export default DocumentUploader;