import React, { useState } from 'react';

const ResultsView = ({ results, isLoading }) => {
  const [exportFormat, setExportFormat] = useState('csv');
  const [showSqlQuery, setShowSqlQuery] = useState(false);

  const exportData = () => {
    if (!results || !results.results) return;

    const data = results.results;
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
    
    if (exportFormat === 'csv') {
      exportToCSV(data, `query-results-${timestamp}.csv`);
    } else if (exportFormat === 'json') {
      exportToJSON(results, `query-results-${timestamp}.json`);
    }
  };

  const exportToCSV = (data, filename) => {
    if (!data.length) return;
    
    const headers = Object.keys(data[0]);
    const csvContent = [
      headers.join(','),
      ...data.map(row => 
        headers.map(header => {
          const value = row[header];
          return typeof value === 'string' && value.includes(',') 
            ? `"${value}"` 
            : value;
        }).join(',')
      )
    ].join('\n');
    
    downloadFile(csvContent, filename, 'text/csv');
  };

  const exportToJSON = (data, filename) => {
    const jsonContent = JSON.stringify(data, null, 2);
    downloadFile(jsonContent, filename, 'application/json');
  };

  const downloadFile = (content, filename, mimeType) => {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const renderTableData = (data) => {
    if (!data || !data.length) return null;

    const headers = Object.keys(data[0]);
    
    return (
      <div className="table-container">
        <table className="results-table">
          <thead>
            <tr>
              {headers.map((header, index) => (
                <th key={index}>{header.replace(/_/g, ' ').toUpperCase()}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row, rowIndex) => (
              <tr key={rowIndex}>
                {headers.map((header, colIndex) => (
                  <td key={colIndex}>
                    {formatCellValue(row[header], header)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const formatCellValue = (value, header) => {
    if (value === null || value === undefined) return '—';
    
    // Format salary values
    if (header.toLowerCase().includes('salary') && typeof value === 'number') {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
      }).format(value);
    }
    
    // Format dates
    if (header.toLowerCase().includes('date') && value) {
      try {
        const date = new Date(value);
        return date.toLocaleDateString();
      } catch (error) {
        return value;
      }
    }
    
    // Format numbers
    if (typeof value === 'number') {
      return new Intl.NumberFormat().format(value);
    }
    
    return value;
  };

  const renderDocumentResults = (data) => {
    return (
      <div className="document-results">
        {data.map((doc, index) => (
          <div key={index} className="document-card">
            <div className="document-header">
              <div className="document-title">
                📄 {doc.filename || `Document ${index + 1}`}
              </div>
              <div className="relevance-score">
                {Math.round((doc.relevance_score || 0) * 100)}% relevant
              </div>
            </div>
            <div className="document-content">
              {doc.matching_chunks?.map((chunk, chunkIndex) => (
                <div key={chunkIndex} className="text-chunk">
                  <div className="chunk-text">{chunk.chunk_text}</div>
                  <div className="chunk-score">
                    Match: {Math.round((chunk.match_score || 0) * 100)}%
                  </div>
                </div>
              )) || (
                <div className="chunk-text">{doc.content || 'No content available'}</div>
              )}
            </div>
          </div>
        ))}
      </div>
    );
  };

  const renderHybridResults = (data) => {
    const databaseResults = data.filter(item => item.source === 'database' || !item.source);
    const documentResults = data.filter(item => item.source === 'document');

    return (
      <div className="hybrid-results">
        {databaseResults.length > 0 && (
          <div className="results-section">
            <h4>🗄️ Database Results</h4>
            {renderTableData(databaseResults)}
          </div>
        )}
        
        {documentResults.length > 0 && (
          <div className="results-section">
            <h4>📄 Document Results</h4>
            {renderDocumentResults(documentResults)}
          </div>
        )}
      </div>
    );
  };

  const renderHelpMessage = (data) => {
    return (
      <div className="help-message">
        <div className="help-content">
          <h3>💡 {data[0].message}</h3>
          {data[0].suggestions && (
            <div className="suggestions-list">
              {data[0].suggestions.map((suggestion, index) => (
                <div key={index} className="suggestion-item">
                  "• {suggestion}"
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="results-view loading">
        <div className="loading-content">
          <div className="loading-spinner"></div>
          <h3>⏳ Processing your query...</h3>
          <div className="loading-steps">
            <div className="step active">• Analyzing your natural language query</div>
            <div className="step">• Searching database and documents</div>
            <div className="step">• Preparing results</div>
          </div>
        </div>

        <style jsx>{`
          .results-view.loading {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            padding: 2rem;
          }

          .loading-content {
            text-align: center;
            color: #6b7280;
          }

          .loading-spinner {
            width: 50px;
            height: 50px;
            border: 4px solid #f3f4f6;
            border-top: 4px solid #3b82f6;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 2rem auto;
          }

          @keyframes spin {
            to {
              transform: rotate(360deg);
            }
          }

          .loading-content h3 {
            margin-bottom: 1.5rem;
            color: #374151;
          }

          .loading-steps {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            text-align: left;
            max-width: 300px;
          }

          .step {
            padding: 0.5rem 0;
            color: #9ca3af;
            transition: color 0.3s;
          }

          .step.active {
            color: #3b82f6;
            font-weight: 500;
          }
        `}</style>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="results-view empty">
        <div className="empty-content">
          <div className="empty-icon">🔍</div>
          <h3>Ready to search</h3>
          <p>Enter a query to see results here</p>
          <div className="example-queries">
            <h4>Try asking:</h4>
            <ul>
              <li>"How many employees do we have?"</li>
              <li>"Show me the Engineering team"</li>
              <li>"What's the average salary?"</li>
            </ul>
          </div>
        </div>

        <style jsx>{`
          .results-view.empty {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            padding: 2rem;
          }

          .empty-content {
            text-align: center;
            color: #6b7280;
          }

          .empty-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
            opacity: 0.5;
          }

          .empty-content h3 {
            color: #374151;
            margin-bottom: 0.5rem;
          }

          .empty-content p {
            margin-bottom: 2rem;
          }

          .example-queries h4 {
            color: #374151;
            margin-bottom: 1rem;
          }

          .example-queries ul {
            text-align: left;
            color: #6b7280;
            list-style: none;
            padding: 0;
          }

          .example-queries li {
            padding: 0.25rem 0;
          }
        `}</style>
      </div>
    );
  }

  if (results.error) {
    return (
      <div className="results-view error">
        <div className="error-content">
          <div className="error-icon">⚠️</div>
          <h3>Query Error</h3>
          <p>{results.error}</p>
          <button className="retry-button" onClick={() => window.location.reload()}>
            Try Again
          </button>
        </div>

        <style jsx>{`
          .results-view.error {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100%;
            padding: 2rem;
          }

          .error-content {
            text-align: center;
            color: #dc2626;
          }

          .error-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
          }

          .error-content h3 {
            margin-bottom: 1rem;
          }

          .error-content p {
            color: #6b7280;
            margin-bottom: 2rem;
          }

          .retry-button {
            background: #dc2626;
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 0.5rem;
            cursor: pointer;
            font-weight: 500;
          }

          .retry-button:hover {
            background: #b91c1c;
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className="results-view">
      <div className="results-header">
        <div className="results-info">
          <span className="result-type">
            {results.query_type === 'sql' && '🗄️ SQL'}
            {results.query_type === 'document' && '📄 Document'}
            {results.query_type === 'hybrid' && '🔗 Hybrid'}
            {results.query_type === 'help' && '💡 Help'}
          </span>
          
          <span className="result-count">
            {results.total_results} result{results.total_results !== 1 ? 's' : ''}
          </span>
          
          <span className="response-time">
            ⚡ {Math.round(results.response_time)}ms
            {results.cache_hit && <span className="cache-indicator">📦 cached</span>}
          </span>
        </div>

        {results.query_type !== 'help' && results.results && results.results.length > 0 && (
          <div className="export-controls">
            <select 
              value={exportFormat} 
              onChange={(e) => setExportFormat(e.target.value)}
              className="export-select"
            >
              <option value="csv">CSV</option>
              <option value="json">JSON</option>
            </select>
            <button onClick={exportData} className="export-button">
              📥 Export
            </button>
          </div>
        )}
      </div>

      {results.sql_query && (
        <div className="sql-section">
          <button
            className="sql-toggle"
            onClick={() => setShowSqlQuery(!showSqlQuery)}
          >
            🔍 Generated SQL Query {showSqlQuery ? '▲' : '▼'}
          </button>
          {showSqlQuery && (
            <div className="sql-query">
              <code>{results.sql_query}</code>
            </div>
          )}
        </div>
      )}

      <div className="results-content">
        {results.query_type === 'help' && renderHelpMessage(results.results)}
        {results.query_type === 'hybrid' && renderHybridResults(results.results)}
        {results.query_type === 'document' && renderDocumentResults(results.results)}
        {(results.query_type === 'sql' || (!results.query_type && results.results)) && renderTableData(results.results)}
      </div>

      {results.sources && results.sources.length > 0 && (
        <div className="sources-section">
          <div className="sources-label">📊 Data Sources:</div>
          <div className="sources-list">
            {results.sources.map((source, index) => (
              <span key={index} className="source-tag">
                {source}
              </span>
            ))}
          </div>
        </div>
      )}

      <style jsx>{`
        .results-view {
          padding: 2rem;
          height: 100%;
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }

        .results-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 1.5rem;
          flex-wrap: wrap;
          gap: 1rem;
        }

        .results-info {
          display: flex;
          align-items: center;
          gap: 1rem;
          flex-wrap: wrap;
        }

        .result-type {
          background: #f3f4f6;
          color: #374151;
          padding: 0.25rem 0.75rem;
          border-radius: 0.25rem;
          font-weight: 500;
          font-size: 0.875rem;
        }

        .result-count {
          color: #6b7280;
          font-size: 0.875rem;
        }

        .response-time {
          color: #6b7280;
          font-size: 0.875rem;
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .cache-indicator {
          color: #059669;
          font-size: 0.75rem;
        }

        .export-controls {
          display: flex;
          align-items: center;
          gap: 0.5rem;
        }

        .export-select {
          padding: 0.5rem;
          border: 1px solid #d1d5db;
          border-radius: 0.375rem;
          background: white;
          font-size: 0.875rem;
        }

        .export-button {
          background: #3b82f6;
          color: white;
          border: none;
          padding: 0.5rem 1rem;
          border-radius: 0.375rem;
          cursor: pointer;
          font-size: 0.875rem;
          font-weight: 500;
        }

        .export-button:hover {
          background: #2563eb;
        }

        .sql-section {
          margin-bottom: 1.5rem;
          border: 1px solid #e5e7eb;
          border-radius: 0.5rem;
          overflow: hidden;
        }

        .sql-toggle {
          width: 100%;
          text-align: left;
          padding: 0.75rem 1rem;
          background: #f9fafb;
          border: none;
          cursor: pointer;
          font-weight: 500;
          transition: background-color 0.2s;
        }

        .sql-toggle:hover {
          background: #f3f4f6;
        }

        .sql-query {
          padding: 1rem;
          background: #1f2937;
          color: #f9fafb;
        }

        .sql-query code {
          font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
          font-size: 0.875rem;
          line-height: 1.5;
          white-space: pre-wrap;
          word-break: break-all;
        }

        .results-content {
          flex: 1;
          overflow: auto;
          margin-bottom: 1rem;
        }

        .table-container {
          overflow-x: auto;
          border-radius: 0.5rem;
          border: 1px solid #e5e7eb;
        }

        .results-table {
          width: 100%;
          border-collapse: collapse;
          font-size: 0.875rem;
        }

        .results-table th {
          background: #f9fafb;
          color: #374151;
          font-weight: 600;
          padding: 0.75rem 1rem;
          text-align: left;
          border-bottom: 1px solid #e5e7eb;
        }

        .results-table td {
          padding: 0.75rem 1rem;
          border-bottom: 1px solid #f3f4f6;
          vertical-align: top;
        }

        .results-table tr:hover {
          background: #f8fafc;
        }

        .document-results {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .document-card {
          border: 1px solid #e5e7eb;
          border-radius: 0.5rem;
          background: white;
          overflow: hidden;
        }

        .document-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 1rem;
          background: #f9fafb;
          border-bottom: 1px solid #e5e7eb;
        }

        .document-title {
          font-weight: 600;
          color: #374151;
        }

        .relevance-score {
          background: #dbeafe;
          color: #1e40af;
          padding: 0.25rem 0.5rem;
          border-radius: 0.25rem;
          font-size: 0.75rem;
          font-weight: 500;
        }

        .document-content {
          padding: 1rem;
        }

        .text-chunk {
          margin-bottom: 1rem;
          padding-bottom: 1rem;
          border-bottom: 1px solid #f3f4f6;
        }

        .text-chunk:last-child {
          margin-bottom: 0;
          padding-bottom: 0;
          border-bottom: none;
        }

        .chunk-text {
          color: #374151;
          line-height: 1.6;
          margin-bottom: 0.5rem;
        }

        .chunk-score {
          font-size: 0.75rem;
          color: #6b7280;
        }

        .hybrid-results {
          display: flex;
          flex-direction: column;
          gap: 2rem;
        }

        .results-section h4 {
          margin-bottom: 1rem;
          color: #374151;
        }

        .help-message {
          text-align: center;
          padding: 2rem;
        }

        .help-content h3 {
          color: #374151;
          margin-bottom: 2rem;
        }

        .suggestions-list {
          text-align: left;
          max-width: 400px;
          margin: 0 auto;
        }

        .suggestion-item {
          padding: 0.5rem 0;
          color: #6b7280;
          border-bottom: 1px solid #f3f4f6;
        }

        .sources-section {
          display: flex;
          align-items: center;
          gap: 1rem;
          padding-top: 1rem;
          border-top: 1px solid #e5e7eb;
          margin-top: auto;
        }

        .sources-label {
          font-size: 0.875rem;
          font-weight: 500;
          color: #374151;
        }

        .sources-list {
          display: flex;
          gap: 0.5rem;
        }

        .source-tag {
          background: #e0e7ff;
          color: #3730a3;
          padding: 0.25rem 0.5rem;
          border-radius: 0.25rem;
          font-size: 0.75rem;
          font-weight: 500;
        }

        @media (max-width: 640px) {
          .results-view {
            padding: 1rem;
          }
          
          .results-header {
            flex-direction: column;
            align-items: flex-start;
          }
          
          .table-container {
            font-size: 0.75rem;
          }
          
          .results-table th,
          .results-table td {
            padding: 0.5rem;
          }
        }
      `}</style>
    </div>
  );
};

export default ResultsView;