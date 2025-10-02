schema_py_content = '''
from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from datetime import datetime

from ..models import SchemaInfo, TableInfo, ColumnInfo
from ...services.schema_discovery import SchemaDiscovery

router = APIRouter()

# Initialize schema discovery service
schema_discovery = SchemaDiscovery()

# In-memory storage for discovered schemas (use database in production)
discovered_schemas = {}


@router.get("/schema")
async def get_current_schema() -> SchemaInfo:
    """Get the current discovered database schema"""
    try:
        if not discovered_schemas:
            raise HTTPException(
                status_code=404, 
                detail="No schema discovered yet. Please connect to a database first."
            )
        
        # Get the most recent schema
        latest_schema_key = max(discovered_schemas.keys(), key=lambda x: discovered_schemas[x].get("discovered_at", datetime.min))
        latest_schema = discovered_schemas[latest_schema_key]
        
        return SchemaInfo(**latest_schema)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve schema: {str(e)}"
        )


@router.get("/schema/tables")
async def get_tables() -> List[TableInfo]:
    """Get all discovered tables"""
    try:
        if not discovered_schemas:
            return []
        
        # Get the most recent schema
        latest_schema_key = max(discovered_schemas.keys())
        latest_schema = discovered_schemas[latest_schema_key]
        
        tables = []
        for table_data in latest_schema.get("tables", []):
            tables.append(TableInfo(**table_data))
        
        return tables
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve tables: {str(e)}"
        )


@router.get("/schema/tables/{table_name}")
async def get_table_details(table_name: str) -> TableInfo:
    """Get detailed information about a specific table"""
    try:
        if not discovered_schemas:
            raise HTTPException(status_code=404, detail="No schema discovered")
        
        # Get the most recent schema
        latest_schema_key = max(discovered_schemas.keys())
        latest_schema = discovered_schemas[latest_schema_key]
        
        # Find the specific table
        table_data = next(
            (t for t in latest_schema.get("tables", []) if t["name"] == table_name), 
            None
        )
        
        if not table_data:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
        
        return TableInfo(**table_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve table details: {str(e)}"
        )


@router.get("/schema/columns")
async def get_all_columns() -> List[ColumnInfo]:
    """Get all columns from all tables"""
    try:
        if not discovered_schemas:
            return []
        
        # Get the most recent schema
        latest_schema_key = max(discovered_schemas.keys())
        latest_schema = discovered_schemas[latest_schema_key]
        
        all_columns = []
        for table_data in latest_schema.get("tables", []):
            table_name = table_data["name"]
            for column_data in table_data.get("columns", []):
                column_info = ColumnInfo(**column_data)
                column_info.table_name = table_name
                all_columns.append(column_info)
        
        return all_columns
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve columns: {str(e)}"
        )


@router.get("/schema/relationships")
async def get_relationships() -> List[Dict[str, Any]]:
    """Get all discovered table relationships"""
    try:
        if not discovered_schemas:
            return []
        
        # Get the most recent schema
        latest_schema_key = max(discovered_schemas.keys())
        latest_schema = discovered_schemas[latest_schema_key]
        
        return latest_schema.get("relationships", [])
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to retrieve relationships: {str(e)}"
        )


@router.post("/schema/refresh")
async def refresh_schema(connection_string: str):
    """Refresh the database schema discovery"""
    try:
        # Re-discover schema
        new_schema = await schema_discovery.analyze_database(connection_string)
        
        # Store new schema with timestamp
        schema_key = datetime.now().isoformat()
        discovered_schemas[schema_key] = new_schema
        
        return {
            "message": "Schema refreshed successfully",
            "tables_count": len(new_schema.get("tables", [])),
            "relationships_count": len(new_schema.get("relationships", []))
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to refresh schema: {str(e)}"
        )


# Helper function to store discovered schema (called from ingestion routes)
def store_discovered_schema(schema_data: Dict[str, Any], job_id: str):
    """Store a discovered schema"""
    discovered_schemas[job_id] = schema_data
'''

print("Created schema.py content")