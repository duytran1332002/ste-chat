"""
LLM Service for handling Gemini LLM provider.
"""

from typing import List, Dict
import google.generativeai as genai


class GeminiService:
    """Gemini LLM service implementation."""
    
    def __init__(self, api_key: str, model_name: str, temperature: float = 0.0, max_tokens: int = 2048):
        """
        Initialize Gemini service.
        
        Args:
            api_key: Gemini API key
            model_name: Gemini model name
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = api_key
        if api_key:
            genai.configure(api_key=api_key)
            self._available = True
        else:
            self._available = False
    
    def is_available(self) -> bool:
        """Check if Gemini is available."""
        return self._available
    
    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate response using Gemini API.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Generated response text
        """
        if not self._available:
            raise ValueError("Gemini service not initialized. Check API key.")
        
        model = genai.GenerativeModel(self.model_name)
        
        # Convert messages to Gemini format
        gemini_messages = []
        system_prompt = None
        
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                role = "user" if msg["role"] == "user" else "model"
                gemini_messages.append({"role": role, "parts": [msg["content"]]})
        
        # Add system prompt as first user message if present
        if system_prompt:
            full_messages = [{"role": "user", "parts": [system_prompt]}]
            full_messages.extend(gemini_messages)
        else:
            full_messages = gemini_messages
        
        # Start chat with history
        chat = model.start_chat(history=full_messages[:-1])
        response = chat.send_message(full_messages[-1]["parts"][0])
        
        return response.text


class LLMServiceFactory:
    """Factory for creating Gemini LLM service instances."""
    
    @staticmethod
    def create_service(provider: str, api_key: str, model_name: str, 
                      temperature: float = 0.0, max_tokens: int = 2048) -> GeminiService:
        """
        Create a Gemini LLM service instance.
        
        Args:
            provider: Provider name (should be 'Gemini')
            api_key: Gemini API key
            model_name: Gemini model name
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            
        Returns:
            GeminiService instance
        """
        return GeminiService(api_key, model_name, temperature, max_tokens)
