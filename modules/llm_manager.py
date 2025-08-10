import logging
from typing import Optional, Dict, Any
import google.generativeai as genai

logger = logging.getLogger(__name__)

class LLMManager:
    def __init__(self, config):
        self.config = config
        self.current_mode = "Gemini - Online Mode"
        self.model_name = config.get('GEMINI_MODEL', 'gemini-1.5-flash')
        api_key = config.get('GEMINI_API_KEY')
        if not api_key:
            logging.warning("GEMINI_API_KEY not set; responses will use fallback text")
            self.client = None
        else:
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(self.model_name)
        logging.info(f"🤖 LLM Manager initialized in {self.current_mode} mode (model={self.model_name})")

    def get_response(self, prompt: str, user_id: str = None) -> str:
        try:
            if not self.client:
                return self._fallback_reply(prompt)
            resp = self.client.generate_content(prompt)
            if hasattr(resp, 'text') and resp.text:
                return resp.text
            return self._fallback_reply(prompt)
        except Exception as e:
            logging.error(f"Gemini error: {e}")
            return self._fallback_reply(prompt)

    def _fallback_reply(self, prompt: str) -> str:
        p = prompt.strip().lower()
        if any(x in p for x in ["hello", "hi", "hey"]):
            return "Hello! I'm online. Add GEMINI_API_KEY to your .env for full AI responses."
        return "Temporarily unable to reach Gemini. Please set GEMINI_API_KEY and try again."

    def switch_mode(self, mode: str) -> str:
        return "❌ Only Gemini mode is enabled."

    def get_status(self) -> Dict[str, Any]:
        return {
            "current_mode": self.current_mode,
            "openai_available": False,
            "huggingface_available": False,
            "ollama_available": False,
            "gemini_available": self.client is not None
        }


