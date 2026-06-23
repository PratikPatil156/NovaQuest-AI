import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';

export default function App() {
  const [stats, setStats] = useState({
    connected: false,
    has_api_key: false,
    chunk_count: 0,
    documents: []
  });
  
  const [messages, setMessages] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isResetting, setIsResetting] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Synchronize stats from the FastAPI backend
  const fetchStats = async () => {
    try {
      const response = await fetch('/api/stats');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      } else {
        setStats(prev => ({ ...prev, connected: false }));
      }
    } catch (error) {
      console.error('API Connection Error:', error);
      setStats(prev => ({ ...prev, connected: false }));
    }
  };

  // Run on mount and establish a light polling interface to monitor connection
  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 60000); // refresh every minute
    return () => clearInterval(interval);
  }, []);

  // Multi-file upload ingestion pipeline handler
  const handleUpload = async (files) => {
    if (files.length === 0) return;
    setIsUploading(true);
    
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Upload success:', result.message);
        setStats(prev => ({
          ...prev,
          chunk_count: result.chunk_count,
          documents: result.documents
        }));
      } else {
        const errorData = await response.json();
        alert(`Ingestion failed: ${errorData.detail || 'Server error'}`);
      }
    } catch (error) {
      console.error('Error uploading files:', error);
      alert('Network error uploading files. Ensure the FastAPI backend is running.');
    } finally {
      setIsUploading(false);
    }
  };

  // Single-file deletion handler
  const handleDeleteDoc = async (filename) => {
    try {
      const response = await fetch(`/api/documents/${encodeURIComponent(filename)}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Delete success:', result.message);
        setStats(prev => ({
          ...prev,
          chunk_count: result.chunk_count,
          documents: result.documents
        }));
      } else {
        alert('Could not delete document.');
      }
    } catch (error) {
      console.error('Error deleting document:', error);
    }
  };

  // Quantum database wipe reset handler
  const handleResetDb = async () => {
    setIsResetting(true);
    try {
      const response = await fetch('/api/reset', {
        method: 'POST',
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Reset success:', result.message);
        setStats(prev => ({
          ...prev,
          chunk_count: 0,
          documents: []
        }));
        setMessages([]); // Clear chat logs
      } else {
        alert('Error resetting database.');
      }
    } catch (error) {
      console.error('Error resetting DB:', error);
    } finally {
      setIsResetting(false);
    }
  };

  // load sample documentation handler
  const handleLoadSample = async () => {
    setIsUploading(true);
    try {
      const response = await fetch('/api/load-sample', {
        method: 'POST',
      });

      if (response.ok) {
        const result = await response.json();
        setStats(prev => ({
          ...prev,
          chunk_count: result.chunk_count,
          documents: result.documents
        }));
      } else {
        const errorData = await response.json();
        alert(`Failed to load sample: ${errorData.detail || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error loading sample guide:', error);
    } finally {
      setIsUploading(false);
    }
  };

  // Chat prompting query execution
  const handleSend = async (queryText) => {
    // 1. Add user query to conversation array
    const userMessage = { role: 'user', content: queryText };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: queryText }),
      });

      if (response.ok) {
        const result = await response.json();
        const assistantMessage = {
          role: 'assistant',
          content: result.answer,
          sources: result.sources
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        const assistantMessage = {
          role: 'assistant',
          content: '❌ **Quantum Core Connection Fault:** The retrieval synthesis system encountered an internal execution exception.',
          sources: []
        };
        setMessages(prev => [...prev, assistantMessage]);
      }
    } catch (error) {
      console.error('Error querying engine:', error);
      const assistantMessage = {
        role: 'assistant',
        content: '❌ **Network Connection Fault:** Could not establish communication links with the backend services. Verify the server is running on port `8000`.',
        sources: []
      };
      setMessages(prev => [...prev, assistantMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <Sidebar 
        stats={stats}
        onUpload={handleUpload}
        onDeleteDoc={handleDeleteDoc}
        onResetDb={handleResetDb}
        isUploading={isUploading}
        isResetting={isResetting}
      />
      <ChatWindow 
        messages={messages}
        onSend={handleSend}
        isLoading={isLoading}
        onLoadSample={handleLoadSample}
        hasDocs={stats.chunk_count > 0}
      />
    </div>
  );
}
