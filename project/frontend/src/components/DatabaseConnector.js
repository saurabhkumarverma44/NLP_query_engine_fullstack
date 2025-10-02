import React, { useState } from 'react';

const DatabaseConnector = ({ onConnectionSuccess, connectionStatus }) => {
  const [connectionString, setConnectionString] = useState('');
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState('');
  const [showExamples, setShowExamples] = useState(false);

  const connectionExamples = [
    {
      type: 'Demo Database',
      value: 'demo://employee-database',
      description: 'Use this for testing and demonstration'
    },
    {
      type: 'SQLite',
      value: 'sqlite:///./data/employees.db',
      description: 'Local SQLite database file'
    },
    {
      type: 'PostgreSQL',
      value: 'postgresql://user:password@localhost:5432/employees',
      description: 'PostgreSQL database connection'
    },
    {
      type: 'MySQL',
      value: 'mysql://user:password@localhost:3306/employees',
      description: 'MySQL database connection'
    }
  ];

  const handleConnect = async () => {
    if (!connectionString.trim()) {
      setError('Please enter a connection string');
      return;
    }

    setIsConnecting(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/connect-database', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          connection_string: connectionString,
          test_connection: true
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Poll for connection status
        pollConnectionStatus(data.job_id);
      } else {
        setError(data.detail || 'Connection failed');
        setIsConnecting(false);
      }
    } catch (error) {
      setError('Network error: Could not connect to backend');
      setIsConnecting(false);
    }
  };

  const pollConnectionStatus = async (jobId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/ingestion-status/${jobId}`);
      const data = await response.json();

      if (response.ok) {
        if (data.status === 'completed') {
          setIsConnecting(false);
          onConnectionSuccess(data.schema);
        } else if (data.status === 'failed') {
          setError(data.message || 'Connection failed');
          setIsConnecting(false);
        } else {
          // Still processing, poll again
          setTimeout(() => pollConnectionStatus(jobId), 1000);
        }
      } else {
        setError('Failed to check connection status');
        setIsConnecting(false);
      }
    } catch (error) {
      setError('Network error while checking status');
      setIsConnecting(false);
    }
  };

  const handleTestConnection = async () => {
    if (!connectionString.trim()) {
      setError('Please enter a connection string');
      return;
    }

    // For demo purposes, just validate the format
    if (connectionString.includes('demo://')) {
      alert('✅ Demo connection string is valid!');
      setError('');
    } else if (connectionString.includes('://')) {
      alert('✅ Connection string format looks valid!');
      setError('');
    } else {
      setError('Invalid connection string format');
    }
  };

  const selectExample = (example) => {
    setConnectionString(example.value);
    setShowExamples(false);
    setError('');
  };

  return (
    <div className="database-connector">
      <div className="connection-form">
        <div className="input-group">
          <label htmlFor="connection-string">Connection String</label>
          <input
            id="connection-string"
            type="text"
            value={connectionString}
            onChange={(e) => setConnectionString(e.target.value)}
            placeholder="Enter database connection string..."
            disabled={isConnecting}
            className={error ? 'error' : ''}
          />
          {error && <div className="error-message">{error}</div>}
        </div>

        <div className="examples-section">
          <button
            type="button"
            className="examples-toggle"
            onClick={() => setShowExamples(!showExamples)}
          >
            📋 Connection String Examples {showExamples ? '▲' : '▼'}
          </button>
          
          {showExamples && (
            <div className="examples-list">
              {connectionExamples.map((example, index) => (
                <div key={index} className="example-item">
                  <div className="example-header">
                    <strong>{example.type}</strong>
                    <button
                      className="use-example-btn"
                      onClick={() => selectExample(example)}
                    >
                      Use This
                    </button>
                  </div>
                  <code className="example-value">{example.value}</code>
                  <p className="example-description">{example.description}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="action-buttons">
          <button
            className="test-button secondary"
            onClick={handleTestConnection}
            disabled={isConnecting || !connectionString.trim()}
          >
            🧪 Test Connection
          </button>
          
          <button
            className="connect-button primary"
            onClick={handleConnect}
            disabled={isConnecting || !connectionString.trim()}
          >
            {isConnecting ? (
              <>
                <span className="loading-spinner"></span>
                Connecting...
              </>
            ) : (
              <>🔌 Connect & Analyze</>
            )}
          </button>
        </div>

        {connectionStatus === 'connected' && (
          <div className="success-message">
            ✅ Database connected successfully! Schema discovered and ready for queries.
          </div>
        )}
      </div>

      <style jsx>{`
        .database-connector {
          padding: 1rem;
        }

        .connection-form {
          display: flex;
          flex-direction: column;
          gap: 1.5rem;
        }

        .input-group {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .input-group label {
          font-weight: 500;
          color: #374151;
        }

        .input-group input {
          padding: 0.75rem 1rem;
          border: 2px solid #e5e7eb;
          border-radius: 0.5rem;
          font-size: 1rem;
          transition: border-color 0.2s;
        }

        .input-group input:focus {
          outline: none;
          border-color: #3b82f6;
        }

        .input-group input.error {
          border-color: #ef4444;
        }

        .input-group input:disabled {
          background-color: #f9fafb;
          cursor: not-allowed;
        }

        .error-message {
          color: #ef4444;
          font-size: 0.875rem;
          margin-top: 0.25rem;
        }

        .examples-section {
          border: 1px solid #e5e7eb;
          border-radius: 0.5rem;
          overflow: hidden;
        }

        .examples-toggle {
          width: 100%;
          padding: 0.75rem 1rem;
          background: #f9fafb;
          border: none;
          text-align: left;
          cursor: pointer;
          font-weight: 500;
          transition: background-color 0.2s;
        }

        .examples-toggle:hover {
          background: #f3f4f6;
        }

        .examples-list {
          padding: 1rem;
          display: flex;
          flex-direction: column;
          gap: 1rem;
          background: white;
        }

        .example-item {
          padding: 1rem;
          border: 1px solid #e5e7eb;
          border-radius: 0.5rem;
          background: #f8fafc;
        }

        .example-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.5rem;
        }

        .use-example-btn {
          background: #3b82f6;
          color: white;
          border: none;
          padding: 0.25rem 0.75rem;
          border-radius: 0.25rem;
          cursor: pointer;
          font-size: 0.875rem;
        }

        .use-example-btn:hover {
          background: #2563eb;
        }

        .example-value {
          display: block;
          background: #1f2937;
          color: #f9fafb;
          padding: 0.5rem;
          border-radius: 0.25rem;
          font-family: monospace;
          margin: 0.5rem 0;
          word-break: break-all;
        }

        .example-description {
          font-size: 0.875rem;
          color: #6b7280;
          margin: 0;
        }

        .action-buttons {
          display: flex;
          gap: 1rem;
        }

        .test-button, .connect-button {
          flex: 1;
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 0.5rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
        }

        .test-button {
          background: #f3f4f6;
          color: #374151;
          border: 1px solid #d1d5db;
        }

        .test-button:hover:not(:disabled) {
          background: #e5e7eb;
        }

        .connect-button {
          background: #3b82f6;
          color: white;
        }

        .connect-button:hover:not(:disabled) {
          background: #2563eb;
        }

        .test-button:disabled, .connect-button:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .loading-spinner {
          width: 16px;
          height: 16px;
          border: 2px solid transparent;
          border-top: 2px solid currentColor;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          to {
            transform: rotate(360deg);
          }
        }

        .success-message {
          background: #ecfdf5;
          color: #065f46;
          padding: 0.75rem 1rem;
          border-radius: 0.5rem;
          border: 1px solid #a7f3d0;
        }

        @media (max-width: 640px) {
          .action-buttons {
            flex-direction: column;
          }
          
          .example-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.5rem;
          }
        }
      `}</style>
    </div>
  );
};

export default DatabaseConnector;