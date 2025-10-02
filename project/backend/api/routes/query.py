query_py_content = '''
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
import time
import json

from ..models import QueryRequest, QueryResponse, QueryHistory
from ...services.query_engine import QueryEngine

router = APIRouter()

# Initialize query engine
query_engine = QueryEngine()

# In-memory storage for query history (use database in production)
query_history_storage = []


@router.post("/query")
async def process_query(query_request: QueryRequest) -> QueryResponse:
    """Process natural language query"""
    start_time = time.time()
    
    try:
        # Validate query
        if not query_request.query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        # Process the query
        result = await query_engine.process_query(query_request.query)
        
        # Calculate response time
        response_time = round((time.time() - start_time) * 1000, 2)  # in milliseconds
        
        # Create response
        query_response = QueryResponse(
            query_id=result["query_id"],
            query=query_request.query,
            query_type=result["query_type"],
            sql_query=result.get("sql_query"),
            results=result["results"],
            total_results=result["total_results"],
            response_time=response_time,
            cache_hit=result["cache_hit"],
            sources=result.get("sources", []),
            metadata=result.get("metadata", {})
        )
        
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
        raise HTTPException(
            status_code=500, 
            detail=f"Query processing failed: {str(e)}"
        )


@router.get("/query-history")
async def get_query_history(
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0)
) -> List[QueryHistory]:
    """Get query history with pagination"""
    try:
        # Sort by timestamp (newest first)
        sorted_history = sorted(
            query_history_storage, 
            key=lambda x: x["timestamp"], 
            reverse=True
        )
        
        # Apply pagination
        paginated_history = sorted_history[offset:offset + limit]
        
        return [QueryHistory(**item) for item in paginated_history]
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve query history: {str(e)}"
        )


@router.get("/query-suggestions")
async def get_query_suggestions(
    partial_query: str = Query(..., min_length=1)
) -> Dict[str, List[str]]:
    """Get query suggestions based on partial input"""
    try:
        suggestions = await query_engine.get_suggestions(partial_query)
        return {"suggestions": suggestions}
        
    except Exception as e:
        return {"suggestions": []}


@router.delete("/query-history")
async def clear_query_history():
    """Clear all query history"""
    try:
        query_history_storage.clear()
        return {"message": "Query history cleared successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to clear query history: {str(e)}"
        )


@router.get("/query/{query_id}")
async def get_query_details(query_id: str) -> Dict[str, Any]:
    """Get detailed information about a specific query"""
    try:
        # Find query in history
        query_details = next(
            (q for q in query_history_storage if q["query_id"] == query_id), 
            None
        )
        
        if not query_details:
            raise HTTPException(status_code=404, detail="Query not found")
        
        return query_details
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve query details: {str(e)}"
        )
'''

print("Created query.py content")