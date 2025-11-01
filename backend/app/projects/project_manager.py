# backend/app/projects/project_manager.py
from backend.app.ai.memory_system import MemorySystem
from backend.app.projects.doc_flow import DocumentFlow


class ProjectManager:
    """Manages project lifecycle and document flow."""
    
    def __init__(self, orchestrator):
        self.orch = orchestrator
        self.memory = MemorySystem()
        self.flow = DocumentFlow(orchestrator)

    def handle_project(self, name: str):
        """
        Handle project progression through document flow.
        
        Args:
            name: Project name
            
        Returns:
            Updated project data
        """
        pr = self.flow.advance(name)
        self.memory.insert(
            f"Project {name} in phase {pr.get('phase', 'unknown')}",
            title=f"Project {name} Status"
        )
        return pr

