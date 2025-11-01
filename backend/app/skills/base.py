"""
Base Skill Class
----------------
Abstract base class for all agent skills.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json
from pathlib import Path


class BaseSkill(ABC):
    """Base class for all agent skills"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize skill with configuration.
        
        Args:
            config: Skill configuration from config.json
        """
        self.config = config
        self.name = config.get("name", self.__class__.__name__)
        self.description = config.get("description", "")
        self.version = config.get("version", "1.0.0")
        self.enabled = config.get("enabled", True)
        self.parameters = config.get("parameters", {})
        self.permissions = config.get("permissions", [])
        self.timeout = config.get("timeout", 30)
    
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        """
        Execute the skill.
        
        Args:
            **kwargs: Skill-specific parameters
            
        Returns:
            Skill execution result
        """
        pass
    
    def validate_params(self, params: Dict[str, Any]) -> bool:
        """
        Validate parameters against config schema.
        
        Args:
            params: Parameters to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required parameters
        for param_name, param_config in self.parameters.items():
            if param_config.get("required", False):
                if param_name not in params:
                    raise ValueError(f"Missing required parameter: {param_name}")
        
        # Check parameter types
        for param_name, value in params.items():
            if param_name in self.parameters:
                expected_type = self.parameters[param_name].get("type")
                if expected_type == "string" and not isinstance(value, str):
                    raise TypeError(f"Parameter {param_name} must be string")
                elif expected_type == "integer" and not isinstance(value, int):
                    raise TypeError(f"Parameter {param_name} must be integer")
                elif expected_type == "boolean" and not isinstance(value, bool):
                    raise TypeError(f"Parameter {param_name} must be boolean")
        
        return True
    
    def get_default_params(self) -> Dict[str, Any]:
        """
        Get default parameter values.
        
        Returns:
            Dictionary of default values
        """
        defaults = {}
        for param_name, param_config in self.parameters.items():
            if "default" in param_config:
                defaults[param_name] = param_config["default"]
        return defaults
    
    def check_permissions(self, available_permissions: list) -> bool:
        """
        Check if required permissions are available.
        
        Args:
            available_permissions: List of available permissions
            
        Returns:
            True if all required permissions are available
        """
        return all(perm in available_permissions for perm in self.permissions)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert skill to dictionary representation.
        
        Returns:
            Skill metadata dictionary
        """
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "enabled": self.enabled,
            "parameters": self.parameters,
            "permissions": self.permissions,
            "timeout": self.timeout
        }
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', version='{self.version}')>"

