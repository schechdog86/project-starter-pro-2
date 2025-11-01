"""
Skill Registry
--------------
Manages skill metadata and discovery.
"""

import json
from pathlib import Path
from typing import Dict, Optional, List


class SkillRegistry:
    """Manages skill metadata and discovery."""

    def __init__(self):
        self.registry_path = Path(__file__).parent / "registry.json"
        self.skills: Dict[str, dict] = {}
        self._load_registry()
        self.discover_skills()

    def _load_registry(self):
        """Load registry from registry.json"""
        if self.registry_path.exists():
            try:
                self.skills = json.loads(self.registry_path.read_text())
                print(f"✅ Loaded {len(self.skills)} skills from registry")
            except Exception as e:
                print(f"❌ Failed to load registry: {e}")
                self.skills = {}

    def _save_registry(self):
        """Save registry to registry.json"""
        try:
            self.registry_path.write_text(json.dumps(self.skills, indent=2))
            print(f"✅ Saved {len(self.skills)} skills to registry")
        except Exception as e:
            print(f"❌ Failed to save registry: {e}")

    def discover_skills(self):
        """Auto-discover skills from directory structure"""
        base = Path(__file__).parent
        discovered = 0
        
        for skill_dir in base.iterdir():
            if not skill_dir.is_dir() or skill_dir.name.startswith("_"):
                continue
            
            config_path = skill_dir / "config.json"
            if not config_path.exists():
                continue
            
            try:
                data = json.loads(config_path.read_text())
                skill_name = data.get("name", skill_dir.name)
                
                # Only register if enabled
                if data.get("enabled", True):
                    self.skills[skill_name] = data
                    discovered += 1
                    print(f"✅ Discovered skill: {skill_name}")
            except Exception as e:
                print(f"❌ Failed to load skill {skill_dir.name}: {e}")
        
        if discovered > 0:
            self._save_registry()
        
        print(f"✅ Skill discovery complete: {discovered} skills found")

    def get_skill(self, name: str) -> Optional[dict]:
        """
        Get skill configuration by name.
        
        Args:
            name: Skill name
            
        Returns:
            Skill configuration or None
        """
        return self.skills.get(name)

    def register_skill(self, name: str, config: dict):
        """
        Register a new skill.
        
        Args:
            name: Skill name
            config: Skill configuration
        """
        self.skills[name] = config
        self._save_registry()
        print(f"✅ Registered skill: {name}")

    def unregister_skill(self, name: str):
        """
        Unregister a skill.
        
        Args:
            name: Skill name
        """
        if name in self.skills:
            del self.skills[name]
            self._save_registry()
            print(f"✅ Unregistered skill: {name}")

    def list_skills(self) -> List[str]:
        """
        List all registered skill names.
        
        Returns:
            List of skill names
        """
        return list(self.skills.keys())

    def list_skills_by_category(self, category: str) -> List[str]:
        """
        List skills by category.
        
        Args:
            category: Skill category
            
        Returns:
            List of skill names in category
        """
        return [
            name for name, config in self.skills.items()
            if config.get("category") == category
        ]

    def get_all_skills(self) -> Dict[str, dict]:
        """
        Get all skill configurations.
        
        Returns:
            Dictionary of all skills
        """
        return self.skills.copy()

    def reload(self):
        """Reload registry from disk and rediscover skills"""
        self.skills = {}
        self._load_registry()
        self.discover_skills()

