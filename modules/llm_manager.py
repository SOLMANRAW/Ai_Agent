import requests
import openai
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class LLMManager:
    def __init__(self, config):
        self.config = config
        self.current_mode = config.DEFAULT_MODE
        self.openai_client = None
        self.huggingface_token = getattr(config, 'HUGGINGFACE_TOKEN', None)
        self._setup_openai()
    
    def _setup_openai(self):
        """Initialize OpenAI client"""
        if self.config.OPENAI_API_KEY:
            self.openai_client = openai.OpenAI(api_key=self.config.OPENAI_API_KEY)
    
    def set_mode(self, mode: str):
        """Set the LLM mode (online/offline/huggingface)"""
        if mode not in ["online", "offline", "huggingface"]:
            raise ValueError("Mode must be 'online', 'offline', or 'huggingface'")
        self.current_mode = mode
        logger.info(f"LLM mode set to: {mode}")
    
    def get_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Get response from the current LLM"""
        if self.current_mode == "online":
            return self._get_openai_response(prompt, context)
        elif self.current_mode == "huggingface":
            return self._get_huggingface_response(prompt, context)
        else:
            return self._get_ollama_response(prompt, context)
    
    def _get_openai_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Get response from OpenAI using new v1.0.0 API"""
        try:
            messages = []
            if context:
                messages.append({"role": "system", "content": context})
            messages.append({"role": "user", "content": prompt})
            
            response = self.openai_client.chat.completions.create(
                model=self.config.OPENAI_MODEL,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return f"Error getting OpenAI response: {str(e)}"
    
    def _get_huggingface_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Get response from Hugging Face Inference API"""
        try:
            if not self.huggingface_token:
                return "Hugging Face token not configured. Please add HUGGINGFACE_TOKEN to your .env file"
            
            # Use a free model from Hugging Face
            model_id = "microsoft/DialoGPT-medium"  # Free model
            
            headers = {
                "Authorization": f"Bearer {self.huggingface_token}",
                "Content-Type": "application/json"
            }
            
            # Prepare the full prompt
            full_prompt = prompt
            if context:
                full_prompt = f"Context: {context}\n\nUser: {prompt}"
            
            payload = {
                "inputs": full_prompt,
                "parameters": {
                    "max_length": 1000,
                    "temperature": 0.7,
                    "do_sample": True
                }
            }
            
            response = requests.post(
                f"https://api-inference.huggingface.co/models/{model_id}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "No response generated")
                else:
                    return str(result)
            else:
                return f"Hugging Face API error: {response.status_code} - {response.text}"
                
        except Exception as e:
            logger.error(f"Hugging Face API error: {e}")
            return f"Error getting Hugging Face response: {str(e)}"
    
    def _get_ollama_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Get response from Ollama"""
        try:
            url = f"{self.config.OLLAMA_BASE_URL}/api/generate"
            
            # Prepare the full prompt with context
            full_prompt = prompt
            if context:
                full_prompt = f"Context: {context}\n\nUser: {prompt}\n\nAssistant:"
            
            payload = {
                "model": self.config.OLLAMA_MODEL,
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 1000
                }
            }
            
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "No response from Ollama")
            
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            return f"Error getting Ollama response: {str(e)}"
    
    def get_available_models(self) -> Dict[str, Any]:
        """Get list of available models"""
        models = {
            "online": {
                "current": self.config.OPENAI_MODEL,
                "available": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
            },
            "huggingface": {
                "current": "microsoft/DialoGPT-medium",
                "available": ["microsoft/DialoGPT-medium", "gpt2", "distilgpt2"]
            },
            "offline": {
                "current": self.config.OLLAMA_MODEL,
                "available": []
            }
        }
        
        # Get available Ollama models
        try:
            response = requests.get(f"{self.config.OLLAMA_BASE_URL}/api/tags")
            if response.status_code == 200:
                ollama_models = response.json().get("models", [])
                models["offline"]["available"] = [model["name"] for model in ollama_models]
        except Exception as e:
            logger.error(f"Error getting Ollama models: {e}")
        
        return models


