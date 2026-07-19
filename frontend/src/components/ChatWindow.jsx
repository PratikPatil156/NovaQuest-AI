import React, { useState, useEffect, useRef } from 'react';

export default function ChatWindow({ 
  messages, 
  onSend, 
  isLoading, 
  onLoadSample, 
  hasDocs 
}) {
  const [input, setInput] = useState('');
  const [selectedCitation, setSelectedCitation] = useState(null);
  const scrollRef = useRef(null);

  // Auto-scroll to bottom of chat logs when new messages arrive
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSend(input.trim());
    setInput('');
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <main className="main-workspace">
      {/* Top Navigation Workspace Header */}
      <div className="workspace-header">
        <div className="header-text">
          <h2>Knowledge Retrieval Terminal</h2>
          <p>Retrieve and synthesize high-context knowledge from indexed files</p>
        </div>
      </div>

      {/* Chat Messages Display Container */}
      <div className="chat-container" ref={scrollRef}>
        {messages.length === 0 ? (
          <div className="welcome-screen">
            <span className="welcome-emoji">🛰️</span>
            <h3>Welcome to NovaQuest AI</h3>
            <p>
              Your high-fidelity cosmic RAG environment. Upload knowledge bases in the sidebar and query the core engine for instant, cited intelligence.
            </p>
            
            {!hasDocs && (
              <div className="quickstart-grid">
                <div className="quickstart-card" onClick={onLoadSample}>
                  <div className="quickstart-card-header">
                    <span>🚀</span>
                    <span>Load Sample Zero-G Guidelines</span>
                  </div>
                  <p>Instantly feed rules regarding gravity flux, space office decorum, and jetpack charging logs to test the retrieval synthesis.</p>
                </div>
              </div>
            )}
          </div>
        ) : (
          messages.map((msg, index) => (
            <div key={index} className={`message-row ${msg.role}`}>
              <div className="avatar">
                {msg.role === 'user' ? '👨‍💻' : '🤖'}
              </div>
              <div className="message-content">
                <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
                

              </div>
            </div>
          ))
        )}

        {/* Loading Spinner typing indicator */}
        {isLoading && (
          <div className="message-row assistant">
            <div className="avatar">🤖</div>
            <div className="message-content">
              <div className="typing-indicator">
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
                <div className="typing-dot"></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Interactive Input Deck */}
      <div className="input-area">
        <div className="input-glow-wrapper">
          <form className="input-form" onSubmit={handleSubmit}>
            <textarea
              className="chat-input"
              rows="1"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={hasDocs ? "Ask NovaQuest Core..." : "Upload documents in the control panel to query..."}
              disabled={!hasDocs || isLoading}
            />
            <button 
              type="submit" 
              className="send-btn" 
              disabled={!input.trim() || !hasDocs || isLoading}
            >
              <svg viewBox="0 0 24 24">
                <path fill="currentColor" d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
              </svg>
            </button>
          </form>
        </div>
        <div className="input-notice">
          
        </div>
      </div>

      {/* Citation Details Lightbox Modal */}
      {selectedCitation && (
        <div className="modal-overlay" onClick={() => setSelectedCitation(null)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h4>Citation Node Details</h4>
              <button className="modal-close" onClick={() => setSelectedCitation(null)}>×</button>
            </div>
            <div className="modal-body">
              <p style={{ marginBottom: '8px' }}>
                <strong>Source:</strong> <code>{selectedCitation.file}</code>
              </p>
              <p style={{ marginBottom: '14px' }}>
                <strong>Index Page Reference:</strong> Page {selectedCitation.page}
              </p>
              <strong>Retrieved Context Chunk:</strong>
              <div className="citation-snippet-box">
                "{selectedCitation.snippet}"
              </div>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
