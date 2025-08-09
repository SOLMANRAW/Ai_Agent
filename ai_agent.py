import logging
import os
import sys
from typing import Dict, Any
import asyncio
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from modules.llm_manager import LLMManager
from modules.telegram_bot import TelegramBot
from modules.file_search import FileSearch
from modules.speech_recognition import SpeechRecognition
from modules.email_manager import EmailManager
from modules.hotkey_manager import HotkeyManager

class AIAgent:
    def __init__(self):
        """Initialize the AI Agent with all modules"""
        self.config = Config()
        self.setup_logging()
        
        # Initialize modules
        self.llm_manager = LLMManager(self.config)
        self.file_search = FileSearch(self.config)
        self.speech_recognition = SpeechRecognition(self.config)
        self.email_manager = EmailManager(self.config) if self.config.get('GMAIL_CREDENTIALS_FILE') else None
        self.telegram_bot = TelegramBot(self.config, self.llm_manager, self.email_manager)
        self.hotkey_manager = HotkeyManager(self.config, self._hotkey_activation)
        
        logging.info("🤖 AI Agent initialized successfully!")

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('ai_agent.log'),
                logging.StreamHandler()
            ]
        )

    def _hotkey_activation(self):
        """Handle hotkey activation for voice input"""
        try:
            logging.info("🎤 Hotkey activated - starting voice recording")
            
            # Record and transcribe
            transcription = self.speech_recognition.record_and_transcribe(duration=10)
            
            if transcription and transcription != "Error recording and transcribing":
                logging.info(f"🎤 Transcription: {transcription}")
                
                # Process the transcription with LLM
                response = self.llm_manager.get_response(transcription)
                logging.info(f"🤖 Response: {response}")
            else:
                logging.error("❌ Failed to transcribe hotkey activation")
                
        except Exception as e:
            logging.error(f"❌ Error in hotkey activation: {e}")

    async def start(self):
        """Start all AI Agent services"""
        try:
            logging.info("🚀 Starting AI Agent...")
            
            # Start Telegram bot
            await self.telegram_bot.start()
            
            # Start hotkey manager
            self.hotkey_manager.start()
            
            logging.info("✅ AI Agent is running!")
            logging.info("📱 Telegram bot: @DgPsmbot")
            logging.info("⌨️  Hotkey: Ctrl+Alt+A")
            logging.info("🔄 Mode: " + self.llm_manager.current_mode)
            
            # Keep the agent running
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logging.info("🛑 Shutting down AI Agent...")
            await self.telegram_bot.stop()
            self.hotkey_manager.stop()
        except Exception as e:
            logging.error(f"❌ Error in AI Agent: {e}")
            await self.telegram_bot.stop()
            self.hotkey_manager.stop()

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all modules"""
        status = {
            "agent_status": "running",
            "timestamp": datetime.now().isoformat(),
            "llm_status": self.llm_manager.get_status(),
            "telegram_status": "connected" if self.telegram_bot else "disconnected",
            "file_search": "available",
            "speech_recognition": "available" if self.speech_recognition else "unavailable",
            "email_manager": "available" if self.email_manager else "unavailable",
            "hotkey_manager": "active" if self.hotkey_manager else "inactive"
        }
        return status

if __name__ == "__main__":
    agent = AIAgent()
    asyncio.run(agent.start())



