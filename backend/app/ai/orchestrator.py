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
from backend.app.ai.data_retrieval import DataRetrieval
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
        self.retriever = DataRetrieval()
        self.loaded_agents: Dict[str, Any] = {}
        self.audit_log: List[dict] = []

        # Import ProjectManager here to avoid circular imports
        self.project_manager = None

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

    # -------------------------
    # Research & Data Retrieval
    # -------------------------
    def research_retrieve(self, topic: str, urls: List[str]) -> dict:
        """
        Retrieve and store research data via ScrapeGraph + Firecrawl.

        Args:
            topic: Research topic
            urls: List of URLs to scrape

        Returns:
            Merged research data
        """
        try:
            # Scrape all URLs
            scrape_results = self.retriever.search_and_cache(topic, urls)

            # Crawl first domain
            crawl_data = {}
            if urls:
                domain = urls[0].split('/')[2] if '/' in urls[0] else urls[0]
                crawl_data = self.retriever.crawl(domain, depth=1, out_name=f"{topic}_crawl.json")

            # Merge results
            merged = {
                "topic": topic,
                "scrapes": scrape_results,
                "crawl": crawl_data,
                "url_count": len(urls)
            }

            # Store in memory with high importance
            self.memory.teach(
                f"Research on {topic}: {len(urls)} sources analyzed",
                title=f"Research: {topic}"
            )

            self._log("research_retrieved", {"topic": topic, "urls": len(urls)})
            print(f"✅ Research retrieved: {topic} ({len(urls)} URLs)")

            return merged

        except Exception as e:
            self._log("research_error", {"topic": topic, "error": str(e)})
            print(f"❌ Research retrieval error: {e}")
            return {"error": str(e)}

    # -------------------------
    # Project Management
    # -------------------------
    def run_project(self, name: str) -> dict:
        """
        Run project through document flow.

        Args:
            name: Project name

        Returns:
            Project data
        """
        # Lazy load project manager to avoid circular imports
        if not self.project_manager:
            from backend.app.projects.project_manager import ProjectManager
            self.project_manager = ProjectManager(self)

        try:
            result = self.project_manager.handle_project(name)
            self._log("project_run", {"name": name})
            print(f"✅ Project run: {name}")
            return result
        except Exception as e:
            self._log("project_error", {"name": name, "error": str(e)})
            print(f"❌ Project error: {e}")
            return {"error": str(e)}

    # -------------------------
    # Skill Approval Methods
    # -------------------------
    def get_skill_info(self, name: str) -> Optional[dict]:
        """
        Get skill information.

        Args:
            name: Skill name

        Returns:
            Skill config or None
        """
        return self.skill_registry.get_skill(name)

    def approve_skill(self, name: str, enabled: bool = True) -> bool:
        """
        Approve and enable a skill.

        Args:
            name: Skill name
            enabled: Whether to enable

        Returns:
            True if successful
        """
        skill_info = self.skill_registry.get_skill(name)
        if not skill_info:
            return False

        # Update config
        skill_info["enabled"] = enabled

        # Save to file
        from pathlib import Path
        import json
        skill_path = Path(self.base_dir, "../skills", name, "config.json")
        if skill_path.exists():
            skill_path.write_text(json.dumps(skill_info, indent=2))
            self.skill_registry.reload()
            self._log("skill_approved", {"name": name, "enabled": enabled})
            print(f"✅ Skill approved: {name} (enabled={enabled})")
            return True

        return False

    def execute_skill(self, name: str, params: dict) -> Any:
        """
        Execute a skill with parameters.

        Args:
            name: Skill name
            params: Skill parameters

        Returns:
            Skill execution result
        """
        skill = self.load_skill(name)
        if not skill:
            raise ValueError(f"Skill '{name}' not found or not enabled")

        result = skill.execute(**params)
        self._log("skill_executed", {"name": name, "params": params})
        return result

    def generate_skill_from_prompt(self, name: str, prompt: str) -> dict:
        """
        Generate a new skill from a prompt using LLM.

        Args:
            name: Skill name
            prompt: Description of what the skill should do

        Returns:
            Generated skill draft
        """
        try:
            # Create prompt for LLM
            system_prompt = f"""Generate a Python skill class for '{name}' based on this description:
{prompt}

The skill should:
1. Inherit from BaseSkill
2. Implement execute() method
3. Validate parameters
4. Return meaningful results

Also generate a config.json with:
- name, version, description
- parameters with types and descriptions
- permissions needed
- timeout value

Return both the Python code and JSON config."""

            response = self.llm.chat(system_prompt, temperature=0.3, max_tokens=2000)

            self._log("skill_generated", {"name": name, "prompt": prompt})
            print(f"✅ Skill draft generated: {name}")

            return {
                "name": name,
                "draft": response,
                "status": "pending_review"
            }

        except Exception as e:
            self._log("skill_generation_error", {"name": name, "error": str(e)})
            print(f"❌ Skill generation error: {e}")
            return {"error": str(e)}


# Singleton instance
orchestrator = Orchestrator()

