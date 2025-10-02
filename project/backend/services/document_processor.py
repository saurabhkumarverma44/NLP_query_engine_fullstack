document_processor_py_content = '''
import asyncio
import uuid
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import re
import os
import tempfile
from pathlib import Path

# For document processing
try:
    import PyPDF2
    from docx import Document as DocxDocument
    import pandas as pd
except ImportError:
    PyPDF2 = None
    DocxDocument = None
    pd = None

# For embeddings
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
except ImportError:
    SentenceTransformer = None
    np = None


class DocumentProcessor:
    """Service for processing and indexing documents"""
    
    def __init__(self):
        # Initialize embedding model (if available)
        self.embedding_model = None
        if SentenceTransformer:
            try:
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            except:
                print("Warning: Could not load embedding model")
        
        # Document storage (use vector database in production)
        self.document_store = []
        self.document_embeddings = []
        
        # Supported file types
        self.supported_types = {'.pdf', '.docx', '.txt', '.csv', '.json'}
    
    async def process_document(self, filename: str, content: bytes) -> Dict[str, Any]:
        """
        Process a single document and extract information
        """
        try:
            # Determine file type
            file_extension = Path(filename).suffix.lower()
            
            if file_extension not in self.supported_types:
                raise ValueError(f"Unsupported file type: {file_extension}")
            
            # Extract text content
            if file_extension == '.pdf':
                text_content = await self._extract_pdf_text(content)
            elif file_extension == '.docx':
                text_content = await self._extract_docx_text(content)
            elif file_extension == '.txt':
                text_content = content.decode('utf-8')
            elif file_extension == '.csv':
                text_content = await self._extract_csv_text(content)
            elif file_extension == '.json':
                text_content = await self._extract_json_text(content)
            else:
                text_content = content.decode('utf-8', errors='ignore')
            
            # Chunk the content
            chunks = await self._chunk_content(text_content, file_extension)
            
            # Generate embeddings if model is available
            embeddings = []
            if self.embedding_model and chunks:
                embeddings = await self._generate_embeddings(chunks)
            
            # Store document
            doc_id = str(uuid.uuid4())
            document_data = {
                "id": doc_id,
                "filename": filename,
                "file_type": file_extension,
                "content": text_content,
                "chunks": chunks,
                "chunk_count": len(chunks),
                "processed_at": datetime.now().isoformat(),
                "metadata": await self._extract_metadata(text_content, filename)
            }
            
            # Store in document store
            self.document_store.append(document_data)
            if embeddings:
                self.document_embeddings.extend(embeddings)
            
            return {
                "document_id": doc_id,
                "filename": filename,
                "chunks_created": len(chunks),
                "status": "success"
            }
            
        except Exception as e:
            return {
                "filename": filename,
                "error": str(e),
                "status": "failed"
            }
    
    async def _extract_pdf_text(self, content: bytes) -> str:
        """Extract text from PDF content"""
        if not PyPDF2:
            raise ImportError("PyPDF2 not installed. Install with: pip install PyPDF2")
        
        try:
            # Write content to temporary file
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
                temp_file.write(content)
                temp_path = temp_file.name
            
            # Extract text
            text_content = ""
            with open(temp_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\\n"
            
            # Clean up
            os.unlink(temp_path)
            
            return text_content.strip()
            
        except Exception as e:
            # Fallback: return raw text (might be garbled but better than nothing)
            return content.decode('utf-8', errors='ignore')
    
    async def _extract_docx_text(self, content: bytes) -> str:
        """Extract text from DOCX content"""
        if not DocxDocument:
            raise ImportError("python-docx not installed. Install with: pip install python-docx")
        
        try:
            # Write content to temporary file
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_file:
                temp_file.write(content)
                temp_path = temp_file.name
            
            # Extract text
            doc = DocxDocument(temp_path)
            text_content = ""
            for paragraph in doc.paragraphs:
                text_content += paragraph.text + "\\n"
            
            # Clean up
            os.unlink(temp_path)
            
            return text_content.strip()
            
        except Exception as e:
            # Fallback: return raw text
            return content.decode('utf-8', errors='ignore')
    
    async def _extract_csv_text(self, content: bytes) -> str:
        """Extract and format CSV content as text"""
        try:
            # Decode content
            csv_text = content.decode('utf-8')
            
            # If pandas is available, use it for better formatting
            if pd:
                import io
                df = pd.read_csv(io.StringIO(csv_text))
                return f"CSV Data Summary:\\nColumns: {', '.join(df.columns)}\\nRows: {len(df)}\\n\\nContent:\\n{df.to_string()}"
            else:
                return f"CSV Content:\\n{csv_text}"
                
        except Exception as e:
            return content.decode('utf-8', errors='ignore')
    
    async def _extract_json_text(self, content: bytes) -> str:
        """Extract and format JSON content as text"""
        try:
            import json
            json_data = json.loads(content.decode('utf-8'))
            return f"JSON Content:\\n{json.dumps(json_data, indent=2)}"
        except Exception as e:
            return content.decode('utf-8', errors='ignore')
    
    async def _chunk_content(self, text: str, file_type: str) -> List[str]:
        """
        Intelligently chunk content based on document structure
        """
        if not text.strip():
            return []
        
        # Base chunk size (can be optimized based on document type)
        base_chunk_size = 1000
        overlap_size = 200
        
        if file_type == '.pdf':
            # For PDFs, try to preserve paragraph boundaries
            chunks = await self._chunk_by_paragraphs(text, base_chunk_size, overlap_size)
        elif file_type == '.docx':
            # For Word docs, chunk by paragraphs
            chunks = await self._chunk_by_paragraphs(text, base_chunk_size, overlap_size)
        elif file_type == '.csv':
            # For CSVs, chunk by rows while preserving header
            chunks = await self._chunk_csv_data(text, base_chunk_size)
        else:
            # Default chunking for other file types
            chunks = await self._chunk_by_sentences(text, base_chunk_size, overlap_size)
        
        return [chunk.strip() for chunk in chunks if chunk.strip()]
    
    async def _chunk_by_paragraphs(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Chunk text by paragraphs while respecting size limits"""
        paragraphs = text.split('\\n\\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) <= chunk_size:
                current_chunk += paragraph + "\\n\\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # If paragraph is too long, split it further
                if len(paragraph) > chunk_size:
                    sub_chunks = await self._chunk_by_sentences(paragraph, chunk_size, overlap)
                    chunks.extend(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = paragraph + "\\n\\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def _chunk_by_sentences(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Chunk text by sentences"""
        sentences = re.split(r'(?<=[.!?])\\s+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= chunk_size:
                current_chunk += sentence + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + " "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def _chunk_csv_data(self, text: str, chunk_size: int) -> List[str]:
        """Chunk CSV data while preserving structure"""
        lines = text.split('\\n')
        if not lines:
            return []
        
        header = lines[0] if lines else ""
        data_lines = lines[1:] if len(lines) > 1 else []
        
        chunks = []
        current_chunk_lines = [header]
        current_size = len(header)
        
        for line in data_lines:
            if current_size + len(line) <= chunk_size:
                current_chunk_lines.append(line)
                current_size += len(line)
            else:
                if len(current_chunk_lines) > 1:  # More than just header
                    chunks.append('\\n'.join(current_chunk_lines))
                current_chunk_lines = [header, line]
                current_size = len(header) + len(line)
        
        if len(current_chunk_lines) > 1:
            chunks.append('\\n'.join(current_chunk_lines))
        
        return chunks
    
    async def _generate_embeddings(self, chunks: List[str]) -> List[Dict[str, Any]]:
        """Generate embeddings for text chunks"""
        if not self.embedding_model or not chunks:
            return []
        
        try:
            # Generate embeddings in batches
            batch_size = 32
            embeddings = []
            
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                batch_embeddings = self.embedding_model.encode(batch)
                
                for j, embedding in enumerate(batch_embeddings):
                    embeddings.append({
                        "chunk_index": i + j,
                        "chunk_text": batch[j],
                        "embedding": embedding.tolist() if hasattr(embedding, 'tolist') else embedding
                    })
            
            return embeddings
            
        except Exception as e:
            print(f"Embedding generation error: {e}")
            return []
    
    async def _extract_metadata(self, content: str, filename: str) -> Dict[str, Any]:
        """Extract metadata from document content"""
        metadata = {
            "word_count": len(content.split()),
            "character_count": len(content),
            "filename": filename,
            "extracted_at": datetime.now().isoformat()
        }
        
        # Try to extract common metadata patterns
        email_pattern = r'\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\\b'
        phone_pattern = r'\\b\\d{3}[-.]?\\d{3}[-.]?\\d{4}\\b'
        date_pattern = r'\\b\\d{1,2}[/-]\\d{1,2}[/-]\\d{2,4}\\b'
        
        metadata["emails_found"] = len(re.findall(email_pattern, content))
        metadata["phones_found"] = len(re.findall(phone_pattern, content))
        metadata["dates_found"] = len(re.findall(date_pattern, content))
        
        return metadata
    
    async def search_documents(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search documents using text matching or semantic search
        """
        if not self.document_store:
            return []
        
        # Simple text search (can be enhanced with semantic search)
        results = []
        query_lower = query.lower()
        
        for doc in self.document_store:
            # Check if query matches filename or content
            score = 0
            
            if query_lower in doc["filename"].lower():
                score += 10
            
            if query_lower in doc["content"].lower():
                score += 5
            
            # Check chunks for matches
            matching_chunks = []
            for i, chunk in enumerate(doc["chunks"]):
                if query_lower in chunk.lower():
                    matching_chunks.append({
                        "chunk_index": i,
                        "chunk_text": chunk,
                        "match_score": chunk.lower().count(query_lower)
                    })
                    score += chunk.lower().count(query_lower)
            
            if score > 0:
                results.append({
                    "document_id": doc["id"],
                    "filename": doc["filename"],
                    "file_type": doc["file_type"],
                    "relevance_score": score,
                    "matching_chunks": matching_chunks[:3],  # Top 3 matching chunks
                    "metadata": doc["metadata"]
                })
        
        # Sort by relevance score
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return results[:limit]
    
    def get_document_stats(self) -> Dict[str, Any]:
        """Get statistics about processed documents"""
        if not self.document_store:
            return {"total_documents": 0}
        
        file_types = {}
        total_chunks = 0
        total_words = 0
        
        for doc in self.document_store:
            file_type = doc["file_type"]
            file_types[file_type] = file_types.get(file_type, 0) + 1
            total_chunks += doc["chunk_count"]
            total_words += doc["metadata"].get("word_count", 0)
        
        return {
            "total_documents": len(self.document_store),
            "file_types": file_types,
            "total_chunks": total_chunks,
            "total_words": total_words,
            "embedding_model": "all-MiniLM-L6-v2" if self.embedding_model else "none"
        }
'''

print("Created document_processor.py content")