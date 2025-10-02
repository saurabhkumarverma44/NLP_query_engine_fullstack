# Create the API routes - ingestion.py
ingestion_py_content = '''
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from typing import List, Optional
import asyncio
import uuid
from datetime import datetime

from ..models import DatabaseConnection, IngestionStatus, IngestionResponse
from ...services.schema_discovery import SchemaDiscovery
from ...services.document_processor import DocumentProcessor

router = APIRouter()

# In-memory storage for demo (in production, use Redis or database)
ingestion_jobs = {}
connected_databases = {}
document_processor = DocumentProcessor()
schema_discovery = SchemaDiscovery()


@router.post("/connect-database")
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


@router.post("/upload-documents")
async def upload_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...)
):
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


@router.get("/ingestion-status/{job_id}")
async def get_ingestion_status(job_id: str):
    """Get ingestion job status"""
    if job_id not in ingestion_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = ingestion_jobs[job_id]
    return IngestionStatus(**job)


async def discover_schema_background(job_id: str, connection_string: str):
    """Background task for schema discovery"""
    try:
        # Update progress
        ingestion_jobs[job_id]["progress"] = 25
        ingestion_jobs[job_id]["message"] = "Analyzing database structure..."
        
        # Simulate schema discovery (replace with actual implementation)
        schema = await schema_discovery.analyze_database(connection_string)
        
        ingestion_jobs[job_id]["progress"] = 75
        ingestion_jobs[job_id]["message"] = "Mapping relationships..."
        
        # Simulate some processing time
        await asyncio.sleep(2)
        
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


async def process_documents_background(job_id: str, files: List[UploadFile]):
    """Background task for document processing"""
    try:
        total_files = len(files)
        processed = 0
        
        for i, file in enumerate(files):
            # Update progress
            ingestion_jobs[job_id]["progress"] = int((i / total_files) * 100)
            ingestion_jobs[job_id]["message"] = f"Processing {file.filename}..."
            
            # Read file content
            content = await file.read()
            
            # Process document
            await document_processor.process_document(file.filename, content)
            
            processed += 1
            ingestion_jobs[job_id]["processed_files"] = processed
            
            # Simulate processing time
            await asyncio.sleep(0.5)
        
        # Complete job
        ingestion_jobs[job_id]["status"] = "completed"
        ingestion_jobs[job_id]["progress"] = 100
        ingestion_jobs[job_id]["message"] = f"Successfully processed {processed} documents"
        
    except Exception as e:
        ingestion_jobs[job_id]["status"] = "failed"
        ingestion_jobs[job_id]["message"] = f"Failed: {str(e)}"
'''

print("Created ingestion.py content")