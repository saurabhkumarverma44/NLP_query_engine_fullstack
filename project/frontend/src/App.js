import React, { useState, useEffect } from 'react';
import './App.css';
import DatabaseConnector from './components/DatabaseConnector';
import DocumentUploader from './components/DocumentUploader';
import QueryPanel from './components/QueryPanel';
import ResultsView from './components/ResultsView';

function App() {
  const [currentView, setCurrentView] = useState('connect'); // 'connect', 'query'
  const [schemaData, setSchemaData] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [documentsCount, setDocumentsCount] = useState(0);
  const [queryResults, setQueryResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [systemMetrics, setSystemMetrics] = useState(null);

  // Check system status on mount
  useEffect(() => {
    checkSystemStatus();
    fetchMetrics();
    
    // Set up periodic metrics updates
    const metricsInterval = setInterval(fetchMetrics, 30000); // Every 30 seconds
    
    return () => clearInterval(metricsInterval);
  }, []);

  const checkSystemStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/health');
      if (response.ok) {
        const data = await response.json();
        console.log('Backend is running:', data);
      }
    } catch (error) {
      console.error('Backend connection failed:', error);
    }
  };

  const fetchMetrics = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/metrics');
      if (response.ok) {
        const data = await response.json();
        setSystemMetrics(data);
      }
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    }
  };

  const handleConnectionSuccess = (schema) => {
    setSchemaData(schema);
    setConnectionStatus('connected');
    fetchMetrics(); // Update metrics after connection
  };

  const handleDocumentsUploaded = (count) => {
    setDocumentsCount(prev => prev + count);
    fetchMetrics(); // Update metrics after document upload
  };

  const handleQuerySubmit = async (queryData) => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: queryData.query }),
      });

      if (response.ok) {
        const results = await response.json();
        setQueryResults(results);
        fetchMetrics(); // Update metrics after query
      } else {
        console.error('Query failed');
        setQueryResults({
          error: 'Query processing failed',
          results: [],
          query_type: 'error'
        });
      }
    } catch (error) {
      console.error('Query error:', error);
      setQueryResults({
        error: 'Network error occurred',
        results: [],
        query_type: 'error'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.body.classList.toggle('dark-mode');
  };

  return (
    <div className={`App ${darkMode ? 'dark-mode' : ''}`}>
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="logo-section">
            <h1>🔍 NLP Query Engine</h1>
            <p>AI-powered database and document search</p>
          </div>
          <div className="header-controls">
            <div className="status-indicators">
              <span className={`status-badge ${connectionStatus === 'connected' ? 'connected' : 'disconnected'}`}>
                {connectionStatus === 'connected' ? '✅ Connected' : '⚠️ Disconnected'}
              </span>
              {documentsCount > 0 && (
                <span className="status-badge documents">📄 {documentsCount} docs</span>
              )}
              {systemMetrics && (
                <span className="status-badge metrics">
                  ⚡ {Math.round(systemMetrics.average_response_time)}ms avg
                </span>
              )}
            </div>
            <button 
              className="theme-toggle"
              onClick={toggleDarkMode}
              title={`Switch to ${darkMode ? 'light' : 'dark'} mode`}
            >
              {darkMode ? '☀️' : '🌙'}
            </button>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="main-nav">
        <div className="nav-container">
          <button 
            className={`nav-button ${currentView === 'connect' ? 'active' : ''}`}
            onClick={() => setCurrentView('connect')}
          >
            📊 Connect Data
          </button>
          <button 
            className={`nav-button ${currentView === 'query' ? 'active' : ''}`}
            onClick={() => setCurrentView('query')}
            disabled={connectionStatus !== 'connected' && documentsCount === 0}
          >
            🔍 Query Data
          </button>
        </div>
      </nav>

      {/* Main Content */}
      <main className="main-content">
        {currentView === 'connect' && (
          <div className="connect-view fade-in">
            {/* Data Connection Grid */}
            <div className="data-connection-grid">
              {/* Database Connection */}
              <div className="connection-card">
                <div className="card-header">
                  <h2>🗄️ Database Connection</h2>
                  <p>Connect to your employee database to enable SQL queries</p>
                </div>
                <div className="card-content">
                  <DatabaseConnector 
                    onConnectionSuccess={handleConnectionSuccess}
                    connectionStatus={connectionStatus}
                  />
                </div>
              </div>

              {/* Document Upload */}
              <div className="connection-card">
                <div className="card-header">
                  <h2>📁 Document Upload</h2>
                  <p>Upload employee documents for content search</p>
                </div>
                <div className="card-content">
                  <DocumentUploader 
                    onDocumentsUploaded={handleDocumentsUploaded}
                    documentsCount={documentsCount}
                  />
                </div>
              </div>
            </div>

            {/* Schema Visualization */}
            {schemaData && (
              <div className="schema-section slide-up">
                <div className="section-header">
                  <h2>📋 Discovered Database Schema</h2>
                  <p>Automatically discovered database structure and relationships</p>
                </div>
                
                <div className="schema-summary">
                  <div className="schema-stats">
                    <div className="stat-item">
                      <span className="stat-value">{schemaData.total_tables || 0}</span>
                      <span className="stat-label">Tables</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-value">{schemaData.total_columns || 0}</span>
                      <span className="stat-label">Columns</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-value">{schemaData.relationships?.length || 0}</span>
                      <span className="stat-label">Relationships</span>
                    </div>
                  </div>
                  
                  <div className="tables-list">
                    {schemaData.tables?.map((table, index) => (
                      <div key={index} className="table-card">
                        <div className="table-header">
                          <h4>{table.name}</h4>
                          <span className="table-category">{table.category}</span>
                        </div>
                        <div className="table-info">
                          <p>{table.columns?.length || 0} columns • {table.row_count || 0} rows</p>
                        </div>
                        <div className="table-columns">
                          {table.columns?.slice(0, 4).map((column, colIndex) => (
                            <span key={colIndex} className="column-tag">
                              {column.name}
                            </span>
                          ))}
                          {table.columns?.length > 4 && (
                            <span className="column-tag more">
                              +{table.columns.length - 4} more
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* System Metrics */}
            {systemMetrics && (
              <div className="metrics-section">
                <div className="section-header">
                  <h3>📊 System Performance</h3>
                </div>
                <div className="metrics-grid">
                  <div className="metric-card">
                    <span className="metric-value">{systemMetrics.total_queries}</span>
                    <span className="metric-label">Total Queries</span>
                  </div>
                  <div className="metric-card">
                    <span className="metric-value">{Math.round(systemMetrics.cache_hit_rate * 100)}%</span>
                    <span className="metric-label">Cache Hit Rate</span>
                  </div>
                  <div className="metric-card">
                    <span className="metric-value">{Math.round(systemMetrics.average_response_time)}ms</span>
                    <span className="metric-label">Avg Response Time</span>
                  </div>
                  <div className="metric-card">
                    <span className="metric-value">{systemMetrics.active_connections}</span>
                    <span className="metric-label">Active Connections</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {currentView === 'query' && (
          <div className="query-view fade-in">
            <div className="query-interface">
              <div className="query-panel-section">
                <QueryPanel 
                  onQuerySubmit={handleQuerySubmit}
                  isLoading={isLoading}
                  schemaData={schemaData}
                />
              </div>
              
              <div className="results-section">
                <ResultsView 
                  results={queryResults}
                  isLoading={isLoading}
                />
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <div className="footer-content">
          <div className="footer-left">
            <p>© 2024 NLP Query Engine • Built with React & FastAPI</p>
          </div>
          <div className="footer-right">
            <div className="footer-links">
              <span>Status: {connectionStatus}</span>
              <span>•</span>
              <span>Documents: {documentsCount}</span>
              <span>•</span>
              <span>Version: 1.0.0</span>
              {systemMetrics?.total_queries > 0 && (
                <>
                  <span>•</span>
                  <span>Queries: {systemMetrics.total_queries}</span>
                </>
              )}
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;;
