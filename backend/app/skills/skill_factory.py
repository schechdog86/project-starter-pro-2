"""
Skill Factory
-------------
Loads skill Python modules dynamically.
"""

import importlib
from pathlib import Path
from typing import Optional
from backend.app.skills.registry import SkillRegistry
from backend.app.skills.base import BaseSkill


class SkillFactory:
    """Loads skill Python module dynamically."""

    def __init__(self, registry: SkillRegistry):
        """
        Initialize skill factory.
        
        Args:
            registry: Skill registry instance
        """
        self.registry = registry
        self.base_dir = Path(__file__).parent
        self._cache = {}

    def instantiate(self, name: str) -> Optional[BaseSkill]:
        """
        Instantiate a skill by name.
        
        Args:
            name: Skill name
            
        Returns:
            Skill instance or None if not found
        """
        # Check cache first
        if name in self._cache:
            config = self.registry.get_skill(name)
            if config:
                return self._cache[name](config)
        
        # Get skill configuration
        config = self.registry.get_skill(name)
        if not config:
            print(f"❌ Skill '{name}' not found in registry")
            return None
        
        # Build module path
        module_path = f"backend.app.skills.{name}.skill"
        
        try:
            # Import module
            mod = importlib.import_module(module_path)
            
            # Find skill class
            # Try multiple naming conventions
            class_names = [
                f"{name.replace('_', '').capitalize()}Skill",  # web_search -> WebsearchSkill
                f"{''.join(word.capitalize() for word in name.split('_'))}Skill",  # web_search -> WebSearchSkill
                f"{name.capitalize()}Skill",  # web_search -> Web_searchSkill
            ]
            
            skill_class = None
            for class_name in class_names:
                skill_class = getattr(mod, class_name, None)
                if skill_class:
                    break
            
            if not skill_class:
                print(f"❌ Skill class not found in {module_path}")
                print(f"   Tried: {class_names}")
                return None
            
            # Cache the class
            self._cache[name] = skill_class
            
            # Instantiate and return
            instance = skill_class(config)
            print(f"✅ Instantiated skill: {name}")
            return instance
            
        except ImportError as e:
            print(f"❌ Failed to import skill module {module_path}: {e}")
            return None
        except Exception as e:
            print(f"❌ Failed to instantiate skill {name}: {e}")
            return None

    def instantiate_all(self) -> dict:
        """
        Instantiate all registered skills.
        
        Returns:
            Dictionary of skill name -> skill instance
        """
        skills = {}
        for name in self.registry.list_skills():
            skill = self.instantiate(name)
            if skill:
                skills[name] = skill
        return skills

    def clear_cache(self):
        """Clear the skill class cache"""
        self._cache = {}
        print("✅ Skill cache cleared")

    def reload_skill(self, name: str) -> Optional[BaseSkill]:
        """
        Reload a skill (clear cache and re-import).
        
        Args:
            name: Skill name
            
        Returns:
            Reloaded skill instance or None
        """
        # Clear from cache
        if name in self._cache:
            del self._cache[name]
        
        # Reload module
        module_path = f"backend.app.skills.{name}.skill"
        if module_path in importlib.sys.modules:
            importlib.reload(importlib.sys.modules[module_path])
        
        # Reinstantiate
        return self.instantiate(name)

