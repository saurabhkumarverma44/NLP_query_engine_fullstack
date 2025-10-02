models_py_content = '''
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


# Database Connection Models
class DatabaseConnection(BaseModel):
    connection_string: str = Field(..., description="Database connection string")
    test_connection: bool = Field(default=False, description="Whether to test connection")


# Schema Models
class ColumnInfo(BaseModel):
    name: str
    type: str
    nullable: bool = True
    primary_key: bool = False
    default_value: Optional[Union[str, int, float]] = None
    table_name: Optional[str] = None  # Added for convenience


class TableInfo(BaseModel):
    name: str
    category: str = "other"
    columns: List[ColumnInfo]
    row_count: int = 0
    relationships: List[Dict[str, Any]] = []


class SchemaInfo(BaseModel):
    database_type: str
    tables: List[TableInfo]
    relationships: List[Dict[str, Any]]
    total_tables: int
    total_columns: int
    discovered_at: str


# Ingestion Models
class IngestionStatus(BaseModel):
    status: str = Field(..., description="Status: processing, completed, failed")
    type: str = Field(..., description="Type: database, documents")
    progress: int = Field(default=0, description="Progress percentage (0-100)")
    message: str = Field(default="", description="Status message")
    started_at: datetime
    completed_at: Optional[datetime] = None
    total_files: Optional[int] = None
    processed_files: Optional[int] = None
    schema: Optional[Dict[str, Any]] = None


class IngestionResponse(BaseModel):
    job_id: str
    status: str
    message: str


# Query Models
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


# Document Models
class DocumentUpload(BaseModel):
    filename: str
    content_type: str
    size: int


class DocumentInfo(BaseModel):
    document_id: str
    filename: str
    file_type: str
    upload_date: datetime
    size: int
    chunk_count: int
    status: str = "processed"


# API Response Models
class HealthCheckResponse(BaseModel):
    status: str = "healthy"
    timestamp: str
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: str


class SuccessResponse(BaseModel):
    message: str
    data: Optional[Dict[str, Any]] = None


# Metrics Models
class PerformanceMetrics(BaseModel):
    total_queries: int
    average_response_time: float
    cache_hit_rate: float
    active_connections: int
    uptime_seconds: float


class SystemStatus(BaseModel):
    database_connected: bool
    documents_indexed: int
    schema_discovered: bool
    last_activity: Optional[datetime] = None


# Configuration Models
class CacheConfig(BaseModel):
    ttl_seconds: int = 300
    max_size: int = 1000


class DatabaseConfig(BaseModel):
    pool_size: int = 10
    connection_timeout: int = 30


class EmbeddingConfig(BaseModel):
    model: str = "sentence-transformers/all-MiniLM-L6-v2"
    batch_size: int = 32


class AppConfig(BaseModel):
    cache: CacheConfig = CacheConfig()
    database: DatabaseConfig = DatabaseConfig()
    embeddings: EmbeddingConfig = EmbeddingConfig()


# Enum Classes
class QueryTypeEnum(str, Enum):
    SQL = "sql"
    DOCUMENT = "document"
    HYBRID = "hybrid"
    UNKNOWN = "unknown"


class IngestionStatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DocumentStatusEnum(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


# Utility Models for API responses
class PaginationMeta(BaseModel):
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool


class PaginatedResponse(BaseModel):
    data: List[Dict[str, Any]]
    meta: PaginationMeta
'''

print("Created models.py content")