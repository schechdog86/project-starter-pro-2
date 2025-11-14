"""
Vector Database Manager for Code Search RAG

Supports multiple embedding providers via environment variables:
- PSP_EMBED_PROVIDER: Provider name (default: "voyageai")
- PSP_EMBED_MODEL: Model name (default: "voyage-3")
- Provider-specific API keys (VOYAGE_API_KEY, OPENAI_API_KEY, etc.)
"""
import os
import lancedb
from lancedb.pydantic import LanceModel, Vector
from lancedb.embeddings import get_registry
from typing import List, Dict, Any, Optional, Type
import logging

logger = logging.getLogger(__name__)


# Provider configuration: maps provider name to default model and dimensions
PROVIDER_CONFIG = {
    "voyageai": {
        "models": {
            "voyage-3": {"dims": 1024, "api_key_env": "VOYAGE_API_KEY"},
            "voyage-3-lite": {"dims": 512, "api_key_env": "VOYAGE_API_KEY"},
            "voyage-code-2": {"dims": 1536, "api_key_env": "VOYAGE_API_KEY"},
            "voyage-finance-2": {"dims": 1024, "api_key_env": "VOYAGE_API_KEY"},
            "voyage-law-2": {"dims": 1024, "api_key_env": "VOYAGE_API_KEY"},
        },
        "default_model": "voyage-3",
    },
    "openai": {
        "models": {
            "text-embedding-3-small": {"dims": 1536, "api_key_env": "OPENAI_API_KEY"},
            "text-embedding-3-large": {"dims": 3072, "api_key_env": "OPENAI_API_KEY"},
            "text-embedding-ada-002": {"dims": 1536, "api_key_env": "OPENAI_API_KEY"},
        },
        "default_model": "text-embedding-3-small",
    },
    "ollama": {
        "models": {
            "nomic-embed-text": {"dims": 768, "api_key_env": None},
            "mxbai-embed-large": {"dims": 1024, "api_key_env": None},
            "bge-m3": {"dims": 1024, "api_key_env": None},
            "all-minilm": {"dims": 384, "api_key_env": None},
        },
        "default_model": "nomic-embed-text",
    },
    "sentence-transformers": {
        "models": {
            "all-MiniLM-L6-v2": {"dims": 384, "api_key_env": None},
            "all-mpnet-base-v2": {"dims": 768, "api_key_env": None},
        },
        "default_model": "all-MiniLM-L6-v2",
    },
}


def create_code_chunks_schema(vector_dim: int) -> Type[LanceModel]:
    """
    Dynamically create a CodeChunks schema with the specified vector dimension.

    Args:
        vector_dim: Dimension of the embedding vectors

    Returns:
        LanceModel class with the correct vector dimension
    """
    class CodeChunks(LanceModel):
        """Schema for code chunks in LanceDB."""
        filename: str
        text: str
        chunk_index: int
        total_chunks: int
        vector: Vector(vector_dim)

        # Optional metadata
        node_type: Optional[str] = None
        node_name: Optional[str] = None
        truncated: bool = False

    return CodeChunks


class VectorDBManager:
    """Manages vector database operations for code search."""

    def __init__(self, db_path: str = None):
        # Use provided path or default
        self.db_path = db_path or "/data/vector_db"
        self.db = None
        self.table = None
        self.embedding_func = None
        self.vector_dim = None
        self.provider = None
        self.model = None
        self.schema_class = None

        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

        self._initialize_embedding_function()
        self._connect_to_db()

    def _initialize_embedding_function(self):
        """Initialize the embedding function based on environment configuration."""
        try:
            # Get provider and model from environment
            self.provider = os.environ.get("PSP_EMBED_PROVIDER", "voyageai")

            # Validate provider
            if self.provider not in PROVIDER_CONFIG:
                available = ", ".join(PROVIDER_CONFIG.keys())
                raise ValueError(
                    f"Unsupported embedding provider: {self.provider}. "
                    f"Available providers: {available}"
                )

            provider_config = PROVIDER_CONFIG[self.provider]
            self.model = os.environ.get("PSP_EMBED_MODEL", provider_config["default_model"])

            # Validate model
            if self.model not in provider_config["models"]:
                available = ", ".join(provider_config["models"].keys())
                raise ValueError(
                    f"Unsupported model '{self.model}' for provider '{self.provider}'. "
                    f"Available models: {available}"
                )

            model_config = provider_config["models"][self.model]
            self.vector_dim = model_config["dims"]

            # Check API key if required
            api_key_env = model_config.get("api_key_env")
            if api_key_env:
                api_key = os.environ.get(api_key_env)
                if not api_key:
                    raise ValueError(
                        f"API key not found. Set {api_key_env} environment variable."
                    )
                # Ensure the environment variable is set for the provider
                os.environ[api_key_env] = api_key

            # Initialize the embedding function via LanceDB registry
            registry = get_registry()

            if self.provider == "voyageai":
                self.embedding_func = registry.get("voyageai").create(
                    name=self.model,
                    api_key=os.environ.get(api_key_env),
                )
            elif self.provider == "openai":
                self.embedding_func = registry.get("openai").create(
                    name=self.model,
                    api_key=os.environ.get(api_key_env),
                )
            elif self.provider == "ollama":
                # Ollama may need base_url configuration
                base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
                self.embedding_func = registry.get("ollama").create(
                    name=self.model,
                    base_url=base_url,
                )
            elif self.provider == "sentence-transformers":
                self.embedding_func = registry.get("sentence-transformers").create(
                    name=self.model,
                )
            else:
                raise ValueError(f"Provider initialization not implemented: {self.provider}")

            # Create schema with correct vector dimension
            self.schema_class = create_code_chunks_schema(self.vector_dim)

            logger.info(
                f"Initialized {self.provider} embedding function: {self.model} "
                f"(dimension: {self.vector_dim})"
            )

        except Exception as e:
            logger.error(f"Failed to initialize embedding function: {e}")
            raise

    def _connect_to_db(self):
        """Connect to LanceDB and create/load the table."""
        try:
            self.db = lancedb.connect(self.db_path)

            # Check if table exists
            table_names = self.db.table_names()
            if "code_chunks" in table_names:
                self.table = self.db.open_table("code_chunks")
                logger.info("Loaded existing code_chunks table")
            else:
                # Create new table with the dynamic schema
                self.table = self.db.create_table(
                    "code_chunks",
                    schema=self.schema_class,
                    mode="overwrite"
                )
                logger.info("Created new code_chunks table")

        except Exception as e:
            logger.error(f"Failed to connect to vector database: {e}")
            raise

    def add_chunks(self, chunks: List[Dict[str, Any]]) -> int:
        """
        Add code chunks to the vector database.

        Args:
            chunks: List of chunk dictionaries

        Returns:
            Number of chunks added
        """
        if not chunks:
            return 0

        try:
            # Prepare data and compute embeddings
            texts = [c["text"] for c in chunks]
            vectors = []
            for t in texts:
                out = self.embedding_func.compute_source_embeddings(t)
                vectors.append(out[0] if isinstance(out, list) and len(out) > 0 else out)

            data_to_insert = []
            for chunk, vec in zip(chunks, vectors):
                data_to_insert.append({
                    "filename": chunk["filename"],
                    "text": chunk["text"],
                    "chunk_index": chunk["chunk_index"],
                    "total_chunks": chunk["total_chunks"],
                    "node_type": chunk.get("node_type"),
                    "node_name": chunk.get("node_name"),
                    "truncated": chunk.get("truncated", False),
                    "vector": vec,
                })

            # Insert rows (vectors are provided explicitly)
            self.table.add(data_to_insert)
            logger.info(f"Added {len(chunks)} chunks to vector database")
            return len(chunks)

        except Exception as e:
            logger.error(f"Failed to add chunks to vector database: {e}")
            raise

    def search(self, query: str, limit: int = 10, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for code chunks similar to the query.

        Args:
            query: Search query
            limit: Maximum number of results
            filters: Optional filters (e.g., {"filename": "*.py"})

        Returns:
            List of matching chunks with scores
        """
        try:
            # Embed query text -> vector, then perform vector search
            query_vector_out = self.embedding_func.compute_query_embeddings(query)
            query_vector = query_vector_out[0] if isinstance(query_vector_out, list) and len(query_vector_out) > 0 else query_vector_out
            search_query = self.table.search(query_vector)

            # Apply filters if provided
            if filters:
                for key, value in filters.items():
                    if key == "filename" and isinstance(value, str):
                        search_query = search_query.where(f"filename LIKE '%{value}%'")
                    elif key == "node_type" and value:
                        search_query = search_query.where(f"node_type = '{value}'")

            # Execute search
            results = search_query.limit(limit).to_list()

            # Format results
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "filename": result["filename"],
                    "text": result["text"],
                    "chunk_index": result["chunk_index"],
                    "total_chunks": result["total_chunks"],
                    "node_type": result.get("node_type"),
                    "node_name": result.get("node_name"),
                    "score": result.get("_distance", 0.0),
                    "truncated": result.get("truncated", False)
                })

            return formatted_results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def get_file_chunks(self, filename: str) -> List[Dict[str, Any]]:
        """
        Get all chunks for a specific file.

        Args:
            filename: File to retrieve chunks for

        Returns:
            List of chunks from the file
        """
        try:
            results = self.table.where(f"filename = '{filename}'").to_list()

            formatted_results = []
            for result in results:
                formatted_results.append({
                    "filename": result["filename"],
                    "text": result["text"],
                    "chunk_index": result["chunk_index"],
                    "total_chunks": result["total_chunks"],
                    "node_type": result.get("node_type"),
                    "node_name": result.get("node_name"),
                    "truncated": result.get("truncated", False)
                })

            # Sort by chunk index
            formatted_results.sort(key=lambda x: x["chunk_index"])
            return formatted_results

        except Exception as e:
            logger.error(f"Failed to get file chunks: {e}")
            return []

    def get_table_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database."""
        try:
            count = self.table.count_rows()

            # Get unique files
            files = set()
            for row in self.table.to_list():

                files.add(row["filename"])

            return {
                "total_chunks": count,
                "unique_files": len(files),
                "table_name": "code_chunks",
                "db_path": self.db_path
            }

        except Exception as e:
            logger.error(f"Failed to get table stats: {e}")
            return {}

    def clear_table(self):
        """Clear all data from the table."""
        try:
            self.db.drop_table("code_chunks")
            self.table = self.db.create_table(
                "code_chunks",
                schema=self.schema_class,
                mode="overwrite"
            )
            logger.info("Cleared code_chunks table")
        except Exception as e:
            logger.error(f"Failed to clear table: {e}")
            raise


# Global instance for easy access (can be disabled for testing via PSP_VDB_CREATE_GLOBAL=0)
if os.environ.get("PSP_VDB_CREATE_GLOBAL", "1") == "1":
    vector_db_manager = VectorDBManager()