# backend/app/projects/doc_flow.py
"""
Document Flow System
--------------------
Moves a project through required docs by invoking known agents.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime


class DocumentFlow:
    """Moves a project through required docs by invoking known agents (loaded by orchestrator)."""


    def _project_dir(self, name: str) -> Path:
        d = Path("data/projects") / name
        d.mkdir(parents=True, exist_ok=True)
        # Ensure per-project doc categories exist
        docs = d / "docs"
        for cat in ("docs", "code", "graphics", "marketing", "research"):
            (docs / cat).mkdir(parents=True, exist_ok=True)
        # Ensure per-project RAG root exists
        (d / "rag").mkdir(parents=True, exist_ok=True)
        return d

    def _project_file(self, name: str) -> Path:
        return self._project_dir(name) / "project.json"

    def __init__(self, orchestrator):
        self.orch = orchestrator

    def advance(self, name: str) -> Dict[str, Any]:
        """
        Advance project to next document phase.

        This implementation is production-ready for persistence using a
        local-first project store at data/projects/<name>/project.json.
        It safely advances the document workflow and records status timestamps.

        Args:
            name: Project name

        Returns:
            Updated project data
        """
        # Ordered steps for document flow
        steps_order = [
            "01_project_scope.md",
            "02_research_outline.md",
            "03_technical_spec.md",
            "04_project_outline.md",
            "10_business_plan.md",
        ]

        pr = self._load_project(name)
        docs_status: Dict[str, Any] = pr.get("docs_status") or {}
        current = pr.get("next_required_doc") or steps_order[0]

        # Initialize current doc status if missing
        if current not in docs_status:
            docs_status[current] = {
                "status": "in_progress",
                "started_at": datetime.now().isoformat(),
            }

        # Mark current as done and compute next
        docs_status[current]["status"] = "done"
        docs_status[current]["completed_at"] = datetime.now().isoformat()

        try:
            idx = steps_order.index(current)
            next_doc = steps_order[idx + 1] if idx + 1 < len(steps_order) else None
        except ValueError:
            next_doc = steps_order[0] if steps_order else None

        pr["docs_status"] = docs_status
        pr["next_required_doc"] = next_doc
        pr["phase"] = "complete" if next_doc is None else "in_progress"

        self._save_project(name, pr)
        self.orch._log("doc_advanced", {"project": name, "from": current, "to": next_doc})
        return pr

    def _get_agent(self, agent_name: str) -> Optional[Any]:
        """
        Get agent instance from orchestrator.

        Args:
            agent_name: Agent name

        Returns:
            Agent instance or None
        """
        # Check if agent is loaded
        if agent_name in self.orch.loaded_agents:
            # Return the agent config for now
            # In full implementation, this would return the actual agent instance
            return self.orch.loaded_agents[agent_name]
        return None

    def _load_project(self, name: str) -> Dict[str, Any]:
        """
        Load project data from local project store.

        Args:
            name: Project name

        Returns:
            Project data dict
        """
        path = self._project_file(name)
        if path.exists():
            try:
                return json.loads(path.read_text())
            except Exception:
                # Corrupt file fallback
                self.orch._log("project_load_corrupt", {"name": name})
        # Default structure
        return {
            "name": name,
            "phase": "planning",
            "next_required_doc": "01_project_scope.md",
            "docs_status": {},
            "updated_at": datetime.now().isoformat(),
        }

    def _save_project(self, name: str, data: Dict[str, Any]):
        """
        Persist project data to local project store.

        Args:
            name: Project name
            data: Project data
        """
        path = self._project_file(name)
        # Ensure updated timestamp
        data["updated_at"] = datetime.now().isoformat()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2))
        self.orch._log("project_saved", {"name": name, "phase": data.get("phase")})

