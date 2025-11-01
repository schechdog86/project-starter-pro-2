"""
LLM Service
-----------
Unified interface for multiple LLM providers using LiteLLM.

Supports:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- DeepSeek
- Any LiteLLM-supported provider
"""

from typing import Optional, List, Dict
from backend.app.core.config import settings
from backend.app.ai import AI_REGISTRY


class LLMService:
    """Unified LLM service using LiteLLM."""
    
    def __init__(self):
        self.litellm = AI_REGISTRY["core"].get("litellm")
        if not self.litellm:
            raise RuntimeError("LiteLLM not available. Install with: pip install litellm")
    
    def chat(
        self,
        message: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Send a chat message to an LLM.
        
        Args:
            message: User message
            provider: LLM provider (openai, anthropic, deepseek)
            model: Specific model name (overrides provider default)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum response tokens
            
        Returns:
            LLM response text
        """
        provider = provider or settings.MODEL_PROVIDER
        
        # Select model and API key based on provider
        if model:
            selected_model = model
        elif provider == "openai":
            selected_model = "gpt-4"
        elif provider == "anthropic":
            selected_model = "claude-3-opus-20240229"
        elif provider == "deepseek":
            selected_model = "deepseek-chat"
        else:
            selected_model = "gpt-3.5-turbo"
        
        # Get API key
        if provider == "openai":
            api_key = settings.OPENAI_API_KEY
        elif provider == "anthropic":
            api_key = settings.ANTHROPIC_API_KEY
        elif provider == "deepseek":
            api_key = settings.DEEPSEEK_API_KEY
        else:
            api_key = settings.OPENAI_API_KEY
        
        # Call LiteLLM
        response = self.litellm.completion(
            model=selected_model,
            messages=[{"role": "user", "content": message}],
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    def chat_with_history(
        self,
        messages: List[Dict[str, str]],
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Chat with conversation history.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            provider: LLM provider
            model: Specific model name
            temperature: Sampling temperature
            max_tokens: Maximum response tokens
            
        Returns:
            LLM response text
        """
        provider = provider or settings.MODEL_PROVIDER
        
        # Select model
        if model:
            selected_model = model
        elif provider == "openai":
            selected_model = "gpt-4"
        elif provider == "anthropic":
            selected_model = "claude-3-opus-20240229"
        elif provider == "deepseek":
            selected_model = "deepseek-chat"
        else:
            selected_model = "gpt-3.5-turbo"
        
        # Get API key
        if provider == "openai":
            api_key = settings.OPENAI_API_KEY
        elif provider == "anthropic":
            api_key = settings.ANTHROPIC_API_KEY
        elif provider == "deepseek":
            api_key = settings.DEEPSEEK_API_KEY
        else:
            api_key = settings.OPENAI_API_KEY
        
        # Call LiteLLM
        response = self.litellm.completion(
            model=selected_model,
            messages=messages,
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    def stream_chat(
        self,
        message: str,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ):
        """
        Stream chat responses.
        
        Args:
            message: User message
            provider: LLM provider
            model: Specific model name
            temperature: Sampling temperature
            max_tokens: Maximum response tokens
            
        Yields:
            Response chunks
        """
        provider = provider or settings.MODEL_PROVIDER
        
        # Select model
        if model:
            selected_model = model
        elif provider == "openai":
            selected_model = "gpt-4"
        elif provider == "anthropic":
            selected_model = "claude-3-opus-20240229"
        elif provider == "deepseek":
            selected_model = "deepseek-chat"
        else:
            selected_model = "gpt-3.5-turbo"
        
        # Get API key
        if provider == "openai":
            api_key = settings.OPENAI_API_KEY
        elif provider == "anthropic":
            api_key = settings.ANTHROPIC_API_KEY
        elif provider == "deepseek":
            api_key = settings.DEEPSEEK_API_KEY
        else:
            api_key = settings.OPENAI_API_KEY
        
        # Stream response
        response = self.litellm.completion(
            model=selected_model,
            messages=[{"role": "user", "content": message}],
            api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


# Singleton instance
llm_service = LLMService()

