from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uvicorn
import asyncio
import uuid
import time
import json

# Pydantic Models
class DatabaseConnection(BaseModel):
    connection_string: str = Field(..., description="Database connection string")
    test_connection: bool = Field(default=False, description="Whether to test connection")

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language query")
    include_sources: bool = Field(default=True, description="Include source information")
    max_results: int = Field(default=50, le=100, description="Maximum number of results")

class QueryResponse(BaseModel):
    query_id: str
    query: str
    query_type: str = Field(..., description="Type: sql, document, hybrid")
    sql_query: Optional[str] = None
    results: List[Dict[str, Any]]
    total_results: int
    response_time: float = Field(..., description="Response time in milliseconds")
    cache_hit: bool = False
    sources: List[str] = []
    metadata: Dict[str, Any] = {}

class QueryHistory(BaseModel):
    query_id: str
    query: str
    query_type: str
    timestamp: datetime
    response_time: float
    cache_hit: bool

# Global storage (use database in production)
ingestion_jobs = {}
connected_databases = {}
query_history_storage = []
query_cache = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 NLP Query Engine starting up...")
    yield
    # Shutdown
    print("🔽 NLP Query Engine shutting down...")

app = FastAPI(
    title="NLP Query Engine",
    description="AI-powered natural language query system for employee databases",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "NLP Query Engine API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat(), "version": "1.0.0"}

# Database Connection Routes
@app.post("/api/connect-database")
async def connect_database(connection: DatabaseConnection):
    """Connect to database and discover schema"""
    try:
        job_id = str(uuid.uuid4())
        
        # Initialize job
        ingestion_jobs[job_id] = {
            "status": "processing",
            "type": "database",
            "progress": 0,
            "message": "Connecting to database...",
            "started_at": datetime.now(),
            "connection_string": connection.connection_string
        }
        
        # Start schema discovery in background
        asyncio.create_task(discover_schema_background(job_id, connection.connection_string))
        
        return {
            "job_id": job_id,
            "status": "started",
            "message": "Database connection initiated"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to database: {str(e)}")

async def discover_schema_background(job_id: str, connection_string: str):
    """Background task for schema discovery"""
    try:
        # Update progress
        ingestion_jobs[job_id]["progress"] = 25
        ingestion_jobs[job_id]["message"] = "Analyzing database structure..."
        
        await asyncio.sleep(1)
        
        # Mock schema discovery with different variations based on connection string
        if "demo" in connection_string.lower():
            schema = {
                "database_type": "demo",
                "tables": [
                    {
                        "name": "employees",
                        "category": "employee",
                        "columns": [
                            {"name": "emp_id", "type": "INTEGER", "nullable": False, "primary_key": True},
                            {"name": "full_name", "type": "VARCHAR(255)", "nullable": False},
                            {"name": "email", "type": "VARCHAR(255)", "nullable": False},
                            {"name": "dept_id", "type": "INTEGER", "nullable": True},
                            {"name": "position", "type": "VARCHAR(100)", "nullable": True},
                            {"name": "salary", "type": "DECIMAL(10,2)", "nullable": True},
                            {"name": "hire_date", "type": "DATE", "nullable": True},
                            {"name": "manager_id", "type": "INTEGER", "nullable": True},
                        ],
                        "row_count": 245,
                        "relationships": []
                    },
                    {
                        "name": "departments",
                        "category": "department", 
                        "columns": [
                            {"name": "dept_id", "type": "INTEGER", "nullable": False, "primary_key": True},
                            {"name": "dept_name", "type": "VARCHAR(100)", "nullable": False},
                            {"name": "manager_id", "type": "INTEGER", "nullable": True},
                            {"name": "budget", "type": "DECIMAL(15,2)", "nullable": True},
                            {"name": "location", "type": "VARCHAR(100)", "nullable": True}
                        ],
                        "row_count": 12,
                        "relationships": []
                    },
                    {
                        "name": "projects",
                        "category": "project",
                        "columns": [
                            {"name": "project_id", "type": "INTEGER", "nullable": False, "primary_key": True},
                            {"name": "project_name", "type": "VARCHAR(200)", "nullable": False},
                            {"name": "dept_id", "type": "INTEGER", "nullable": True},
                            {"name": "start_date", "type": "DATE", "nullable": True},
                            {"name": "end_date", "type": "DATE", "nullable": True},
                            {"name": "budget", "type": "DECIMAL(12,2)", "nullable": True}
                        ],
                        "row_count": 48,
                        "relationships": []
                    }
                ],
                "relationships": [
                    {
                        "from_table": "employees",
                        "from_column": "dept_id",
                        "to_table": "departments", 
                        "to_column": "dept_id",
                        "relationship_type": "foreign_key"
                    },
                    {
                        "from_table": "projects",
                        "from_column": "dept_id",
                        "to_table": "departments",
                        "to_column": "dept_id", 
                        "relationship_type": "foreign_key"
                    },
                    {
                        "from_table": "employees",
                        "from_column": "manager_id",
                        "to_table": "employees",
                        "to_column": "emp_id",
                        "relationship_type": "self_reference"
                    }
                ],
                "total_tables": 3,
                "total_columns": 21,
                "discovered_at": datetime.now().isoformat()
            }
        else:
            # Handle other connection types
            schema = {
                "database_type": "unknown",
                "tables": [],
                "relationships": [],
                "total_tables": 0,
                "total_columns": 0,
                "discovered_at": datetime.now().isoformat()
            }
        
        ingestion_jobs[job_id]["progress"] = 75
        ingestion_jobs[job_id]["message"] = "Mapping relationships..."
        
        await asyncio.sleep(1)
        
        # Store discovered schema
        connected_databases[job_id] = schema
        
        # Complete job
        ingestion_jobs[job_id]["status"] = "completed"
        ingestion_jobs[job_id]["progress"] = 100
        ingestion_jobs[job_id]["message"] = f"Discovered {len(schema.get('tables', []))} tables"
        ingestion_jobs[job_id]["schema"] = schema
        
    except Exception as e:
        ingestion_jobs[job_id]["status"] = "failed"
        ingestion_jobs[job_id]["message"] = f"Failed: {str(e)}"

# Document Upload Routes
@app.post("/api/upload-documents")
async def upload_documents(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    """Upload and process documents"""
    try:
        job_id = str(uuid.uuid4())
        
        # Initialize job
        ingestion_jobs[job_id] = {
            "status": "processing",
            "type": "documents",
            "progress": 0,
            "message": f"Processing {len(files)} documents...",
            "started_at": datetime.now(),
            "total_files": len(files),
            "processed_files": 0
        }
        
        # Start document processing in background
        background_tasks.add_task(process_documents_background, job_id, files)
        
        return {
            "job_id": job_id,
            "status": "started",
            "message": f"Started processing {len(files)} documents"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload documents: {str(e)}")

async def process_documents_background(job_id: str, files: List[UploadFile]):
    """Background task for document processing"""
    try:
        total_files = len(files)
        
        for i, file in enumerate(files):
            # Update progress
            ingestion_jobs[job_id]["progress"] = int((i / total_files) * 100)
            ingestion_jobs[job_id]["message"] = f"Processing {file.filename}..."
            
            # Simulate processing based on file type
            content = await file.read()
            file_size = len(content)
            
            # Simulate processing time based on file size
            processing_time = min(2.0, file_size / 100000)  # Max 2 seconds
            await asyncio.sleep(processing_time)
            
            ingestion_jobs[job_id]["processed_files"] = i + 1
        
        # Complete job
        ingestion_jobs[job_id]["status"] = "completed"
        ingestion_jobs[job_id]["progress"] = 100
        ingestion_jobs[job_id]["message"] = f"Successfully processed {total_files} documents"
        
    except Exception as e:
        ingestion_jobs[job_id]["status"] = "failed"
        ingestion_jobs[job_id]["message"] = f"Failed: {str(e)}"

@app.get("/api/ingestion-status/{job_id}")
async def get_ingestion_status(job_id: str):
    """Get ingestion job status"""
    if job_id not in ingestion_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return ingestion_jobs[job_id]

# Enhanced Query Routes
@app.post("/api/query")
async def process_query(query_request: QueryRequest) -> QueryResponse:
    """Process natural language query with enhanced capabilities"""
    start_time = time.time()
    
    try:
        # Check cache first
        cache_key = query_request.query.lower().strip()
        if cache_key in query_cache:
            cached_result = query_cache[cache_key]
            cached_result["cache_hit"] = True
            cached_result["response_time"] = round((time.time() - start_time) * 1000, 2)
            return QueryResponse(**cached_result)
        
        # Validate query
        if not query_request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        query_id = str(uuid.uuid4())
        query_lower = query_request.query.lower()
        
        # Enhanced query processing logic
        results = []
        sql_query = None
        query_type = "sql"
        sources = ["database"]
        metadata = {}
        
        # Employee count queries
        if any(phrase in query_lower for phrase in ['how many employees', 'count employees', 'number of employees', 'total employees']):
            results = [{"employee_count": 245}]
            sql_query = "SELECT COUNT(*) as employee_count FROM employees;"
            metadata = {"tables_accessed": ["employees"], "query_pattern": "count"}
            
        # Salary queries
        elif 'average salary' in query_lower or 'avg salary' in query_lower:
            if 'department' in query_lower or 'dept' in query_lower:
                results = [
                    {"dept_name": "Engineering", "avg_salary": 95000.00, "employee_count": 45},
                    {"dept_name": "Sales", "avg_salary": 75000.00, "employee_count": 32},
                    {"dept_name": "HR", "avg_salary": 65000.00, "employee_count": 12},
                    {"dept_name": "Marketing", "avg_salary": 70000.00, "employee_count": 18},
                    {"dept_name": "Finance", "avg_salary": 80000.00, "employee_count": 15}
                ]
                sql_query = "SELECT d.dept_name, AVG(e.salary) as avg_salary, COUNT(e.emp_id) as employee_count FROM employees e JOIN departments d ON e.dept_id = d.dept_id GROUP BY d.dept_name ORDER BY avg_salary DESC;"
                metadata = {"tables_accessed": ["employees", "departments"], "query_pattern": "aggregation"}
            else:
                results = [{"average_salary": 78500.00, "total_employees": 245}]
                sql_query = "SELECT AVG(salary) as average_salary, COUNT(*) as total_employees FROM employees;"
                metadata = {"tables_accessed": ["employees"], "query_pattern": "aggregate_simple"}
                
        # Employee listing queries
        elif any(phrase in query_lower for phrase in ['list employees', 'show employees', 'all employees']):
            if 'engineering' in query_lower:
                results = [
                    {"full_name": "Alice Cooper", "position": "Senior Software Engineer", "salary": 120000.00, "hire_date": "2020-01-15"},
                    {"full_name": "Bob Wilson", "position": "DevOps Engineer", "salary": 105000.00, "hire_date": "2019-03-22"},
                    {"full_name": "Carol Davis", "position": "Frontend Developer", "salary": 95000.00, "hire_date": "2021-06-10"},
                    {"full_name": "David Kim", "position": "Data Engineer", "salary": 110000.00, "hire_date": "2020-09-05"},
                    {"full_name": "Emma Thompson", "position": "Software Architect", "salary": 130000.00, "hire_date": "2018-11-20"}
                ]
                sql_query = "SELECT e.full_name, e.position, e.salary, e.hire_date FROM employees e JOIN departments d ON e.dept_id = d.dept_id WHERE d.dept_name = 'Engineering' ORDER BY e.salary DESC;"
            else:
                results = [
                    {"full_name": "Alice Cooper", "position": "Senior Software Engineer", "dept_name": "Engineering"},
                    {"full_name": "Frank Miller", "position": "Sales Manager", "dept_name": "Sales"},
                    {"full_name": "Grace Lee", "position": "HR Specialist", "dept_name": "HR"},
                    {"full_name": "Henry Ford", "position": "Marketing Director", "dept_name": "Marketing"},
                    {"full_name": "Ivy Chen", "position": "Financial Analyst", "dept_name": "Finance"}
                ]
                sql_query = f"SELECT e.full_name, e.position, d.dept_name FROM employees e JOIN departments d ON e.dept_id = d.dept_id ORDER BY e.full_name LIMIT {query_request.max_results};"
            
            metadata = {"tables_accessed": ["employees", "departments"], "query_pattern": "list"}
            
        # Highest paid queries
        elif 'highest paid' in query_lower or 'top paid' in query_lower:
            results = [
                {"full_name": "Emma Thompson", "position": "Software Architect", "salary": 130000.00, "dept_name": "Engineering"},
                {"full_name": "Michael Johnson", "position": "VP of Sales", "salary": 125000.00, "dept_name": "Sales"},
                {"full_name": "Alice Cooper", "position": "Senior Software Engineer", "salary": 120000.00, "dept_name": "Engineering"},
                {"full_name": "Sarah Williams", "position": "Finance Director", "salary": 115000.00, "dept_name": "Finance"},
                {"full_name": "David Kim", "position": "Data Engineer", "salary": 110000.00, "dept_name": "Engineering"}
            ]
            sql_query = "SELECT e.full_name, e.position, e.salary, d.dept_name FROM employees e JOIN departments d ON e.dept_id = d.dept_id ORDER BY e.salary DESC LIMIT 10;"
            metadata = {"tables_accessed": ["employees", "departments"], "query_pattern": "top_n"}
            
        # Department queries
        elif any(phrase in query_lower for phrase in ['departments', 'list departments', 'show departments']):
            results = [
                {"dept_name": "Engineering", "employee_count": 45, "avg_salary": 95000.00, "budget": 2500000.00},
                {"dept_name": "Sales", "employee_count": 32, "avg_salary": 75000.00, "budget": 1800000.00},
                {"dept_name": "Marketing", "employee_count": 18, "avg_salary": 70000.00, "budget": 1200000.00},
                {"dept_name": "Finance", "employee_count": 15, "avg_salary": 80000.00, "budget": 1000000.00},
                {"dept_name": "HR", "employee_count": 12, "avg_salary": 65000.00, "budget": 800000.00}
            ]
            sql_query = "SELECT d.dept_name, COUNT(e.emp_id) as employee_count, AVG(e.salary) as avg_salary, d.budget FROM departments d LEFT JOIN employees e ON d.dept_id = e.dept_id GROUP BY d.dept_name, d.budget ORDER BY employee_count DESC;"
            metadata = {"tables_accessed": ["departments", "employees"], "query_pattern": "department_summary"}
        
        # Recent hires
        elif any(phrase in query_lower for phrase in ['hired this year', 'new employees', 'recent hires']):
            results = [
                {"full_name": "Jennifer Brown", "position": "Software Developer", "hire_date": "2024-02-15", "dept_name": "Engineering"},
                {"full_name": "Robert Taylor", "position": "Sales Representative", "hire_date": "2024-03-01", "dept_name": "Sales"},
                {"full_name": "Lisa Anderson", "position": "Marketing Coordinator", "hire_date": "2024-01-20", "dept_name": "Marketing"},
                {"full_name": "James Wilson", "position": "Data Analyst", "hire_date": "2024-04-10", "dept_name": "Engineering"}
            ]
            sql_query = "SELECT e.full_name, e.position, e.hire_date, d.dept_name FROM employees e JOIN departments d ON e.dept_id = d.dept_id WHERE YEAR(e.hire_date) = 2024 ORDER BY e.hire_date DESC;"
            metadata = {"tables_accessed": ["employees", "departments"], "query_pattern": "temporal"}
            
        # Python skills query (hybrid - database + documents)
        elif 'python' in query_lower and ('skills' in query_lower or 'developers' in query_lower):
            # Database results
            db_results = [
                {"full_name": "Alice Cooper", "position": "Senior Software Engineer", "dept_name": "Engineering", "source": "database"},
                {"full_name": "David Kim", "position": "Data Engineer", "dept_name": "Engineering", "source": "database"}
            ]
            
            # Document results (simulated)
            doc_results = [
                {
                    "filename": "alice_cooper_resume.pdf",
                    "relevance_score": 0.95,
                    "matching_chunks": [
                        {"chunk_text": "Proficient in Python, Django, and FastAPI with 5+ years experience", "match_score": 0.9}
                    ],
                    "source": "document"
                },
                {
                    "filename": "david_kim_resume.pdf", 
                    "relevance_score": 0.88,
                    "matching_chunks": [
                        {"chunk_text": "Expert Python developer specializing in data processing and ML pipelines", "match_score": 0.85}
                    ],
                    "source": "document"
                }
            ]
            
            results = db_results + doc_results
            query_type = "hybrid"
            sources = ["database", "documents"]
            sql_query = "SELECT e.full_name, e.position, d.dept_name FROM employees e JOIN departments d ON e.dept_id = d.dept_id WHERE e.position LIKE '%Python%' OR e.position LIKE '%Developer%' OR e.position LIKE '%Engineer%';"
            metadata = {"tables_accessed": ["employees", "departments"], "query_pattern": "skills_hybrid", "document_matches": 2}
            
        else:
            # Default help response
            results = [{
                "message": "I can help you query employee data. Try asking:",
                "suggestions": [
                    "How many employees do we have?",
                    "What is the average salary by department?", 
                    "List all employees in Engineering",
                    "Show me the highest paid employees",
                    "Who was hired this year?",
                    "Find employees with Python skills"
                ]
            }]
            query_type = "help"
            sources = []
            metadata = {"query_pattern": "help"}
        
        # Calculate response time
        response_time = round((time.time() - start_time) * 1000, 2)
        
        # Create response
        query_response = QueryResponse(
            query_id=query_id,
            query=query_request.query,
            query_type=query_type,
            sql_query=sql_query,
            results=results,
            total_results=len(results),
            response_time=response_time,
            cache_hit=False,
            sources=sources,
            metadata=metadata
        )
        
        # Cache the result (excluding help queries)
        if query_type != "help":
            query_cache[cache_key] = {
                "query_id": query_id,
                "query": query_request.query,
                "query_type": query_type,
                "sql_query": sql_query,
                "results": results,
                "total_results": len(results),
                "response_time": response_time,
                "cache_hit": False,
                "sources": sources,
                "metadata": metadata
            }
        
        # Store in query history
        query_history_storage.append({
            "query_id": query_response.query_id,
            "query": query_response.query,
            "query_type": query_response.query_type,
            "timestamp": datetime.now(),
            "response_time": response_time,
            "cache_hit": query_response.cache_hit
        })
        
        return query_response
        
    except Exception as e:
        response_time = round((time.time() - start_time) * 1000, 2)
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@app.get("/api/query-history")
async def get_query_history(limit: int = Query(50, le=100), offset: int = Query(0, ge=0)) -> List[QueryHistory]:
    """Get query history with pagination"""
    try:
        # Sort by timestamp (newest first)
        sorted_history = sorted(query_history_storage, key=lambda x: x["timestamp"], reverse=True)
        
        # Apply pagination
        paginated_history = sorted_history[offset:offset + limit]
        
        return [QueryHistory(**item) for item in paginated_history]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve query history: {str(e)}")

@app.get("/api/query-suggestions")
async def get_query_suggestions(partial_query: str = Query(..., min_length=1)) -> Dict[str, List[str]]:
    """Get query suggestions based on partial input"""
    suggestions = [
        "How many employees do we have?",
        "Show me all employees in Engineering", 
        "What is the average salary by department?",
        "List the highest paid employees",
        "Who was hired this year?",
        "Show me all departments",
        "Find employees with Python skills",
        "List employees by hire date",
        "Show me management structure",
        "What projects are active?"
    ]
    
    # Filter based on partial query
    filtered = [s for s in suggestions if partial_query.lower() in s.lower()]
    return {"suggestions": filtered[:5] if filtered else suggestions[:5]}

# Schema Routes
@app.get("/api/schema")
async def get_current_schema():
    """Get the current discovered database schema"""
    if not connected_databases:
        raise HTTPException(status_code=404, detail="No schema discovered yet. Please connect to a database first.")
    
    # Get the most recent schema
    latest_schema_key = max(connected_databases.keys())
    return connected_databases[latest_schema_key]

@app.get("/api/schema/tables")
async def get_tables():
    """Get all discovered tables"""
    if not connected_databases:
        return []
    
    latest_schema_key = max(connected_databases.keys())
    latest_schema = connected_databases[latest_schema_key]
    
    return latest_schema.get("tables", [])

# Metrics and Status
@app.get("/api/metrics")
async def get_metrics():
    """Get system performance metrics"""
    return {
        "total_queries": len(query_history_storage),
        "cache_hit_rate": len([q for q in query_history_storage if q.get("cache_hit", False)]) / max(len(query_history_storage), 1),
        "average_response_time": sum(q.get("response_time", 0) for q in query_history_storage) / max(len(query_history_storage), 1),
        "active_connections": len(connected_databases),
        "ingestion_jobs": len([j for j in ingestion_jobs.values() if j["status"] == "processing"]),
        "uptime_seconds": time.time(),
        "last_query": max(query_history_storage, key=lambda x: x["timestamp"])["timestamp"] if query_history_storage else None
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")