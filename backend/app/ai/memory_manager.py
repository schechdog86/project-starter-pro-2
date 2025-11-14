"""
Memory Manager for agent long-term and episodic memory, backed by LanceDB.
"""
import os
import time
import logging
from typing import List, Dict, Any, Optional

import lancedb  # type: ignore
from lancedb.pydantic import LanceModel, Vector
from lancedb.embeddings import get_registry

from backend.app.core.rag_config import rag_settings

logger = logging.getLogger(__name__)


class Memories(LanceModel):
    """Schema for agent memories in LanceDB."""
    user_id: str
    scope: str  # e.g., "project", "session", "global"
    type: str   # e.g., "decision", "preference", "summary", "snippet"
    text: str
    ts: float  # unix timestamp
    vector: Vector(1024)  # voyage-code-3 uses 1024 dimensions

    # Optional metadata
    source: Optional[str] = None  # url or file path
    tags: Optional[List[str]] = None


class MemoryManager:
    """Manages vectorized memories for retrieval-augmented agents."""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or rag_settings.VECTOR_DB_PATH
        self.db = None
        self.table = None
        self.embedding_func = None

        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._initialize_embedding_function()
        self._connect_to_db()

    def _initialize_embedding_function(self):
        """Initialize embedding function (Voyage AI via OpenAI-compatible plugin)."""
        try:
            # Ensure API key is in environment (LanceDB requires env vars for sensitive keys)
            api_key = rag_settings.VOYAGE_API_KEY or os.environ.get("VOYAGE_API_KEY")
            if not api_key:
                raise ValueError("Voyage AI API key not found. Set VOYAGE_API_KEY environment variable.")
            os.environ["VOYAGE_API_KEY"] = api_key

            self.embedding_func = get_registry().get("openai").create(
                name=rag_settings.EMBEDDINGS_MODEL,
                base_url=rag_settings.VOYAGE_API_BASE,
                api_key="$VOYAGE_API_KEY",  # Use env var reference
            )
            logger.info(f"Initialized embedding function for Memories: {rag_settings.EMBEDDINGS_MODEL}")
        except Exception as e:
            logger.error(f"Failed to initialize memory embedding function: {e}")
            raise

    def _connect_to_db(self):
        """Connect to LanceDB and ensure the memories table exists."""
        try:
            self.db = lancedb.connect(self.db_path)
            table_names = self.db.table_names()
            if "memories" in table_names:
                self.table = self.db.open_table("memories")
                logger.info("Loaded existing memories table")
            else:
                self.table = self.db.create_table(
                    "memories",
                    schema=Memories,
                    mode="overwrite",
                )
                logger.info("Created new memories table")
        except Exception as e:
            logger.error(f"Failed to connect to memories table: {e}")
            raise

    def add_memory(
        self,
        user_id: str,
        text: str,
        scope: str = "project",
        type: str = "summary",
        tags: Optional[List[str]] = None,
        source: Optional[str] = None,
        ts: Optional[float] = None,
    ) -> int:
        """Insert a memory row. Returns number of rows added (1 or 0)."""
        if not text or not user_id:
            return 0
        try:
            payload = {
                "user_id": user_id,
                "text": text,
                "scope": scope,
                "type": type,
                "tags": tags,
                "source": source,
                "ts": ts or time.time(),
            }
            self.table.add([payload])  # embedding handled automatically by LanceDB
            return 1
        except Exception as e:
            logger.error(f"Failed to add memory: {e}")
            return 0

    def search_memories(
        self,
        user_id: str,
        query: str,
        k: int = 5,
        scope: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Semantic search memories filtered by user and optional scope."""
        try:
            search_query = self.table.search(query).limit(k)
            # Filter by user and optionally scope
            search_query = search_query.where(f"user_id = '{user_id}'")
            if scope:
                search_query = search_query.where(f"scope = '{scope}'")

            results = search_query.to_list()
            formatted: List[Dict[str, Any]] = []
            for r in results:
                formatted.append({
                    "user_id": r["user_id"],
                    "scope": r["scope"],
                    "type": r["type"],
                    "text": r["text"],
                    "ts": r["ts"],
                    "source": r.get("source"),
                    "tags": r.get("tags"),
                    "score": r.get("_distance", 0.0),
                })
            return formatted
        except Exception as e:
            logger.error(f"Memory search failed: {e}")
            return []

    def get_stats(self) -> Dict[str, Any]:
        try:
            count = self.table.count_rows()
            users = set()
            scopes = set()
            for row in self.table.to_list():
                users.add(row["user_id"])
                scopes.add(row["scope"])
            return {
                "total_memories": count,
                "unique_users": len(users),
                "scopes": sorted(list(scopes)),
                "table_name": "memories",
                "db_path": self.db_path,
            }
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {}

    def clear(self):
        try:
            self.db.drop_table("memories")
            self.table = self.db.create_table("memories", schema=Memories, mode="overwrite")
            logger.info("Cleared memories table")
        except Exception as e:
            logger.error(f"Failed to clear memories: {e}")
            raise


# Global instance for easy import (can be disabled for testing via PSP_VDB_CREATE_GLOBAL=0)
if os.environ.get("PSP_VDB_CREATE_GLOBAL", "1") == "1":
    memory_manager = MemoryManager()
else:
    memory_manager = None

