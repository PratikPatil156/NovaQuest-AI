import React, { useState, useRef } from 'react';

export default function Sidebar({ 
  stats, 
  onUpload, 
  onDeleteDoc, 
  onResetDb, 
  isUploading, 
  isResetting 
}) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [confirmReset, setConfirmReset] = useState(false);
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = () => {
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onUpload(e.dataTransfer.files);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      onUpload(e.target.files);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  const handleResetClick = () => {
    if (confirmReset) {
      onResetDb();
      setConfirmReset(false);
    } else {
      setConfirmReset(true);
      // Auto cancel reset confirm after 4 seconds
      setTimeout(() => {
        setConfirmReset(false);
      }, 4000);
    }
  };

  return (
    <aside className="sidebar">
      {/* Brand Header */}
      <div className="sidebar-header">
        <div className="logo-container">
          <svg viewBox="0 0 24 24">
            <path d="M12 2c-.1 0-.2.1-.2.2l-1.2 4.4a1 1 0 0 1-.7.7L5.5 8.5c-.1 0-.2.1-.2.2s.1.2.2.2l4.4 1.2c.3.1.6.4.7.7l1.2 4.4c0 .1.1.2.2.2s.2-.1.2-.2l1.2-4.4c.1-.3.4-.6.7-.7l4.4-1.2c.1 0 .2-.1.2-.2s-.1-.2-.2-.2l-4.4-1.2a1 1 0 0 1-.7-.7L12.2 2.2c0-.1-.1-.2-.2-.2z" />
            <path d="M19 15c-.05 0-.1.05-.1.1l-.6 2.2a.5.5 0 0 1-.35.35l-2.2.6c-.05 0-.1.05-.1.1s.05.1.1.1l2.2.6c.15.05.3.2.35.35l.6 2.2c0 .05.05.1.1.1s.1-.05.1-.1l.6-2.2a.5.5 0 0 1 .35-.35l2.2-.6c.05 0 .1-.05.1-.1s-.05-.1-.1-.1l-2.2-.6a.5.5 0 0 1-.35-.35l-.6-2.2c0-.05-.05-.1-.1-.1z" />
          </svg>
        </div>
        <div className="logo-title-group">
          <h1>NovaQuest AI</h1>
          <div className="subtitle">Knowledge Deck</div>
        </div>
      </div>

      {/* Main Control Panel Body */}
      <div className="sidebar-scrollable-content">
        {/* Connection status */}
        <div className="connection-badge">
          <span className={`status-dot ${stats.connected ? 'connected' : 'disconnected'}`}></span>
          <span>{stats.connected ? 'Engine Active' : 'Offline'}</span>
        </div>

        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-title">Managed Files</div>
            <div className="metric-value">{stats.documents ? stats.documents.length : 0}</div>
          </div>
        </div>

        {/* File Ingestion Drag-and-Drop Area */}
        <div 
          className={`uploader-container ${isDragOver ? 'dragover' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={triggerFileInput}
        >
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileChange} 
            multiple 
            accept=".pdf,.txt,.md" 
            style={{ display: 'none' }} 
          />
          <span className="uploader-icon">
            {isUploading ? '🛰️' : '📥'}
          </span>
          <p className="uploader-text">
            {isUploading ? 'Ingesting data nodes...' : 'Upload Knowledge Files'}
          </p>
          <p className="uploader-subtext">
            Drag & drop PDF, TXT, or MD here or click to browse
          </p>
        </div>

        {/* Managed Documents Inventory */}
        <div className="doc-manager-section">
          <div className="section-header">
            <span className="section-title">Ingested Repositories</span>
          </div>

          <div className="doc-list">
            {stats.documents && stats.documents.length > 0 ? (
              stats.documents.map((doc, idx) => (
                <div key={idx} className="doc-item" title={doc}>
                  <span className="doc-name">📄 {doc}</span>
                  <button 
                    className="doc-delete-btn" 
                    onClick={(e) => {
                      e.stopPropagation();
                      onDeleteDoc(doc);
                    }}
                    title={`Delete ${doc}`}
                  >
                    <svg viewBox="0 0 24 24">
                      <path fill="currentColor" d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z" />
                    </svg>
                  </button>
                </div>
              ))
            ) : (
              <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', textAlign: 'center', marginTop: '10px' }}>
                No active document vectors.
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Danger Zone Controls */}
      <div className="sidebar-footer">
        <button 
          className="btn btn-danger-outline" 
          onClick={handleResetClick}
          disabled={isResetting}
        >
          <svg viewBox="0 0 24 24" width="16" height="16">
            <path fill="currentColor" d="M15 16h2v-2h-2v2zm0-4h2V8h-2v4zM9 16h2V8H9v8zm3-12c-4.97 0-9 4.03-9 9s4.03 9 9 9 9-4.03 9-9-4.03-9-9-9zm0 16c-3.86 0-7-3.14-7-7s3.14-7 7-7 7 3.14 7 7-3.14 7-7 7z" />
          </svg>
          {isResetting 
            ? 'Purging Engine...' 
            : confirmReset 
              ? 'Click to Confirm Wipe!' 
              : 'Wipe Database'
          }
        </button>
      </div>
    </aside>
  );
}
