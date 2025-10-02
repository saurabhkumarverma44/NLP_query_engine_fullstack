query_engine_py_content = '''
import asyncio
import uuid
import re
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum

from .schema_discovery import SchemaDiscovery
from .document_processor import DocumentProcessor


class QueryType(Enum):
    SQL = "sql"
    DOCUMENT = "document"
    HYBRID = "hybrid"
    UNKNOWN = "unknown"


class QueryEngine:
    """Main query processing engine"""
    
    def __init__(self):
        self.schema_discovery = SchemaDiscovery()
        self.document_processor = DocumentProcessor()
        
        # Query cache (use Redis in production)
        self.query_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Current database schema
        self.current_schema = None
        
        # Query patterns for classification
        self.sql_patterns = [
            r'\\bhow many\\b', r'\\bcount\\b', r'\\btotal\\b', r'\\bsum\\b', r'\\baverage\\b',
            r'\\blist\\b', r'\\bshow\\b', r'\\bfind\\b', r'\\bget\\b', r'\\bselect\\b',
            r'\\bemployees?\\b', r'\\bdepartments?\\b', r'\\bsalary\\b', r'\\bpay\\b',
            r'\\bhired?\\b', r'\\bjoined?\\b', r'\\bworking\\b', r'\\breports? to\\b'
        ]
        
        self.document_patterns = [
            r'\\bresume\\b', r'\\bcv\\b', r'\\bskills?\\b', r'\\bexperience\\b',
            r'\\bqualifications?\\b', r'\\beducation\\b', r'\\bcertificates?\\b',
            r'\\breview\\b', r'\\bperformance\\b', r'\\bdocuments?\\b'
        ]
        
    async def process_query(self, user_query: str) -> Dict[str, Any]:
        """
        Main query processing method
        """
        query_id = str(uuid.uuid4())
        start_time = time.time()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(user_query)
            cached_result = self._get_cached_result(cache_key)
            
            if cached_result:
                cached_result["query_id"] = query_id
                cached_result["cache_hit"] = True
                return cached_result
            
            # Classify query type
            query_type = await self._classify_query(user_query)
            
            # Process based on query type
            if query_type == QueryType.SQL:
                result = await self._process_sql_query(user_query)
            elif query_type == QueryType.DOCUMENT:
                result = await self._process_document_query(user_query)
            elif query_type == QueryType.HYBRID:
                result = await self._process_hybrid_query(user_query)
            else:
                result = await self._process_fallback_query(user_query)
            
            # Prepare response
            response = {
                "query_id": query_id,
                "query_type": query_type.value,
                "results": result.get("results", []),
                "total_results": result.get("total_results", 0),
                "sql_query": result.get("sql_query"),
                "sources": result.get("sources", []),
                "metadata": result.get("metadata", {}),
                "cache_hit": False,
                "processing_time": round((time.time() - start_time) * 1000, 2)
            }
            
            # Cache the result
            self._cache_result(cache_key, response)
            
            return response
            
        except Exception as e:
            return {
                "query_id": query_id,
                "query_type": "error",
                "results": [],
                "total_results": 0,
                "error": str(e),
                "cache_hit": False,
                "processing_time": round((time.time() - start_time) * 1000, 2)
            }
    
    async def _classify_query(self, query: str) -> QueryType:
        """Classify the query type based on patterns"""
        query_lower = query.lower()
        
        # Check for SQL patterns
        sql_score = sum(1 for pattern in self.sql_patterns if re.search(pattern, query_lower))
        
        # Check for document patterns
        doc_score = sum(1 for pattern in self.document_patterns if re.search(pattern, query_lower))
        
        # Determine query type
        if sql_score > 0 and doc_score > 0:
            return QueryType.HYBRID
        elif sql_score > 0:
            return QueryType.SQL
        elif doc_score > 0:
            return QueryType.DOCUMENT
        else:
            # Default classification based on content
            if any(word in query_lower for word in ['employee', 'department', 'salary', 'count', 'list', 'show']):
                return QueryType.SQL
            else:
                return QueryType.DOCUMENT
    
    async def _process_sql_query(self, query: str) -> Dict[str, Any]:
        """Process SQL-type queries"""
        try:
            # Generate SQL from natural language
            sql_query = await self._generate_sql(query)
            
            # Execute SQL query (mock execution for demo)
            results = await self._execute_sql_query(sql_query)
            
            return {
                "results": results,
                "total_results": len(results),
                "sql_query": sql_query,
                "sources": ["database"],
                "metadata": {
                    "query_type": "sql",
                    "tables_accessed": self._extract_tables_from_sql(sql_query)
                }
            }
            
        except Exception as e:
            return {
                "results": [],
                "total_results": 0,
                "error": f"SQL query processing failed: {str(e)}",
                "sources": []
            }
    
    async def _process_document_query(self, query: str) -> Dict[str, Any]:
        """Process document search queries"""
        try:
            # Search documents
            document_results = await self.document_processor.search_documents(query, limit=10)
            
            # Format results
            results = []
            for doc_result in document_results:
                results.append({
                    "type": "document",
                    "filename": doc_result["filename"],
                    "relevance_score": doc_result["relevance_score"],
                    "matching_chunks": doc_result["matching_chunks"],
                    "metadata": doc_result["metadata"]
                })
            
            return {
                "results": results,
                "total_results": len(results),
                "sources": ["documents"],
                "metadata": {
                    "query_type": "document",
                    "search_method": "text_matching"
                }
            }
            
        except Exception as e:
            return {
                "results": [],
                "total_results": 0,
                "error": f"Document query processing failed: {str(e)}",
                "sources": []
            }
    
    async def _process_hybrid_query(self, query: str) -> Dict[str, Any]:
        """Process queries that require both SQL and document search"""
        try:
            # Process SQL part
            sql_result = await self._process_sql_query(query)
            
            # Process document part  
            doc_result = await self._process_document_query(query)
            
            # Combine results
            combined_results = []
            
            # Add SQL results
            for result in sql_result.get("results", []):
                result["source_type"] = "database"
                combined_results.append(result)
            
            # Add document results
            for result in doc_result.get("results", []):
                result["source_type"] = "document"
                combined_results.append(result)
            
            return {
                "results": combined_results,
                "total_results": len(combined_results),
                "sql_query": sql_result.get("sql_query"),
                "sources": ["database", "documents"],
                "metadata": {
                    "query_type": "hybrid",
                    "sql_results": len(sql_result.get("results", [])),
                    "document_results": len(doc_result.get("results", []))
                }
            }
            
        except Exception as e:
            return {
                "results": [],
                "total_results": 0,
                "error": f"Hybrid query processing failed: {str(e)}",
                "sources": []
            }
    
    async def _process_fallback_query(self, query: str) -> Dict[str, Any]:
        """Fallback processing for unclassified queries"""
        # Try both SQL and document search
        try:
            hybrid_result = await self._process_hybrid_query(query)
            hybrid_result["metadata"]["query_type"] = "fallback"
            return hybrid_result
        except Exception as e:
            return {
                "results": [{"message": "Unable to process query. Please try rephrasing your question."}],
                "total_results": 1,
                "error": f"Fallback processing failed: {str(e)}",
                "sources": []
            }
    
    async def _generate_sql(self, query: str) -> str:
        """Generate SQL query from natural language"""
        query_lower = query.lower()
        
        # Simple pattern-based SQL generation (enhance with ML models)
        if 'how many employees' in query_lower or 'count employees' in query_lower:
            return "SELECT COUNT(*) as employee_count FROM employees;"
        
        elif 'average salary' in query_lower:
            if 'department' in query_lower:
                return """SELECT d.dept_name, AVG(e.salary) as avg_salary 
                         FROM employees e 
                         JOIN departments d ON e.dept_id = d.dept_id 
                         GROUP BY d.dept_name;"""
            else:
                return "SELECT AVG(salary) as average_salary FROM employees;"
        
        elif 'list employees' in query_lower:
            if 'department' in query_lower:
                return """SELECT e.full_name, e.position, d.dept_name 
                         FROM employees e 
                         JOIN departments d ON e.dept_id = d.dept_id 
                         ORDER BY d.dept_name, e.full_name;"""
            else:
                return "SELECT full_name, position, salary FROM employees ORDER BY full_name;"
        
        elif 'highest paid' in query_lower:
            return "SELECT full_name, position, salary FROM employees ORDER BY salary DESC LIMIT 10;"
        
        elif 'hired' in query_lower and 'year' in query_lower:
            return "SELECT full_name, position, hire_date FROM employees WHERE YEAR(hire_date) = YEAR(CURDATE()) ORDER BY hire_date DESC;"
        
        elif 'departments' in query_lower:
            return "SELECT dept_name, COUNT(*) as employee_count FROM departments d LEFT JOIN employees e ON d.dept_id = e.dept_id GROUP BY d.dept_name;"
        
        else:
            # Generic fallback query
            return "SELECT full_name, position, dept_id FROM employees LIMIT 10;"
    
    async def _execute_sql_query(self, sql_query: str) -> List[Dict[str, Any]]:
        """Execute SQL query (mock implementation)"""
        # Mock data for demonstration
        if 'COUNT(*)' in sql_query.upper():
            return [{"employee_count": 245}]
        
        elif 'AVG(salary)' in sql_query.upper():
            if 'dept_name' in sql_query.lower():
                return [
                    {"dept_name": "Engineering", "avg_salary": 95000.00},
                    {"dept_name": "Sales", "avg_salary": 75000.00},
                    {"dept_name": "HR", "avg_salary": 65000.00},
                    {"dept_name": "Marketing", "avg_salary": 70000.00}
                ]
            else:
                return [{"average_salary": 78500.00}]
        
        elif 'ORDER BY salary DESC' in sql_query.upper():
            return [
                {"full_name": "John Smith", "position": "Senior Engineer", "salary": 120000.00},
                {"full_name": "Sarah Johnson", "position": "Engineering Manager", "salary": 115000.00},
                {"full_name": "Mike Chen", "position": "Principal Architect", "salary": 110000.00},
                {"full_name": "Lisa Wang", "position": "Data Scientist", "salary": 105000.00},
                {"full_name": "David Brown", "position": "Senior Developer", "salary": 100000.00}
            ]
        
        elif 'dept_name' in sql_query.lower() and 'full_name' in sql_query.lower():
            return [
                {"full_name": "Alice Cooper", "position": "Software Engineer", "dept_name": "Engineering"},
                {"full_name": "Bob Wilson", "position": "DevOps Engineer", "dept_name": "Engineering"},
                {"full_name": "Carol Davis", "position": "Sales Manager", "dept_name": "Sales"},
                {"full_name": "David Miller", "position": "HR Specialist", "dept_name": "HR"},
                {"full_name": "Eve Thompson", "position": "Marketing Coordinator", "dept_name": "Marketing"}
            ]
        
        elif 'YEAR(hire_date)' in sql_query.upper():
            return [
                {"full_name": "Tom Anderson", "position": "Junior Developer", "hire_date": "2024-08-15"},
                {"full_name": "Jenny Liu", "position": "Product Manager", "hire_date": "2024-07-01"},
                {"full_name": "Mark Rodriguez", "position": "UX Designer", "hire_date": "2024-06-10"}
            ]
        
        else:
            # Default employee list
            return [
                {"full_name": "Alice Cooper", "position": "Software Engineer", "dept_id": 1},
                {"full_name": "Bob Wilson", "position": "DevOps Engineer", "dept_id": 1},
                {"full_name": "Carol Davis", "position": "Sales Manager", "dept_id": 2},
                {"full_name": "David Miller", "position": "HR Specialist", "dept_id": 3},
                {"full_name": "Eve Thompson", "position": "Marketing Coordinator", "dept_id": 4}
            ]
    
    def _extract_tables_from_sql(self, sql_query: str) -> List[str]:
        """Extract table names from SQL query"""
        # Simple regex to find table names (enhance for production)
        tables = []
        sql_lower = sql_query.lower()
        
        # Common table patterns
        patterns = [
            r'from\\s+(\\w+)',
            r'join\\s+(\\w+)',
            r'update\\s+(\\w+)',
            r'into\\s+(\\w+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, sql_lower)
            tables.extend(matches)
        
        return list(set(tables))  # Remove duplicates
    
    async def get_suggestions(self, partial_query: str) -> List[str]:
        """Get query suggestions based on partial input"""
        suggestions = []
        partial_lower = partial_query.lower()
        
        # Common query patterns
        common_queries = [
            "How many employees do we have?",
            "Show me all employees in Engineering",
            "What is the average salary by department?",
            "List the highest paid employees",
            "Who was hired this year?",
            "Show me all departments",
            "Find employees with Python skills",
            "Show me performance reviews for engineers",
            "List all projects in the Marketing department",
            "What is the total budget for each department?"
        ]
        
        # Filter suggestions based on partial input
        for query in common_queries:
            if partial_lower in query.lower() or any(word in query.lower() for word in partial_lower.split()):
                suggestions.append(query)
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def _generate_cache_key(self, query: str) -> str:
        """Generate cache key for query"""
        import hashlib
        return hashlib.md5(query.lower().strip().encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached query result if available and not expired"""
        if cache_key in self.query_cache:
            cached_item = self.query_cache[cache_key]
            if datetime.now() < cached_item["expires_at"]:
                return cached_item["result"]
            else:
                # Remove expired cache entry
                del self.query_cache[cache_key]
        return None
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]):
        """Cache query result"""
        # Clean up old cache entries periodically
        current_time = datetime.now()
        expired_keys = [k for k, v in self.query_cache.items() if current_time >= v["expires_at"]]
        for key in expired_keys:
            del self.query_cache[key]
        
        # Add new cache entry
        self.query_cache[cache_key] = {
            "result": result.copy(),  # Don't include query_id in cache
            "expires_at": current_time + timedelta(seconds=self.cache_ttl),
            "cached_at": current_time
        }
    
    def optimize_sql_query(self, sql_query: str) -> str:
        """Optimize SQL query for better performance"""
        # Basic optimizations (enhance for production)
        optimized = sql_query
        
        # Add LIMIT if not present for large result sets
        if 'LIMIT' not in optimized.upper() and 'COUNT(' not in optimized.upper():
            optimized = optimized.rstrip(';') + ' LIMIT 100;'
        
        # Add indexes hint for common columns
        if 'WHERE' in optimized.upper():
            # This would contain actual index optimization logic
            pass
        
        return optimized
    
    def set_current_schema(self, schema: Dict[str, Any]):
        """Set the current database schema for query processing"""
        self.current_schema = schema
        
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get query engine performance metrics"""
        return {
            "cache_size": len(self.query_cache),
            "cache_hit_rate": 0.0,  # Calculate actual hit rate
            "average_query_time": 0.0,  # Calculate from historical data
            "total_queries": 0,  # Track total queries processed
            "active_connections": 1  # Current database connections
        }
'''

print("Created query_engine.py content")