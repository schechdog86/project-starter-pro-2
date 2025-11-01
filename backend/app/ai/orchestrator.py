"""
Orchestrator
------------
Main controller for agent lifecycle, skills, and project orchestration.
"""

import os
import importlib
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from backend.app.ai.memory_system import memory_system
from backend.app.ai.llm_service import llm_service
from backend.app.skills.base import BaseSkill
from backend.app.skills.registry import SkillRegistry
from backend.app.skills.skill_factory import SkillFactory


class Orchestrator:
    """Main controller for agent lifecycle, skills, and project orchestration."""

    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        self.llm = llm_service
        self.memory = memory_system
        self.skill_registry = SkillRegistry()
        self.skill_factory = SkillFactory(self.skill_registry)
        self.loaded_agents: Dict[str, Any] = {}
        self.audit_log: List[dict] = []
        
        print("✅ Orchestrator initialized")

    # -------------------------
    # Agent Management
    # -------------------------
    def create_agent(self, name: str, config: dict, approve: bool = False) -> bool:
        """
        Create a new agent if approved or whitelisted.
        
        Args:
            name: Agent name
            config: Agent configuration
            approve: Whether to auto-approve
            
        Returns:
            True if created, False if pending approval
        """
        policy = config.get("policy", "user_approval")
        
        if approve or policy == "auto":
            self.loaded_agents[name] = config
            self._log("agent_created", name)
            print(f"✅ Agent created: {name}")
            return True
        
        self._log("agent_pending_approval", name)
        print(f"⏳ Agent pending approval: {name}")
        return False

    def load_agent(self, name: str, cls):
        """
        Instantiate agent class if allowed.
        
        Args:
            name: Agent name
            cls: Agent class
            
        Returns:
            Agent instance or None
        """
        if name not in self.loaded_agents:
            self._log("agent_load_failed", name)
            print(f"❌ Agent load failed: {name} not registered")
            return None
        
        try:
            agent = cls(self)
            self._log("agent_loaded", name)
            print(f"✅ Agent loaded: {name}")
            return agent
        except Exception as e:
            self._log("agent_load_error", {"name": name, "error": str(e)})
            print(f"❌ Agent load error: {name} - {e}")
            return None

    def destroy_agent(self, name: str):
        """
        Destroy an agent.
        
        Args:
            name: Agent name
        """
        if name in self.loaded_agents:
            del self.loaded_agents[name]
            self._log("agent_destroyed", name)
            print(f"✅ Agent destroyed: {name}")

    def list_agents(self) -> List[str]:
        """
        List all loaded agents.
        
        Returns:
            List of agent names
        """
        return list(self.loaded_agents.keys())

    # -------------------------
    # Skill Management
    # -------------------------
    def load_skill(self, skill_name: str) -> Optional[BaseSkill]:
        """
        Load skill by name.
        
        Args:
            skill_name: Skill name
            
        Returns:
            Skill instance or None
        """
        skill_info = self.skill_registry.get_skill(skill_name)
        if not skill_info:
            self._log("skill_missing", skill_name)
            print(f"❌ Skill missing: {skill_name}")
            return None
        
        skill = self.skill_factory.instantiate(skill_name)
        if skill:
            self._log("skill_loaded", skill_name)
        return skill

    def ensure_skill(self, skill_name: str) -> Optional[BaseSkill]:
        """
        Ensure a skill exists; scrape if missing.
        
        Args:
            skill_name: Skill name
            
        Returns:
            Skill instance or None if needs approval
        """
        skill = self.load_skill(skill_name)
        if skill:
            return skill
        
        # Auto-scrape to propose new skill
        try:
            from backend.app.ai import AI_REGISTRY
            scrapegraph = AI_REGISTRY.get("core", {}).get("scrapegraph")
            
            if not scrapegraph:
                print(f"❌ ScrapeGraph not available for skill generation")
                return None
            
            # Use LLM to generate skill template
            prompt = f"""Generate a skill definition for '{skill_name}' with the following JSON schema:
{{
  "name": "{skill_name}",
  "version": "1.0.0",
  "description": "Description of what this skill does",
  "category": "general",
  "enabled": false,
  "parameters": {{
    "param_name": {{
      "type": "string",
      "required": true,
      "description": "Parameter description"
    }}
  }},
  "dependencies": [],
  "frameworks": ["crewai", "autogen", "langchain"],
  "permissions": [],
  "timeout": 30
}}

Also generate a basic Python implementation."""
            
            response = self.llm.chat(prompt, temperature=0.3)
            
            # Create skill directory
            new_skill_dir = Path(self.base_dir, "../skills", skill_name)
            new_skill_dir.mkdir(parents=True, exist_ok=True)
            
            # Save config (disabled by default - needs approval)
            config = {
                "name": skill_name,
                "version": "1.0.0",
                "description": f"Auto-generated skill for {skill_name}",
                "category": "auto_generated",
                "enabled": False,  # Requires manual approval
                "parameters": {},
                "dependencies": [],
                "frameworks": ["crewai", "autogen", "langchain"],
                "permissions": [],
                "timeout": 30
            }
            
            (new_skill_dir / "config.json").write_text(json.dumps(config, indent=2))
            (new_skill_dir / "README.md").write_text(f"# {skill_name}\n\nAuto-generated skill. Review and enable in config.json.\n\n{response}")
            
            self._log("skill_scraped", skill_name)
            print(f"✅ Skill template generated: {skill_name} (requires approval)")
            
            # User must approve manually by setting enabled: true
            return None
            
        except Exception as e:
            self._log("skill_scrape_error", {"skill": skill_name, "error": str(e)})
            print(f"❌ Skill scrape error: {skill_name} - {e}")
            return None

    def add_skill(self, name: str, config: dict, code: str):
        """
        Add new skill with code + config.
        
        Args:
            name: Skill name
            config: Skill configuration
            code: Skill Python code
        """
        path = Path(self.base_dir, "../skills", name)
        path.mkdir(parents=True, exist_ok=True)
        
        (path / "config.json").write_text(json.dumps(config, indent=2))
        (path / "skill.py").write_text(code)
        (path / "__init__.py").write_text("")
        
        self.skill_registry.register_skill(name, config)
        self._log("skill_added", name)
        print(f"✅ Skill added: {name}")

    def list_skills(self) -> List[str]:
        """
        List all available skills.
        
        Returns:
            List of skill names
        """
        return self.skill_registry.list_skills()

    # -------------------------
    # Memory Routing
    # -------------------------
    def route_memory(self, data: dict, importance: int = 1):
        """
        Send data to proper memory tier.
        
        Args:
            data: Data to store
            importance: Importance level (1=normal, 2=high, 3=critical)
        """
        text = json.dumps(data) if isinstance(data, dict) else str(data)
        
        if importance >= 3:
            # Critical - store in Forever tier
            self.memory.teach(text, title=data.get("title", "Critical Memory"))
        elif importance >= 2:
            # High importance - pin in short-term
            self.memory.insert(text, pin=True, title=data.get("title", "Important Memory"))
        else:
            # Normal - regular insert
            self.memory.insert(text, title=data.get("title", "Memory"))
        
        self._log("memory_stored", {"importance": importance})

    def recall_memory(self, query: str, k: int = 10) -> List[dict]:
        """
        Recall memories based on query.
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            List of relevant memories
        """
        results = self.memory.recall(query, k=k)
        self._log("memory_recalled", {"query": query, "count": len(results)})
        return results

    # -------------------------
    # Utility
    # -------------------------
    def _log(self, event: str, data: Any):
        """
        Log an event to audit log.
        
        Args:
            event: Event name
            data: Event data
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "data": data
        }
        self.audit_log.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]

    def get_audit_log(self, limit: int = 100) -> List[dict]:
        """
        Get recent audit log entries.
        
        Args:
            limit: Maximum number of entries
            
        Returns:
            List of log entries
        """
        return self.audit_log[-limit:]

    def get_status(self) -> dict:
        """
        Get orchestrator status.
        
        Returns:
            Status dictionary
        """
        return {
            "agents": len(self.loaded_agents),
            "skills": len(self.skill_registry.list_skills()),
            "audit_log_size": len(self.audit_log),
            "loaded_agents": list(self.loaded_agents.keys()),
            "available_skills": self.skill_registry.list_skills()
        }


# Singleton instance
orchestrator = Orchestrator()

