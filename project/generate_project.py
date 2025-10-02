import os
import sys
from pathlib import Path

def create_directory_structure():
    """Create the complete directory structure"""
    
    # Base directory (should be run from project root, e.g., C:\Users\saura\Desktop\project)
    base_dir = Path.cwd()
    print(f"Creating project structure in: {base_dir}")
    
    # Create backend directories
    backend_dirs = [
        "backend/api/routes",
        "backend/api/models", 
        "backend/services",
        "backend/models"
    ]
    
    # Create frontend directories
    frontend_dirs = [
        "frontend/src/components",
        "frontend/public"
    ]
    
    # Create all directories
    all_dirs = backend_dirs + frontend_dirs
    for dir_path in all_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"✓ Created directory: {dir_path}")

def write_file(file_path, content):
    """Write content to a file"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Created file: {file_path}")
    except Exception as e:
        print(f"✗ Error creating {file_path}: {e}")

def get_main_py_content():
    return '''
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from api.routes.ingestion import router as ingestion_router
from api.routes.query import router as query_router
from api.routes.schema import router as schema_router

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

# Include routers
app.include_router(ingestion_router, prefix="/api", tags=["ingestion"])
app.include_router(query_router, prefix="/api", tags=["query"])
app.include_router(schema_router, prefix="/api", tags=["schema"])

@app.get("/")
async def root():
    return {"message": "NLP Query Engine API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
'''

def main():
    """Main function to create the entire project structure"""
    print("🚀 NLP Query Engine Project Generator")
    print("=====================================")
    print()
    try:
        print("📁 Creating directory structure...")
        create_directory_structure()
        print()
        # Create backend main.py
        print("📝 Creating backend/main.py...")
        write_file("backend/main.py", get_main_py_content())
        # Empty __init__.py files for Python packages
        for init_file in [
            "backend/__init__.py",
            "backend/api/__init__.py", 
            "backend/api/routes/__init__.py",
            "backend/services/__init__.py"
        ]:
            write_file(init_file, "")
        print()
        print("✅ Directory structure and backend/main.py created!")
        print("⚠️ Now manually add your other files (routes, services, frontend, config) as provided in your assignment.")
        print()
        print("📋 Next Steps:")
        print("1. Copy all the code files I provided for the full system into their correct places.")
        print("2. Install dependencies, then run backend and frontend as per README.")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
