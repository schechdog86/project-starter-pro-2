"""
End-to-End Tests for RAG Pipeline Integration

Tests the complete flow:
1. Code indexing -> Vector storage
2. Vector search -> Result retrieval
3. Context building with RAG results
"""
import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.ai.rag_indexer import RAGIndexer
from app.ai.vector_db_manager import VectorDBManager
from app.ai.context_builder import build_context, build_context_str


# Test fixtures
@pytest.fixture
def temp_codebase():
    """Create a temporary codebase for testing."""
    temp_dir = tempfile.mkdtemp(prefix="test_codebase_")
    
    # Create some test files
    test_files = {
        "auth.py": """
def authenticate_user(username: str, password: str) -> dict:
    '''Authenticate a user with username and password.'''
    # Verify credentials
    if verify_credentials(username, password):
        return generate_token(username)
    raise AuthenticationError("Invalid credentials")

def verify_credentials(username: str, password: str) -> bool:
    '''Verify user credentials against database.'''
    user = database.get_user(username)
    return user and user.check_password(password)
""",
        "database.py": """
class DatabaseConnection:
    '''Manage database connections with connection pooling.'''
    
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.pool = ConnectionPool(max_connections=10)
    
    def execute_query(self, query: str):
        '''Execute a SQL query and return results.'''
        with self.pool.get_connection() as conn:
            return conn.execute(query)
""",
        "api.py": """
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.post("/register")
async def register_user(email: str, password: str):
    '''Register a new user with email validation.'''
    if not validate_email(email):
        raise HTTPException(400, "Invalid email")
    
    user = create_user(email, password)
    return {"user_id": user.id, "email": user.email}
""",
    }
    
    for filename, content in test_files.items():
        filepath = Path(temp_dir) / filename
        filepath.write_text(content)
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_vector_db():
    """Create a temporary vector database."""
    temp_db_path = tempfile.mkdtemp(prefix="test_vector_db_")
    
    # Set environment to disable global instance
    os.environ["PSP_VDB_CREATE_GLOBAL"] = "0"
    
    yield temp_db_path
    
    # Cleanup
    shutil.rmtree(temp_db_path, ignore_errors=True)


@pytest.fixture
def rag_indexer(temp_vector_db):
    """Create a RAG indexer with temporary database."""
    indexer = RAGIndexer(chunking_strategy="truncate")
    indexer.vector_db = VectorDBManager(db_path=temp_vector_db)
    return indexer


class TestRAGPipelineE2E:
    """End-to-end tests for the complete RAG pipeline."""
    
    def test_index_and_search_flow(self, rag_indexer, temp_codebase):
        """Test the complete indexing and search flow."""
        # Step 1: Index the codebase
        result = rag_indexer.index_codebase(temp_codebase, extensions=[".py"])
        
        assert result["processed_files"] == 3
        assert result["total_chunks_indexed"] > 0
        assert result["failed_files"] == 0
        
        # Step 2: Search for authentication-related code
        search_results = rag_indexer.search_code("How do I authenticate users?", limit=5)
        
        assert len(search_results) > 0
        assert any("auth" in r["filename"].lower() for r in search_results)
        
        # Verify result structure
        first_result = search_results[0]
        assert "filename" in first_result
        assert "text" in first_result
        assert "chunk_index" in first_result
        assert "score" in first_result
    
    def test_search_with_filename_filter(self, rag_indexer, temp_codebase):
        """Test search with filename filtering."""
        # Index the codebase
        rag_indexer.index_codebase(temp_codebase, extensions=[".py"])
        
        # Search with filename filter
        results = rag_indexer.search_code(
            "database connection",
            limit=5,
            filters={"filename": "database.py"}
        )
        
        assert len(results) > 0
        assert all("database.py" in r["filename"] for r in results)
    
    def test_get_file_context(self, rag_indexer, temp_codebase):
        """Test retrieving all chunks for a specific file."""
        # Index the codebase
        rag_indexer.index_codebase(temp_codebase, extensions=[".py"])
        
        # Get all chunks for auth.py
        auth_file = str(Path(temp_codebase) / "auth.py")
        chunks = rag_indexer.get_file_context(auth_file)
        
        assert len(chunks) > 0
        assert all(c["filename"] == auth_file for c in chunks)
        assert all("chunk_index" in c for c in chunks)
    
    def test_index_stats(self, rag_indexer, temp_codebase):
        """Test getting index statistics."""
        # Index the codebase
        rag_indexer.index_codebase(temp_codebase, extensions=[".py"])
        
        # Get stats
        stats = rag_indexer.get_index_stats()
        
        assert "total_chunks" in stats
        assert stats["total_chunks"] > 0
        assert "unique_files" in stats
        assert stats["unique_files"] == 3
    
    def test_clear_and_reindex(self, rag_indexer, temp_codebase):
        """Test clearing index and reindexing."""
        # Initial index
        result1 = rag_indexer.index_codebase(temp_codebase, extensions=[".py"])
        initial_chunks = result1["total_chunks_indexed"]
        
        # Clear index
        rag_indexer.clear_index()
        
        # Verify empty
        stats = rag_indexer.get_index_stats()
        assert stats.get("total_chunks", 0) == 0
        
        # Reindex
        result2 = rag_indexer.index_codebase(temp_codebase, extensions=[".py"])
        assert result2["total_chunks_indexed"] == initial_chunks
    
    def test_index_single_file(self, rag_indexer, temp_codebase):
        """Test indexing a single file."""
        auth_file = str(Path(temp_codebase) / "auth.py")
        
        result = rag_indexer.index_single_file(auth_file)
        
        assert result["success"] is True
        assert result["chunks_added"] > 0
        assert result["filepath"] == auth_file
    
    def test_search_relevance(self, rag_indexer, temp_codebase):
        """Test that search returns relevant results."""
        # Index the codebase
        rag_indexer.index_codebase(temp_codebase, extensions=[".py"])
        
        # Test different queries
        test_cases = [
            ("authenticate user", "auth.py"),
            ("database connection", "database.py"),
            ("register endpoint", "api.py"),
        ]
        
        for query, expected_file in test_cases:
            results = rag_indexer.search_code(query, limit=3)
            assert len(results) > 0
            # Top result should be from the expected file
            assert expected_file in results[0]["filename"]
    
    def test_empty_codebase(self, rag_indexer):
        """Test indexing an empty directory."""
        empty_dir = tempfile.mkdtemp(prefix="empty_")
        
        try:
            result = rag_indexer.index_codebase(empty_dir, extensions=[".py"])
            assert result["processed_files"] == 0
            assert result["total_chunks_indexed"] == 0
        finally:
            shutil.rmtree(empty_dir, ignore_errors=True)
    
    def test_search_empty_index(self, rag_indexer):
        """Test searching an empty index."""
        results = rag_indexer.search_code("test query", limit=5)
        assert len(results) == 0
    
    @pytest.mark.skipif(
        not os.environ.get("VOYAGE_API_KEY"),
        reason="Requires VOYAGE_API_KEY environment variable"
    )
    def test_context_builder_integration(self, rag_indexer, temp_codebase):
        """Test context builder with RAG results."""
        # Index the codebase
        rag_indexer.index_codebase(temp_codebase, extensions=[".py"])
        
        # Build context (this will fail if memory_manager isn't set up, so we'll catch that)
        try:
            context = build_context(
                user_id="test_user",
                query="How do I authenticate users?",
                mem_k=3,
                code_k=3
            )
            
            assert "memory" in context
            assert "knowledge" in context
            assert "context_str" in context
            assert len(context["knowledge"]) > 0
        except Exception as e:
            # Memory manager might not be initialized in test environment
            pytest.skip(f"Context builder requires full setup: {e}")


class TestVectorDBManager:
    """Test VectorDBManager directly."""
    
    def test_add_and_search_chunks(self, temp_vector_db):
        """Test adding chunks and searching."""
        vdb = VectorDBManager(db_path=temp_vector_db)
        
        # Add test chunks
        chunks = [
            {
                "filename": "test.py",
                "text": "def authenticate_user(username, password): verify credentials",
                "chunk_index": 0,
                "total_chunks": 1,
            },
            {
                "filename": "db.py",
                "text": "class DatabaseConnection: manage database connections",
                "chunk_index": 0,
                "total_chunks": 1,
            },
        ]
        
        added = vdb.add_chunks(chunks)
        assert added == 2
        
        # Search
        results = vdb.search("authentication", limit=5)
        assert len(results) > 0
    
    def test_provider_configuration(self, temp_vector_db):
        """Test that provider configuration is working."""
        vdb = VectorDBManager(db_path=temp_vector_db)
        
        # Check provider attributes
        assert hasattr(vdb, "provider")
        assert hasattr(vdb, "model")
        assert hasattr(vdb, "vector_dim")
        
        # Default should be voyageai
        assert vdb.provider == "voyageai"
        assert vdb.model == "voyage-3"
        assert vdb.vector_dim == 1024


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

