"""
Code Analysis Skill
-------------------
Analyze code using LLM.
"""

from backend.app.skills.base import BaseSkill
from backend.app.ai.llm_service import llm_service
from typing import Dict, Any


class CodeAnalysisSkill(BaseSkill):
    """Analyze code for quality, security, and best practices."""
    
    def execute(self, code: str, language: str = "python") -> Dict[str, Any]:
        """
        Analyze code.
        
        Args:
            code: Code to analyze
            language: Programming language
            
        Returns:
            Analysis results
        """
        # Validate parameters
        self.validate_params({"code": code, "language": language})
        
        try:
            # Create analysis prompt
            prompt = f"""Analyze the following {language} code for:
1. Code quality and readability
2. Security vulnerabilities
3. Best practices
4. Potential bugs
5. Performance issues

Code:
```{language}
{code}
```

Provide a structured analysis with specific recommendations."""
            
            # Get LLM analysis
            analysis = llm_service.chat(prompt, temperature=0.3, max_tokens=2000)
            
            return {
                "language": language,
                "code_length": len(code),
                "analysis": analysis
            }
            
        except Exception as e:
            print(f"❌ Code analysis error: {e}")
            return {
                "error": str(e)
            }

