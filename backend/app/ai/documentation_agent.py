"""
Documentation Agent - Automated Documentation Ingestion and Search

Integrates with the scraping system to automatically ingest scraped documentation
into the Weaviate RAG system, making it searchable by all agents.

Features:
- Automatic ingestion of scraped documentation
- Periodic updates when new docs are scraped
- Semantic search across all framework documentation
- Integration with orchestrator for agent access
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from backend.app.ai.memory_adapter import UnifiedMemoryAdapter


class DocumentationAgent:
    """
    Documentation Agent that manages framework documentation ingestion and search.
    
    Responsibilities:
    1. Monitor scraping results and ingest new documentation
    2. Maintain RAG indices for all library categories
    3. Provide semantic search across documentation
    4. Track ingestion status and metrics
    """
    
    def __init__(self, backend: str = "weaviate"):
        """
        Initialize Documentation Agent.
        
        Args:
            backend: RAG backend to use (weaviate, qdrant, faiss_local)
        """
        self.backend = backend
        self.data_dir = Path("data/projects")
        self.results_dir = Path("data/scraping_results")
        self.status_file = self.results_dir / "ingestion_status.json"
        
        # Initialize RAG adapters for each library
        self.libraries = {
            "ai_frameworks": None,
            "business_resources": None,
            "technical_resources": None,
        }
        
        # Load ingestion status
        self.status = self._load_status()
    
    def _load_status(self) -> Dict[str, Any]:
        """Load ingestion status from file."""
        if self.status_file.exists():
            with open(self.status_file, 'r') as f:
                return json.load(f)
        return {
            "last_ingestion": None,
            "libraries": {},
            "total_documents": 0,
        }
    
    def _save_status(self):
        """Save ingestion status to file."""
        self.results_dir.mkdir(parents=True, exist_ok=True)
        with open(self.status_file, 'w') as f:
            json.dump(self.status, f, indent=2)
    
    def _get_rag_adapter(self, library: str) -> UnifiedMemoryAdapter:
        """Get or create RAG adapter for a library."""
        if self.libraries[library] is None:
            project_name = f"library_{library.replace('_', '-')}"
            self.libraries[library] = UnifiedMemoryAdapter(
                project_name=project_name,
                backend=self.backend
            )
        return self.libraries[library]
    
    def ingest_library(self, library: str, force: bool = False) -> Dict[str, Any]:
        """
        Ingest all documentation for a specific library.
        
        Args:
            library: Library name (ai_frameworks, business_resources, technical_resources)
            force: Force re-ingestion even if already ingested
            
        Returns:
            Dict with ingestion results
        """
        if library not in self.libraries:
            raise ValueError(f"Unknown library: {library}")
        
        # Check if already ingested
        lib_status = self.status["libraries"].get(library, {})
        if not force and lib_status.get("ingested", False):
            return {
                "library": library,
                "status": "skipped",
                "reason": "already_ingested",
                "documents": lib_status.get("document_count", 0),
            }
        
        # Get RAG adapter
        rag = self._get_rag_adapter(library)
        
        # Check if docs directory exists
        if not rag.docs_dir.exists():
            return {
                "library": library,
                "status": "error",
                "reason": "docs_directory_not_found",
                "path": str(rag.docs_dir),
            }
        
        # Count existing files
        md_files = list(rag.docs_dir.rglob("*.md"))
        if not md_files:
            return {
                "library": library,
                "status": "skipped",
                "reason": "no_documents_found",
            }
        
        # Ingest all docs
        try:
            count = rag.ingest_project_docs()
            
            # Update status
            self.status["libraries"][library] = {
                "ingested": True,
                "document_count": count,
                "file_count": len(md_files),
                "last_ingestion": datetime.now().isoformat(),
            }
            self.status["total_documents"] = sum(
                lib.get("document_count", 0) 
                for lib in self.status["libraries"].values()
            )
            self.status["last_ingestion"] = datetime.now().isoformat()
            self._save_status()
            
            return {
                "library": library,
                "status": "success",
                "documents": count,
                "files": len(md_files),
            }
        except Exception as e:
            return {
                "library": library,
                "status": "error",
                "reason": str(e),
            }
    
    def ingest_all(self, force: bool = False) -> Dict[str, Any]:
        """
        Ingest documentation for all libraries.
        
        Args:
            force: Force re-ingestion even if already ingested
            
        Returns:
            Dict with overall ingestion results
        """
        results = {}
        total_docs = 0
        
        for library in self.libraries.keys():
            result = self.ingest_library(library, force=force)
            results[library] = result
            if result["status"] == "success":
                total_docs += result["documents"]
        
        return {
            "status": "complete",
            "libraries": results,
            "total_documents": total_docs,
            "timestamp": datetime.now().isoformat(),
        }
    
    def search(
        self,
        query: str,
        library: Optional[str] = None,
        k: int = 5,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search documentation across libraries.
        
        Args:
            query: Search query
            library: Specific library to search (None = search all)
            k: Number of results to return
            category: Optional category filter
            
        Returns:
            List of search results with metadata
        """
        if library:
            # Search specific library
            if library not in self.libraries:
                raise ValueError(f"Unknown library: {library}")
            
            rag = self._get_rag_adapter(library)
            results = rag.search(query, k=k, category=category)
            
            # Add library metadata
            for result in results:
                result["library"] = library
            
            return results
        else:
            # Search all libraries
            all_results = []
            for lib in self.libraries.keys():
                try:
                    rag = self._get_rag_adapter(lib)
                    results = rag.search(query, k=k, category=category)
                    
                    # Add library metadata
                    for result in results:
                        result["library"] = lib
                    
                    all_results.extend(results)
                except Exception:
                    continue
            
            # Sort by score and return top k
            all_results.sort(key=lambda x: x.get("score", 0), reverse=True)
            return all_results[:k]
    
    def get_status(self) -> Dict[str, Any]:
        """Get current ingestion status."""
        return {
            **self.status,
            "backend": self.backend,
            "libraries_available": list(self.libraries.keys()),
        }
    
    def check_new_documents(self) -> Dict[str, int]:
        """
        Check for new documents that haven't been ingested.
        
        Returns:
            Dict mapping library names to count of new documents
        """
        new_docs = {}
        
        for library in self.libraries.keys():
            lib_dir = self.data_dir / f"library_{library.replace('_', '-')}" / "docs"
            if not lib_dir.exists():
                continue
            
            current_count = len(list(lib_dir.rglob("*.md")))
            ingested_count = self.status["libraries"].get(library, {}).get("file_count", 0)
            
            if current_count > ingested_count:
                new_docs[library] = current_count - ingested_count
        
        return new_docs
    
    def auto_ingest_new(self) -> Dict[str, Any]:
        """
        Automatically ingest new documents that haven't been processed.
        
        Returns:
            Dict with ingestion results for libraries with new docs
        """
        new_docs = self.check_new_documents()
        
        if not new_docs:
            return {
                "status": "no_new_documents",
                "timestamp": datetime.now().isoformat(),
            }
        
        results = {}
        for library in new_docs.keys():
            result = self.ingest_library(library, force=True)
            results[library] = result
        
        return {
            "status": "complete",
            "libraries": results,
            "timestamp": datetime.now().isoformat(),
        }

