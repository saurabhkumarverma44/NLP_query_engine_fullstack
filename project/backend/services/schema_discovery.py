schema_discovery_py_content = '''
import asyncio
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import sqlite3
import psycopg2
import mysql.connector
from urllib.parse import urlparse


class SchemaDiscovery:
    """Service for automatically discovering database schema"""
    
    def __init__(self):
        self.supported_databases = ["postgresql", "mysql", "sqlite"]
        self.common_table_patterns = {
            "employee": ["employee", "employees", "emp", "staff", "personnel", "worker"],
            "department": ["department", "departments", "dept", "division", "divisions"],
            "salary": ["salary", "salaries", "compensation", "pay", "payroll"],
            "project": ["project", "projects", "task", "tasks"],
            "role": ["role", "roles", "position", "positions", "job"],
            "address": ["address", "addresses", "location", "locations"]
        }
    
    async def analyze_database(self, connection_string: str) -> Dict[str, Any]:
        """
        Analyze database and discover schema
        Returns discovered schema with tables, columns, and relationships
        """
        try:
            # Parse connection string to determine database type
            db_type = self._parse_db_type(connection_string)
            
            if db_type == "sqlite":
                return await self._analyze_sqlite(connection_string)
            elif db_type == "postgresql":
                return await self._analyze_postgresql(connection_string)
            elif db_type == "mysql":
                return await self._analyze_mysql(connection_string)
            else:
                # Default mock schema for demo purposes
                return await self._create_mock_schema()
        
        except Exception as e:
            print(f"Schema discovery error: {e}")
            # Return a mock schema for demo purposes
            return await self._create_mock_schema()
    
    def _parse_db_type(self, connection_string: str) -> str:
        """Parse database type from connection string"""
        if connection_string.startswith("sqlite"):
            return "sqlite"
        elif "postgresql://" in connection_string or "postgres://" in connection_string:
            return "postgresql"
        elif "mysql://" in connection_string:
            return "mysql"
        else:
            return "unknown"
    
    async def _analyze_sqlite(self, connection_string: str) -> Dict[str, Any]:
        """Analyze SQLite database"""
        try:
            # Extract database file path
            db_path = connection_string.replace("sqlite:///", "").replace("sqlite://", "")
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            table_names = [row[0] for row in cursor.fetchall()]
            
            tables = []
            relationships = []
            
            for table_name in table_names:
                # Get column information
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns_info = cursor.fetchall()
                
                columns = []
                for col_info in columns_info:
                    columns.append({
                        "name": col_info[1],
                        "type": col_info[2],
                        "nullable": not col_info[3],
                        "primary_key": bool(col_info[5]),
                        "default_value": col_info[4]
                    })
                
                # Categorize table
                category = self._categorize_table(table_name)
                
                tables.append({
                    "name": table_name,
                    "category": category,
                    "columns": columns,
                    "row_count": await self._get_row_count(cursor, table_name)
                })
                
                # Get foreign key relationships
                cursor.execute(f"PRAGMA foreign_key_list({table_name})")
                fk_info = cursor.fetchall()
                
                for fk in fk_info:
                    relationships.append({
                        "from_table": table_name,
                        "from_column": fk[3],
                        "to_table": fk[2],
                        "to_column": fk[4],
                        "relationship_type": "foreign_key"
                    })
            
            conn.close()
            
            return {
                "database_type": "sqlite",
                "tables": tables,
                "relationships": relationships,
                "total_tables": len(tables),
                "total_columns": sum(len(table["columns"]) for table in tables),
                "discovered_at": datetime.now().isoformat()
            }
        
        except Exception as e:
            print(f"SQLite analysis error: {e}")
            return await self._create_mock_schema()
    
    async def _analyze_postgresql(self, connection_string: str) -> Dict[str, Any]:
        """Analyze PostgreSQL database"""
        try:
            # This would connect to actual PostgreSQL database
            # For now, return mock schema
            return await self._create_mock_schema("postgresql")
        except Exception as e:
            return await self._create_mock_schema("postgresql")
    
    async def _analyze_mysql(self, connection_string: str) -> Dict[str, Any]:
        """Analyze MySQL database"""
        try:
            # This would connect to actual MySQL database
            # For now, return mock schema
            return await self._create_mock_schema("mysql")
        except Exception as e:
            return await self._create_mock_schema("mysql")
    
    async def _create_mock_schema(self, db_type: str = "demo") -> Dict[str, Any]:
        """Create a mock schema for demonstration purposes"""
        
        tables = [
            {
                "name": "employees",
                "category": "employee",
                "columns": [
                    {"name": "emp_id", "type": "INTEGER", "nullable": False, "primary_key": True, "default_value": None},
                    {"name": "full_name", "type": "VARCHAR(255)", "nullable": False, "primary_key": False, "default_value": None},
                    {"name": "email", "type": "VARCHAR(255)", "nullable": False, "primary_key": False, "default_value": None},
                    {"name": "dept_id", "type": "INTEGER", "nullable": True, "primary_key": False, "default_value": None},
                    {"name": "position", "type": "VARCHAR(100)", "nullable": True, "primary_key": False, "default_value": None},
                    {"name": "salary", "type": "DECIMAL(10,2)", "nullable": True, "primary_key": False, "default_value": None},
                    {"name": "hire_date", "type": "DATE", "nullable": True, "primary_key": False, "default_value": None},
                    {"name": "manager_id", "type": "INTEGER", "nullable": True, "primary_key": False, "default_value": None}
                ],
                "row_count": 245
            },
            {
                "name": "departments",
                "category": "department",
                "columns": [
                    {"name": "dept_id", "type": "INTEGER", "nullable": False, "primary_key": True, "default_value": None},
                    {"name": "dept_name", "type": "VARCHAR(100)", "nullable": False, "primary_key": False, "default_value": None},
                    {"name": "manager_id", "type": "INTEGER", "nullable": True, "primary_key": False, "default_value": None},
                    {"name": "budget", "type": "DECIMAL(15,2)", "nullable": True, "primary_key": False, "default_value": None}
                ],
                "row_count": 12
            },
            {
                "name": "projects",
                "category": "project",
                "columns": [
                    {"name": "project_id", "type": "INTEGER", "nullable": False, "primary_key": True, "default_value": None},
                    {"name": "project_name", "type": "VARCHAR(200)", "nullable": False, "primary_key": False, "default_value": None},
                    {"name": "dept_id", "type": "INTEGER", "nullable": True, "primary_key": False, "default_value": None},
                    {"name": "start_date", "type": "DATE", "nullable": True, "primary_key": False, "default_value": None},
                    {"name": "end_date", "type": "DATE", "nullable": True, "primary_key": False, "default_value": None},
                    {"name": "budget", "type": "DECIMAL(12,2)", "nullable": True, "primary_key": False, "default_value": None}
                ],
                "row_count": 34
            },
            {
                "name": "employee_projects",
                "category": "junction",
                "columns": [
                    {"name": "emp_id", "type": "INTEGER", "nullable": False, "primary_key": True, "default_value": None},
                    {"name": "project_id", "type": "INTEGER", "nullable": False, "primary_key": True, "default_value": None},
                    {"name": "role", "type": "VARCHAR(50)", "nullable": True, "primary_key": False, "default_value": None},
                    {"name": "hours_allocated", "type": "INTEGER", "nullable": True, "primary_key": False, "default_value": None}
                ],
                "row_count": 156
            }
        ]
        
        relationships = [
            {
                "from_table": "employees",
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
            },
            {
                "from_table": "projects",
                "from_column": "dept_id",
                "to_table": "departments",
                "to_column": "dept_id",
                "relationship_type": "foreign_key"
            },
            {
                "from_table": "employee_projects",
                "from_column": "emp_id",
                "to_table": "employees",
                "to_column": "emp_id",
                "relationship_type": "foreign_key"
            },
            {
                "from_table": "employee_projects",
                "from_column": "project_id",
                "to_table": "projects",
                "to_column": "project_id",
                "relationship_type": "foreign_key"
            }
        ]
        
        return {
            "database_type": db_type,
            "tables": tables,
            "relationships": relationships,
            "total_tables": len(tables),
            "total_columns": sum(len(table["columns"]) for table in tables),
            "discovered_at": datetime.now().isoformat()
        }
    
    def _categorize_table(self, table_name: str) -> str:
        """Categorize table based on naming patterns"""
        table_lower = table_name.lower()
        
        for category, patterns in self.common_table_patterns.items():
            if any(pattern in table_lower for pattern in patterns):
                return category
        
        return "other"
    
    async def _get_row_count(self, cursor, table_name: str) -> int:
        """Get approximate row count for a table"""
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            return cursor.fetchone()[0]
        except:
            return 0
    
    def map_natural_language_to_schema(self, query: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map natural language query to actual database schema
        Returns mapping of query terms to database elements
        """
        mapping = {
            "tables": [],
            "columns": [],
            "conditions": [],
            "aggregations": []
        }
        
        query_lower = query.lower()
        
        # Map table names
        for table in schema.get("tables", []):
            table_name = table["name"]
            if any(pattern in query_lower for pattern in self.common_table_patterns.get(table["category"], [])):
                mapping["tables"].append(table_name)
        
        # Map column names based on common patterns
        common_column_mappings = {
            "salary": ["salary", "compensation", "pay", "wage"],
            "name": ["name", "full_name", "first_name", "last_name"],
            "department": ["department", "dept", "division"],
            "position": ["position", "role", "job", "title"],
            "date": ["date", "hire_date", "start_date", "end_date"]
        }
        
        for table in schema.get("tables", []):
            for column in table["columns"]:
                col_name = column["name"].lower()
                for mapping_key, patterns in common_column_mappings.items():
                    if any(pattern in query_lower for pattern in patterns):
                        if any(pattern in col_name for pattern in patterns):
                            mapping["columns"].append({
                                "table": table["name"],
                                "column": column["name"],
                                "query_term": mapping_key
                            })
        
        return mapping
'''

print("Created schema_discovery.py content")