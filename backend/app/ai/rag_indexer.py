"""
RAG Indexing Script for Code Search
"""
import os
import logging
from typing import List, Dict, Any
from pathlib import Path

from backend.app.ai.code_chunker import CodeChunker, discover_code_files, read_file_content
from backend.app.ai.vector_db_manager import VectorDBManager
from backend.app.core.rag_config import rag_settings

from backend.app.ai.memory_manager import memory_manager

logger = logging.getLogger(__name__)


class RAGIndexer:
    """Main RAG indexing class for code search."""

    def __init__(self, chunking_strategy: str = "truncate"):
        self.chunker = CodeChunker(
            chunk_size=rag_settings.CHUNK_SIZE,
            chunk_overlap=rag_settings.CHUNK_OVERLAP
        )
        self.vector_db = VectorDBManager()
        self.chunking_strategy = chunking_strategy

    def index_codebase(self, root_path: str, extensions: List[str] = None) -> Dict[str, Any]:
        """
        Index an entire codebase.

        Args:
            root_path: Root directory to index
            extensions: File extensions to include

        Returns:
            Indexing statistics
        """
        logger.info(f"Starting codebase indexing for: {root_path}")

        # Discover code files
        code_files = discover_code_files(root_path, extensions)
        logger.info(f"Found {len(code_files)} code files")

        total_chunks = 0
        processed_files = 0
        failed_files = 0

        # Process each file
        for filepath in code_files:
            try:
                # Read file content
                content = read_file_content(filepath)
                if not content:
                    logger.warning(f"Skipping empty or unreadable file: {filepath}")
                    failed_files += 1
                    continue

                # Chunk the file
                chunks = self.chunker.chunk_file(filepath, content, self.chunking_strategy)

                # Add chunks to vector database
                if chunks:
                    self.vector_db.add_chunks(chunks)
                    total_chunks += len(chunks)
                    processed_files += 1

                    if processed_files % 100 == 0:
                        logger.info(f"Processed {processed_files} files, {total_chunks} chunks")

            except Exception as e:
                logger.error(f"Failed to process file {filepath}: {e}")
                failed_files += 1

        # Get final statistics
        stats = self.vector_db.get_table_stats()

        result = {
            "root_path": root_path,
            "total_files_found": len(code_files),
            "processed_files": processed_files,
            "failed_files": failed_files,
            "total_chunks_indexed": total_chunks,
            "chunking_strategy": self.chunking_strategy,
            "vector_db_stats": stats,
        }

        # Write memory about indexing run (best-effort)
        try:
            memory_manager.add_memory(
                user_id="system",
                text=(
                    f"Indexed {root_path} files_processed={processed_files} "
                    f"chunks={total_chunks} strategy={self.chunking_strategy}"
                ),
                scope="project",
                type="summary",
                tags=["rag", "index"],
                source=str(root_path),
            )
        except Exception as me:
            logger.debug(f"Skipping indexing memory write: {me}")

        logger.info(f"Indexing completed: {result}")
        return result

    def index_single_file(self, filepath: str) -> Dict[str, Any]:
        """
        Index a single file.

        Args:
            filepath: Path to the file to index

        Returns:
            Indexing result
        """
        try:
            # Read file content
            content = read_file_content(filepath)
            if not content:
                return {"success": False, "error": "Empty or unreadable file"}

            # Chunk the file
            chunks = self.chunker.chunk_file(filepath, content, self.chunking_strategy)

            # Add chunks to vector database
            if chunks:
                self.vector_db.add_chunks(chunks)
                return {
                    "success": True,
                    "filepath": filepath,
                    "chunks_added": len(chunks),
                    "chunking_strategy": self.chunking_strategy
                }
            else:
                return {"success": False, "error": "No chunks generated"}

        except Exception as e:
            logger.error(f"Failed to index file {filepath}: {e}")
            return {"success": False, "error": str(e)}

    def search_code(self, query: str, limit: int = 10, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Search the indexed codebase.

        Args:
            query: Search query
            limit: Maximum number of results
            filters: Optional filters

        Returns:
            List of matching code chunks
        """
        results = self.vector_db.search(query, limit, filters)
        # Write memory about search (best-effort)
        try:
            memory_manager.add_memory(
                user_id="system",
                text=f"search query='{query}' results={len(results)}",
                scope="session",
                type="activity",
                tags=["rag", "search"],
                source="RAGIndexer.search_code",
            )
        except Exception as me:
            logger.debug(f"Skipping search memory write: {me}")
        return results

    def get_file_context(self, filename: str) -> List[Dict[str, Any]]:
        """
        Get all chunks for a specific file.

        Args:
            filename: File to retrieve

        Returns:
            List of chunks from the file
        """
        return self.vector_db.get_file_chunks(filename)

    def get_index_stats(self) -> Dict[str, Any]:
        """Get indexing statistics."""
        return self.vector_db.get_table_stats()

    def clear_index(self):
        """Clear the entire index."""
        self.vector_db.clear_table()
        logger.info("Index cleared")


# Global instance for easy access (can be disabled for testing via PSP_VDB_CREATE_GLOBAL=0)
if os.environ.get("PSP_VDB_CREATE_GLOBAL", "1") == "1":
    rag_indexer = RAGIndexer()
else:
    rag_indexer = None


def create_indexing_script():
    """
    Create a standalone indexing script that can be run from command line.
    """
    script_content = '''#!/usr/bin/env python3
"""
Standalone RAG Indexing Script
"""
import os
import sys
import argparse
import logging
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from backend.app.ai.rag_indexer import RAGIndexer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description='Index codebase for RAG search')
    parser.add_argument('root_path', help='Root directory to index')
    parser.add_argument('--strategy', choices=['truncate', 'fixed', 'ast'],
                       default='truncate', help='Chunking strategy')
    parser.add_argument('--clear', action='store_true',
                       help='Clear existing index before indexing')
    parser.add_argument('--extensions', nargs='+',
                       default=['.py', '.js', '.ts', '.java', '.cpp', '.c', '.h'],
                       help='File extensions to include')

    args = parser.parse_args()

    # Initialize indexer
    indexer = RAGIndexer(chunking_strategy=args.strategy)

    # Clear index if requested
    if args.clear:
        logger.info("Clearing existing index...")
        indexer.clear_index()

    # Index the codebase
    logger.info(f"Starting indexing of {args.root_path} with strategy: {args.strategy}")
    result = indexer.index_codebase(args.root_path, args.extensions)

    # Print results
    print("\n=== Indexing Results ===")
    print(f"Root path: {result['root_path']}")
    print(f"Files found: {result['total_files_found']}")
    print(f"Files processed: {result['processed_files']}")
    print(f"Files failed: {result['failed_files']}")
    print(f"Total chunks indexed: {result['total_chunks_indexed']}")
    print(f"Chunking strategy: {result['chunking_strategy']}")
    print(f"Vector DB stats: {result['vector_db_stats']}")

    logger.info("Indexing completed successfully")


if __name__ == "__main__":
    main()
'''

    # Write the script to a file
    script_path = Path("scripts/index_codebase.py")
    script_path.parent.mkdir(exist_ok=True)

    with open(script_path, "w") as f:
        f.write(script_content)

    # Make it executable
    script_path.chmod(0o755)

    logger.info(f"Created indexing script at: {script_path}")
    return str(script_path)


# Create the indexing script when this module is imported
if __name__ != "__main__":
    try:
        indexing_script_path = create_indexing_script()
        logger.info(f"Indexing script available at: {indexing_script_path}")
    except Exception as e:
        logger.warning(f"Could not create indexing script: {e}")
