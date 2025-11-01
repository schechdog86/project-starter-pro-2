# backend/app/projects/doc_flow.py
"""
Document Flow System
--------------------
Moves a project through required docs by invoking known agents.
"""

from typing import Dict, Any, Optional


class DocumentFlow:
    """Moves a project through required docs by invoking known agents (loaded by orchestrator)."""

    def __init__(self, orchestrator):
        self.orch = orchestrator

    def advance(self, name: str) -> Dict[str, Any]:
        """
        Advance project to next document phase.
        
        Args:
            name: Project name
            
        Returns:
            Updated project data
        """
        # Load project data (placeholder - will integrate with project_fs later)
        pr = self._load_project(name)
        nxt = pr.get("next_required_doc")

        # Map docs → agent class + method to call
        steps = {
            "01_project_scope.md": ("ProjectWizard", "run"),
            "02_research_outline.md": ("ResearchCoordinator", "outline"),
            "03_technical_spec.md": ("DeveloperAgent", "technical_spec"),
            "04_project_outline.md": ("ProjectTracker", "outline"),
            "10_business_plan.md": ("ReportCompiler", "business_plan"),
        }

        if nxt in steps:
            agent_name, method_name = steps[nxt]
            
            # Try to load agent (will be None if not registered)
            agent = self._get_agent(agent_name)
            
            if agent:
                # Execute agent method
                if hasattr(agent, method_name):
                    fn = getattr(agent, method_name)
                    fn(name, pr)
                    self._save_project(name, pr)
                    self.orch._log("doc_done", {"project": name, "doc": nxt})
                else:
                    self.orch._log("doc_method_missing", {
                        "project": name,
                        "doc": nxt,
                        "agent": agent_name,
                        "method": method_name
                    })
            else:
                self.orch._log("doc_agent_missing", {
                    "project": name,
                    "doc": nxt,
                    "agent": agent_name
                })
        else:
            self.orch._log("doc_unknown", {"project": name, "doc": nxt})

        return self._load_project(name)

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
        Load project data.
        
        Args:
            name: Project name
            
        Returns:
            Project data
        """
        # Placeholder implementation
        # In full version, this would load from project_fs
        return {
            "name": name,
            "phase": "planning",
            "next_required_doc": "01_project_scope.md",
            "docs_status": {}
        }

    def _save_project(self, name: str, data: Dict[str, Any]):
        """
        Save project data.
        
        Args:
            name: Project name
            data: Project data
        """
        # Placeholder implementation
        # In full version, this would save to project_fs
        self.orch._log("project_saved", {"name": name, "phase": data.get("phase")})

