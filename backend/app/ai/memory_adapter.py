"""
Unified Memory Adapter for Project RAG
=====================================

Goal:
- Provide a per-project RAG store with a simple, unified interface.
- Default to local-first FAISS (no extra deps) under data/projects/<name>/rag
- Optionally support external vector DBs (Qdrant/Weaviate) if installed & enabled.

Backends:
- faiss_local (default) — uses MemorySystem with project-specific root
- qdrant (optional) — requires qdrant-client + sentence-transformers
- weaviate (optional) — requires weaviate-client + sentence-transformers

This module avoids hard dependencies: optional imports guarded at runtime.
"""
from __future__ import annotations

import os
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from backend.app.ai.memory_system import MemorySystem


def _safe_rel(base: Path, cand: Path) -> Path:
    """Ensure cand is inside base (prevent path traversal)."""
    base = base.resolve()
    cand = cand.resolve()
    if not str(cand).startswith(str(base)):
        raise ValueError("path outside allowed base")
    return cand


@dataclass
class RagResult:
    id: str
    score: float
    title: str = ""
    metadata: Optional[dict] = None


class UnifiedMemoryAdapter:
    """Per-project unified RAG adapter."""

    SUPPORTED_CATEGORIES = ("docs", "code", "graphics", "marketing", "research")

    def __init__(self, project_name: str, backend: Optional[str] = None, dims: int = 768):
        self.project = project_name
        self.backend = (backend or os.getenv("RAG_BACKEND", "faiss_local")).lower()
        self.base_dir = Path("data/projects") / project_name
        self.docs_dir = self.base_dir / "docs"
        self.rag_dir = self.base_dir / "rag"
        self.dims = dims

        # Ensure directories exist (project + category subfolders + rag root)
        self.ensure_project_dirs()

        # Backends
        self._ms: Optional[MemorySystem] = None
        self._qdrant = None
        self._weaviate = None
        self._embed_fn = None

        if self.backend == "faiss_local":
            self._ms = MemorySystem(cfg={"root": str(self.rag_dir), "dims": self.dims})
        elif self.backend == "qdrant":
            self._init_qdrant()
        elif self.backend == "weaviate":
            self._init_weaviate()
        else:
            raise ValueError(f"Unsupported RAG backend: {self.backend}")

    # --------------------------- dirs ---------------------------
    def ensure_project_dirs(self):
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.docs_dir.mkdir(parents=True, exist_ok=True)
        self.rag_dir.mkdir(parents=True, exist_ok=True)
        for cat in self.SUPPORTED_CATEGORIES:
            (self.docs_dir / cat).mkdir(parents=True, exist_ok=True)

    # --------------------------- ingest ---------------------------
    def add_text(self, text: str, *, title: str = "", category: str = "docs", meta: Optional[dict] = None) -> str:
        """Add raw text to the RAG store and return an item id."""
        self._validate_category(category)
        meta = meta or {}
        meta.update({"project": self.project, "category": category})

        if self.backend == "faiss_local":
            return self._ms.insert(text, sets=[category, f"project:{self.project}"], meta=meta, title=title)
        elif self.backend == "qdrant":
            return self._qdrant_add(text, title=title, meta=meta)
        else:
            return self._weaviate_add(text, title=title, meta=meta)

    def add_file(self, src_path: str, *, filename: Optional[str] = None, category: str = "docs") -> str:
        """
        Copy a source file into the project's category folder and index it.
        Source reading is restricted to data/imports to avoid arbitrary FS access.
        """
        self._validate_category(category)
        base = Path("data/imports")
        src = _safe_rel(base, Path(src_path))
        if not src.exists():
            raise FileNotFoundError(f"Not found: {src}")

        # Read + copy
        text = src.read_text(encoding="utf-8", errors="ignore")
        dst_name = filename or src.name
        dst = self.docs_dir / category / dst_name
        dst.write_text(text, encoding="utf-8")

        return self.add_text(text, title=dst_name, category=category, meta={"path": str(dst)})

    def ingest_project_docs(self, categories: Optional[Iterable[str]] = None, exts: Tuple[str, ...] = (".md", ".txt", ".py")) -> int:
        """Ingest all files under project docs/<category> with given extensions. Returns count."""
        cats = list(categories) if categories else list(self.SUPPORTED_CATEGORIES)
        count = 0
        for cat in cats:
            self._validate_category(cat)
            for p in (self.docs_dir / cat).rglob("*"):
                if p.is_file() and p.suffix.lower() in exts:
                    try:
                        text = p.read_text(encoding="utf-8", errors="ignore")
                        self.add_text(text, title=p.name, category=cat, meta={"path": str(p)})
                        count += 1
                    except Exception:
                        # Skip unreadable files; do not break batch
                        continue
        return count

    # --------------------------- search ---------------------------
    def search(self, query: str, k: int = 10, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search the RAG store for the project."""
        sets_filter = [category] if category else None
        if self.backend == "faiss_local":
            return self._ms.recall(query, k=k, sets_filter=sets_filter)
        elif self.backend == "qdrant":
            return self._qdrant_search(query, k=k, category=category)
        else:
            return self._weaviate_search(query, k=k, category=category)

    # --------------------------- validators ---------------------------
    def _validate_category(self, category: str):
        if category not in self.SUPPORTED_CATEGORIES:
            raise ValueError(f"Invalid category '{category}'. Must be one of {self.SUPPORTED_CATEGORIES}")

    # --------------------------- qdrant ---------------------------
    def _init_qdrant(self):
        try:
            from qdrant_client import QdrantClient
            from sentence_transformers import SentenceTransformer
            from qdrant_client.http import models as qmodels
        except Exception as e:
            raise RuntimeError("qdrant backend requires 'qdrant-client' and 'sentence-transformers' packages") from e

        # Initialize embedder first to discover actual vector dims
        embed_model = os.getenv("RAG_EMBED_MODEL", "intfloat/e5-small-v2")
        _embedder = SentenceTransformer(embed_model)
        self._embed_fn = _embedder.encode
        embed_dim = len(self._embed_fn("probe dims"))
        self.dims = embed_dim

        url = os.getenv("QDRANT_URL", "http://localhost:6333")
        self._qdrant = {
            "client": QdrantClient(url=url),
            "collection": f"project_{self.project}",
            "models": qmodels,
        }
        # Create collection if not exists with correct dims
        col = self._qdrant["collection"]
        try:
            self._qdrant["client"].get_collection(col)
        except Exception:
            self._qdrant["client"].recreate_collection(
                collection_name=col,
                vectors_config=qmodels.VectorParams(size=embed_dim, distance=qmodels.Distance.COSINE),
            )

    def _qdrant_add(self, text: str, *, title: str, meta: dict) -> str:
        import uuid
        vec = self._embed_fn(text)
        try:
            vec = vec.tolist()
        except AttributeError:
            pass
        rid = str(uuid.uuid4())
        payload = {"title": title, "text": text, **meta}
        self._qdrant["client"].upsert(
            collection_name=self._qdrant["collection"],
            points=self._qdrant["models"].Batch(ids=[rid], vectors=[vec], payloads=[payload]),
        )
        return rid

    def _qdrant_search(self, query: str, k: int, category: Optional[str]):
        vec = self._embed_fn(query)
        try:
            vec = vec.tolist()
        except AttributeError:
            pass
        flt = None
        if category:
            flt = self._qdrant["models"].Filter(must=[self._qdrant["models"].FieldCondition(key="category", match=self._qdrant["models"].MatchValue(value=category))])
        res = self._qdrant["client"].search(collection_name=self._qdrant["collection"], query_vector=vec, limit=k, query_filter=flt)
        out = []
        for p in res:
            out.append({"id": str(p.id), "score": float(p.score), "title": p.payload.get("title", ""), "text": p.payload.get("text", ""), "meta": p.payload})
        return out

    # --------------------------- weaviate ---------------------------
    def _init_weaviate(self):
        try:
            import weaviate
            from sentence_transformers import SentenceTransformer
        except Exception as e:
            raise RuntimeError("weaviate backend requires 'weaviate-client' and 'sentence-transformers'") from e

        # Embedder (we pass vectors explicitly; vectorizer:none)
        embed_model = os.getenv("RAG_EMBED_MODEL", "intfloat/e5-small-v2")
        _embedder = SentenceTransformer(embed_model)
        self._embed_fn = _embedder.encode

        url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
        client = weaviate.Client(url)
        index_name = f"project_{self.project}"
        # Ensure class exists
        schema = client.schema.get()
        if not any(c.get("class") == index_name for c in schema.get("classes", [])):
            client.schema.create_class(
                {
                    "class": index_name,
                    "vectorizer": "none",
                    "properties": [
                        {"name": "title", "dataType": ["text"]},
                        {"name": "text", "dataType": ["text"]},
                        {"name": "category", "dataType": ["text"]},
                        {"name": "project", "dataType": ["text"]},
                        {"name": "path", "dataType": ["text"]},
                    ],
                }
            )
        self._weaviate = {"client": client, "index": index_name}

    def _weaviate_add(self, text: str, *, title: str, meta: dict) -> str:
        import uuid
        vec = self._embed_fn(text)
        try:
            vec = vec.tolist()
        except AttributeError:
            pass
        rid = str(uuid.uuid4())
        obj = {"title": title, "text": text, **meta}
        self._weaviate["client"].data_object.create(obj, class_name=self._weaviate["index"], uuid=rid, vector=vec)
        return rid

    def _weaviate_search(self, query: str, k: int, category: Optional[str]):
        # Vector search using our own embeddings
        vec = self._embed_fn(query)
        try:
            vec = vec.tolist()
        except AttributeError:
            pass
        c = self._weaviate["client"].query
        q = c.get(self._weaviate["index"], ["title", "text", "category", "project", "path"]).with_near_vector({"vector": vec}).with_limit(k)
        if category:
            q = q.with_where({"path": ["category"], "operator": "Equal", "valueText": category})
        q = q.with_additional(["id", "distance"])  # distance in [0,2] depending on metric; smaller is better
        res = q.do()
        items = res.get("data", {}).get("Get", {}).get(self._weaviate["index"], [])
        out = []
        for it in items:
            add = it.get("_additional", {})
            dist = float(add.get("distance", 0.0))
            score = 1.0 - dist
            out.append({"id": add.get("id", ""), "score": score, "title": it.get("title", ""), "text": it.get("text", ""), "meta": it})
        return out

