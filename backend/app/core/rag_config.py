"""
RAG Configuration for Code Search
"""
from pydantic import BaseModel, Field
from backend.app.core.config import Settings


class RAGSettings(BaseModel):
    """RAG-specific configuration settings."""

    # Embeddings Model
    EMBEDDINGS_MODEL: str = Field(
        default="voyage-code-3",
        description="Embeddings model for code search"
    )

    # Vector Database
    VECTOR_DB_PATH: str = Field(
        default=".local/vector_db",
        description="Path to store LanceDB vector database"
    )

    # Chunking Strategy
    CHUNK_SIZE: int = Field(
        default=1000,
        description="Default chunk size for code splitting"
    )

    CHUNK_OVERLAP: int = Field(
        default=200,
        description="Overlap between chunks for context preservation"
    )

    # Voyage AI Configuration
    VOYAGE_API_KEY: str = Field(
        default="",
        description="Voyage AI API key for embeddings"
    )

    VOYAGE_API_BASE: str = Field(
        default="https://api.voyageai.com/v1/",
        description="Voyage AI API base URL"
    )

    # Reranking Configuration
    RERANK_MODEL: str = Field(
        default="rerank-2",
        description="Reranking model for improving search results"
    )

    RERANK_INITIAL_RESULTS: int = Field(
        default=50,
        description="Number of initial results to retrieve before reranking"
    )

    RERANK_FINAL_RESULTS: int = Field(
        default=10,
        description="Number of final results to return after reranking"
    )


# Global RAG settings instance
rag_settings = RAGSettings()
