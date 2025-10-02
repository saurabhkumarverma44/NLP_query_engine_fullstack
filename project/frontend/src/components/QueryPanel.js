import React, { useState, useRef, useEffect } from 'react';

const QueryPanel = ({ onQuerySubmit, isLoading, schemaData }) => {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [queryHistory, setQueryHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [showSchema, setShowSchema] = useState(false);
  const [showTips, setShowTips] = useState(false);
  const inputRef = useRef(null);

  const sampleQueries = [
    {
      query: "How many employees do we have?",
      description: "Get total employee count",
      category: "Count"
    },
    {
      query: "Show me all employees in Engineering",
      description: "List employees by department",
      category: "Filter"
    },
    {
      query: "What is the average salary by department?",
      description: "Calculate salary statistics",
      category: "Aggregation"
    },
    {
      query: "List the highest paid employees",
      description: "Show top earners",
      category: "Ranking"
    },
    {
      query: "Who was hired this year?",
      description: "Recent hires",
      category: "Temporal"
    },
    {
      query: "Find employees with Python skills",
      description: "Search skills in documents",
      category: "Skills"
    }
  ];

  const queryTips = [
    {
      title: "Natural Language",
      tip: "Ask questions in plain English, like 'How many employees work in Sales?'"
    },
    {
      title: "Be Specific",
      tip: "Include details: 'Show employees hired after 2020 with salary above 80k'"
    },
    {
      title: "Use Comparisons",
      tip: "Try 'highest paid', 'newest employees', 'largest department'"
    },
    {
      title: "Search Skills",
      tip: "Find talent: 'employees with JavaScript skills' or 'Python developers'"
    }
  ];

  useEffect(() => {
    fetchQueryHistory();
  }, []);

  const fetchQueryHistory = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/query-history?limit=10');
      if (response.ok) {
        const data = await response.json();
        setQueryHistory(data);
      }
    } catch (error) {
      console.error('Failed to fetch query history:', error);
    }
  };

  const fetchSuggestions = async (partialQuery) => {
    if (partialQuery.length < 2) {
      setSuggestions([]);
      return;
    }

    try {
      const response = await fetch(`http://localhost:8000/api/query-suggestions?partial_query=${encodeURIComponent(partialQuery)}`);
      if (response.ok) {
        const data = await response.json();
        setSuggestions(data.suggestions || []);
      }
    } catch (error) {
      console.error('Failed to fetch suggestions:', error);
      setSuggestions([]);
    }
  };

  const handleQueryChange = (e) => {
    const value = e.target.value;
    setQuery(value);
    
    if (value.trim()) {
      fetchSuggestions(value);
      setShowSuggestions(true);
    } else {
      setShowSuggestions(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onQuerySubmit({ query: query.trim() });
      setShowSuggestions(false);
      fetchQueryHistory(); // Refresh history after query
    }
  };

  const selectQuery = (selectedQuery) => {
    setQuery(selectedQuery);
    setShowSuggestions(false);
    setShowHistory(false);
    inputRef.current?.focus();
  };

  const clearQuery = () => {
    setQuery('');
    setShowSuggestions(false);
    inputRef.current?.focus();
  };

  return (
    <div className="query-panel">
      <div className="query-header">
        <h2>🔍 Natural Language Query</h2>
        <p>Ask questions about your employee data in plain English</p>
      </div>

      <form onSubmit={handleSubmit} className="query-form">
        <div className="query-input-container">
          <div className="input-wrapper">
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={handleQueryChange}
              placeholder="How many employees do we have?"
              disabled={isLoading}
              className="query-input"
              onFocus={() => {
                if (query.trim()) setShowSuggestions(true);
              }}
              onBlur={() => {
                // Delay to allow clicking on suggestions
                setTimeout(() => setShowSuggestions(false), 200);
              }}
            />
            
            {query && (
              <button
                type="button"
                onClick={clearQuery}
                className="clear-button"
                disabled={isLoading}
              >
                ✕
              </button>
            )}
          </div>

          {showSuggestions && suggestions.length > 0 && (
            <div className="suggestions-dropdown">
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  type="button"
                  className="suggestion-item"
                  onClick={() => selectQuery(suggestion)}
                >
                  🔍 {suggestion}
                </button>
              ))}
            </div>
          )}
        </div>

        <button 
          type="submit" 
          disabled={!query.trim() || isLoading}
          className="search-button"
        >
          {isLoading ? (
            <>
              <span className="loading-spinner"></span>
              Searching...
            </>
          ) : (
            <>🔍 Search</>
          )}
        </button>
      </form>

      <div className="panel-sections">
        {/* Sample Queries */}
        <div className="panel-section">
          <button
            className="section-toggle"
            onClick={() => setShowHistory(!showHistory)}
          >
            💡 Try These Sample Queries {showHistory ? '▲' : '▼'}
          </button>
          
          {showHistory && (
            <div className="sample-queries">
              {sampleQueries.map((item, index) => (
                <div key={index} className="sample-query-item">
                  <button
                    className="sample-query-button"
                    onClick={() => selectQuery(item.query)}
                  >
                    <div className="query-text">{item.query}</div>
                    <div className="query-description">{item.description}</div>
                    <span className="query-category">{item.category}</span>
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Query History */}
        {queryHistory.length > 0 && (
          <div className="panel-section">
            <button
              className="section-toggle"
              onClick={() => setShowHistory(!showHistory)}
            >
              🕐 Recent Queries ({queryHistory.length}) {showHistory ? '▲' : '▼'}
            </button>
            
            {showHistory && (
              <div className="query-history">
                {queryHistory.slice(0, 5).map((item, index) => (
                  <div key={index} className="history-item">
                    <button
                      className="history-query-button"
                      onClick={() => selectQuery(item.query)}
                    >
                      <div className="history-query">{item.query}</div>
                      <div className="history-meta">
                        <span className="history-type">{item.query_type}</span>
                        <span className="history-time">{Math.round(item.response_time)}ms</span>
                        {item.cache_hit && <span className="cache-hit">📦 cached</span>}
                      </div>
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Available Data */}
        {schemaData && (
          <div className="panel-section">
            <button
              className="section-toggle"
              onClick={() => setShowSchema(!showSchema)}
            >
              📊 Available Data ({schemaData.total_tables || 0} tables) {showSchema ? '▲' : '▼'}
            </button>
            
            {showSchema && (
              <div className="schema-info">
                {schemaData.tables?.map((table, index) => (
                  <div key={index} className="schema-table">
                    <div className="table-name">{table.name}</div>
                    <div className="table-details">
                      {table.columns?.length || 0} columns • {table.row_count || 0} rows
                    </div>
                    <div className="table-columns">
                      {table.columns?.slice(0, 3).map((col, colIndex) => (
                        <span key={colIndex} className="column-name">
                          {col.name}
                        </span>
                      ))}
                      {table.columns?.length > 3 && (
                        <span className="more-columns">
                          +{table.columns.length - 3} more
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Query Tips */}
        <div className="panel-section">
          <button
            className="section-toggle"
            onClick={() => setShowTips(!showTips)}
          >
            💡 Query Writing Tips {showTips ? '▲' : '▼'}
          </button>
          
          {showTips && (
            <div className="query-tips">
              {queryTips.map((tip, index) => (
                <div key={index} className="tip-item">
                  <div className="tip-title">{tip.title}</div>
                  <div className="tip-content">{tip.tip}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <style jsx>{`
        .query-panel {
          padding: 2rem;
          height: 100%;
          display: flex;
          flex-direction: column;
          overflow-y: auto;
        }

        .query-header {
          margin-bottom: 2rem;
          text-align: center;
        }

        .query-header h2 {
          color: #374151;
          margin-bottom: 0.5rem;
        }

        .query-header p {
          color: #6b7280;
        }

        .query-form {
          margin-bottom: 2rem;
        }

        .query-input-container {
          position: relative;
          margin-bottom: 1rem;
        }

        .input-wrapper {
          position: relative;
          display: flex;
          align-items: center;
        }

        .query-input {
          width: 100%;
          padding: 1rem 3rem 1rem 1rem;
          border: 2px solid #e5e7eb;
          border-radius: 0.75rem;
          font-size: 1rem;
          transition: border-color 0.2s;
        }

        .query-input:focus {
          outline: none;
          border-color: #3b82f6;
        }

        .query-input:disabled {
          background-color: #f9fafb;
          cursor: not-allowed;
        }

        .clear-button {
          position: absolute;
          right: 1rem;
          background: none;
          border: none;
          color: #9ca3af;
          cursor: pointer;
          font-size: 1rem;
          padding: 0.25rem;
        }

        .clear-button:hover {
          color: #374151;
        }

        .suggestions-dropdown {
          position: absolute;
          top: 100%;
          left: 0;
          right: 0;
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 0.5rem;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
          z-index: 10;
          max-height: 200px;
          overflow-y: auto;
        }

        .suggestion-item {
          width: 100%;
          text-align: left;
          padding: 0.75rem 1rem;
          border: none;
          background: white;
          cursor: pointer;
          transition: background-color 0.2s;
          border-bottom: 1px solid #f3f4f6;
        }

        .suggestion-item:last-child {
          border-bottom: none;
        }

        .suggestion-item:hover {
          background: #f9fafb;
        }

        .search-button {
          width: 100%;
          padding: 0.75rem 1.5rem;
          background: #3b82f6;
          color: white;
          border: none;
          border-radius: 0.5rem;
          font-weight: 500;
          cursor: pointer;
          transition: background-color 0.2s;
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 0.5rem;
        }

        .search-button:hover:not(:disabled) {
          background: #2563eb;
        }

        .search-button:disabled {
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

        .panel-sections {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 1rem;
          overflow-y: auto;
        }

        .panel-section {
          border: 1px solid #e5e7eb;
          border-radius: 0.5rem;
          overflow: hidden;
        }

        .section-toggle {
          width: 100%;
          text-align: left;
          padding: 0.75rem 1rem;
          background: #f9fafb;
          border: none;
          font-weight: 500;
          cursor: pointer;
          transition: background-color 0.2s;
        }

        .section-toggle:hover {
          background: #f3f4f6;
        }

        .sample-queries,
        .query-history,
        .schema-info,
        .query-tips {
          padding: 1rem;
          background: white;
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
        }

        .sample-query-item {
          border: 1px solid #e5e7eb;
          border-radius: 0.5rem;
          overflow: hidden;
        }

        .sample-query-button {
          width: 100%;
          text-align: left;
          padding: 1rem;
          background: white;
          border: none;
          cursor: pointer;
          transition: background-color 0.2s;
        }

        .sample-query-button:hover {
          background: #f8fafc;
        }

        .query-text {
          font-weight: 500;
          color: #374151;
          margin-bottom: 0.25rem;
        }

        .query-description {
          font-size: 0.875rem;
          color: #6b7280;
          margin-bottom: 0.5rem;
        }

        .query-category {
          background: #e0e7ff;
          color: #3730a3;
          padding: 0.25rem 0.5rem;
          border-radius: 0.25rem;
          font-size: 0.75rem;
          font-weight: 500;
        }

        .history-item {
          padding: 0.75rem;
          border: 1px solid #f3f4f6;
          border-radius: 0.5rem;
          background: #f9fafb;
        }

        .history-query-button {
          width: 100%;
          text-align: left;
          background: none;
          border: none;
          cursor: pointer;
          padding: 0;
        }

        .history-query {
          font-weight: 500;
          color: #374151;
          margin-bottom: 0.5rem;
        }

        .history-meta {
          display: flex;
          gap: 1rem;
          font-size: 0.75rem;
          color: #6b7280;
        }

        .history-type {
          background: #f3f4f6;
          padding: 0.125rem 0.5rem;
          border-radius: 0.25rem;
        }

        .cache-hit {
          color: #059669;
        }

        .schema-table {
          padding: 0.75rem;
          border: 1px solid #f3f4f6;
          border-radius: 0.5rem;
          background: #f9fafb;
        }

        .table-name {
          font-weight: 600;
          color: #374151;
          margin-bottom: 0.25rem;
        }

        .table-details {
          font-size: 0.875rem;
          color: #6b7280;
          margin-bottom: 0.5rem;
        }

        .table-columns {
          display: flex;
          flex-wrap: wrap;
          gap: 0.25rem;
        }

        .column-name {
          background: #e2e8f0;
          color: #475569;
          padding: 0.125rem 0.375rem;
          border-radius: 0.25rem;
          font-size: 0.75rem;
        }

        .more-columns {
          background: #f1f5f9;
          color: #64748b;
          padding: 0.125rem 0.375rem;
          border-radius: 0.25rem;
          font-size: 0.75rem;
        }

        .tip-item {
          padding: 0.75rem;
          border: 1px solid #f3f4f6;
          border-radius: 0.5rem;
          background: #f9fafb;
        }

        .tip-title {
          font-weight: 600;
          color: #374151;
          margin-bottom: 0.25rem;
        }

        .tip-content {
          font-size: 0.875rem;
          color: #6b7280;
        }

        @media (max-width: 640px) {
          .query-panel {
            padding: 1rem;
          }
          
          .query-input {
            padding: 0.75rem 2.5rem 0.75rem 0.75rem;
          }
          
          .search-button {
            padding: 0.75rem;
          }
        }
      `}</style>
    </div>
  );
};

export default QueryPanel;