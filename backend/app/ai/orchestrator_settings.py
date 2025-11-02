"""
Orchestrator Settings
--------------------
Manage orchestrator configuration and runtime settings.

Settings include:
- Agent scraping permissions
- Skill approval policies
- Memory tier preferences
- Logging levels
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


class OrchestratorSettings:
    """Manage orchestrator settings with persistence."""
    
    DEFAULT_SETTINGS = {
        "allow_agent_scrape": False,  # Require explicit user approval
        "auto_approve_skills": False,  # Skills disabled by default
        "default_memory_tier": "MT",  # Mid-term by default
        "log_level": "INFO",
        "max_concurrent_agents": 10,
        "skill_timeout": 30,  # seconds
        "research_cache_ttl": 86400,  # 24 hours
        "enable_audit_log": True,
        "auto_save_research": True,
        "pdf_generation": "auto",  # auto, weasyprint, md-to-pdf, disabled
    }
    
    def __init__(self, settings_file: str = "backend/app/ai/orchestrator_settings.json"):
        """
        Initialize settings manager.
        
        Args:
            settings_file: Path to settings JSON file
        """
        self.settings_file = Path(settings_file)
        self.settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        """
        Load settings from file or create with defaults.
        
        Returns:
            Settings dictionary
        """
        if self.settings_file.exists():
            try:
                settings = json.loads(self.settings_file.read_text())
                # Merge with defaults (in case new settings were added)
                merged = self.DEFAULT_SETTINGS.copy()
                merged.update(settings)
                print(f"✅ Loaded settings from {self.settings_file}")
                return merged
            except Exception as e:
                print(f"⚠️  Failed to load settings: {e}, using defaults")
                return self.DEFAULT_SETTINGS.copy()
        else:
            # Create settings file with defaults
            self.settings_file.parent.mkdir(parents=True, exist_ok=True)
            self.settings_file.write_text(json.dumps(self.DEFAULT_SETTINGS, indent=2))
            print(f"✅ Created default settings: {self.settings_file}")
            return self.DEFAULT_SETTINGS.copy()
    
    def save(self) -> bool:
        """
        Save current settings to file.
        
        Returns:
            True if successful
        """
        try:
            self.settings_file.write_text(json.dumps(self.settings, indent=2))
            print(f"✅ Settings saved to {self.settings_file}")
            return True
        except Exception as e:
            print(f"❌ Failed to save settings: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value.
        
        Args:
            key: Setting key
            default: Default value if key not found
            
        Returns:
            Setting value
        """
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any, save: bool = True) -> bool:
        """
        Set a setting value.
        
        Args:
            key: Setting key
            value: Setting value
            save: Whether to save to file immediately
            
        Returns:
            True if successful
        """
        self.settings[key] = value
        
        if save:
            return self.save()
        
        return True
    
    def update(self, updates: Dict[str, Any], save: bool = True) -> bool:
        """
        Update multiple settings.
        
        Args:
            updates: Dictionary of settings to update
            save: Whether to save to file immediately
            
        Returns:
            True if successful
        """
        self.settings.update(updates)
        
        if save:
            return self.save()
        
        return True
    
    def reset(self, save: bool = True) -> bool:
        """
        Reset all settings to defaults.
        
        Args:
            save: Whether to save to file immediately
            
        Returns:
            True if successful
        """
        self.settings = self.DEFAULT_SETTINGS.copy()
        
        if save:
            return self.save()
        
        return True
    
    def get_all(self) -> Dict[str, Any]:
        """
        Get all settings.
        
        Returns:
            Settings dictionary
        """
        return self.settings.copy()
    
    def is_agent_scrape_allowed(self) -> bool:
        """
        Check if agent scraping is allowed.
        
        Returns:
            True if allowed
        """
        return self.get("allow_agent_scrape", False)
    
    def enable_agent_scrape(self, enabled: bool = True) -> bool:
        """
        Enable or disable agent scraping.
        
        Args:
            enabled: Whether to enable agent scraping
            
        Returns:
            True if successful
        """
        return self.set("allow_agent_scrape", enabled)
    
    def is_auto_approve_skills(self) -> bool:
        """
        Check if skills are auto-approved.
        
        Returns:
            True if auto-approve is enabled
        """
        return self.get("auto_approve_skills", False)
    
    def enable_auto_approve_skills(self, enabled: bool = True) -> bool:
        """
        Enable or disable auto-approval of skills.
        
        Args:
            enabled: Whether to enable auto-approval
            
        Returns:
            True if successful
        """
        return self.set("auto_approve_skills", enabled)
    
    def get_default_memory_tier(self) -> str:
        """
        Get default memory tier.
        
        Returns:
            Memory tier (ST, MT, LT_HOT, FV)
        """
        return self.get("default_memory_tier", "MT")
    
    def set_default_memory_tier(self, tier: str) -> bool:
        """
        Set default memory tier.
        
        Args:
            tier: Memory tier (ST, MT, LT_HOT, FV)
            
        Returns:
            True if successful
        """
        valid_tiers = ["ST", "MT", "LT_HOT", "FV"]
        if tier not in valid_tiers:
            print(f"❌ Invalid tier: {tier}. Must be one of {valid_tiers}")
            return False
        
        return self.set("default_memory_tier", tier)
    
    def __repr__(self) -> str:
        """String representation."""
        return f"OrchestratorSettings({len(self.settings)} settings)"

