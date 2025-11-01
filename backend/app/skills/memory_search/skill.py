"""
Memory Search Skill
-------------------
Search the AI memory system.
"""

from backend.app.skills.base import BaseSkill
from backend.app.ai.memory_system import memory_system
from typing import List, Dict, Any


class MemorySearchSkill(BaseSkill):
    """Search the AI memory system for relevant information."""
    
    def execute(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """
        Search memory for relevant information.
        
        Args:
            query: Search query
            k: Number of memories to retrieve
            
        Returns:
            List of relevant memories
        """
        # Validate parameters
        self.validate_params({"query": query, "k": k})
        
        try:
            # Search memory
            results = memory_system.recall(query, k=k)
            
            return results
            
        except Exception as e:
            print(f"❌ Memory search error: {e}")
            return []

