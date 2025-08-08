import asyncio
import logging
import re
from typing import Dict, Any, Optional
import threading

from config import Config
from modules.llm_manager import LLMManager
from modules.speech_recognition import SpeechRecognition
from modules.file_search import FileSearch
from modules.email_manager import EmailManager
from modules.telegram_bot import TelegramBot
from modules.hotkey_manager import HotkeyManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AIAgent:
    def __init__(self):
        self.config = Config()
        self.config.validate()
        
        # Initialize modules
        self.llm_manager = LLMManager(self.config)
        self.speech_recognition = SpeechRecognition(self.config)
        self.file_search = FileSearch(self.config)
        self.email_manager = EmailManager(self.config)
        
        # Initialize bot and hotkey manager
        self.telegram_bot = TelegramBot(self.config, self)
        self.hotkey_manager = HotkeyManager(self.config, self._hotkey_activation)
        
        # System state
        self.is_running = False
        
        logger.info("AI Agent initialized successfully")
    
    def start(self):
        """Start the AI agent"""
        try:
            self.is_running = True
            
            # Start hotkey manager
            self.hotkey_manager.start()
            
            # Start Telegram bot
            self.telegram_bot.start()
            
            logger.info("AI Agent started successfully")
            
        except Exception as e:
            logger.error(f"Error starting AI Agent: {e}")
            self.is_running = False
    
    def stop(self):
        """Stop the AI agent"""
        self.is_running = False
        self.hotkey_manager.stop()
        self.telegram_bot.stop()
        logger.info("AI Agent stopped")
    
    def _hotkey_activation(self):
        """Handle hotkey activation"""
        logger.info("Hotkey activated - starting voice recording")
        
        # Record and transcribe
        transcription = self.speech_recognition.record_and_transcribe(duration=10)
        
        if transcription and transcription != "Error recording and transcribing":
            logger.info(f"Transcription: {transcription}")
            
            # Process the transcription
            asyncio.run(self.process_text_message(transcription))
        else:
            logger.error("Failed to transcribe hotkey activation")
    
    async def process_text_message(self, message: str) -> str:
        """Process a text message and return response"""
        try:
            # Parse the message for specific commands
            response = await self._parse_and_execute(message)
            
            # If no specific command was executed, use LLM for general response
            if not response:
                response = self.llm_manager.get_response(
                    message,
                    context="You are a helpful AI assistant. Provide concise and helpful responses."
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing text message: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    async def _parse_and_execute(self, message: str) -> Optional[str]:
        """Parse message for specific commands and execute them"""
        message_lower = message.lower()
        
        # File search commands
        if any(keyword in message_lower for keyword in ['search', 'find', 'look for']):
            return await self._handle_file_search(message)
        
        # Email commands
        elif any(keyword in message_lower for keyword in ['email', 'mail', 'gmail']):
            return await self._handle_email_commands(message)
        
        # System commands
        elif any(keyword in message_lower for keyword in ['mode', 'status', 'help']):
            return await self._handle_system_commands(message)
        
        return None
    
    async def _handle_file_search(self, message: str) -> str:
        """Handle file search requests"""
        try:
            # Extract search query
            search_patterns = [
                r'search for (.+)',
                r'find (.+)',
                r'look for (.+)',
                r'find all (.+) files',
                r'search (.+)'
            ]
            
            query = None
            for pattern in search_patterns:
                match = re.search(pattern, message.lower())
                if match:
                    query = match.group(1)
                    break
            
            if not query:
                return "Please specify what you want to search for. For example: 'search for documents'"
            
            # Perform search
            results = self.file_search.search_files(query)
            
            if results:
                formatted_results = self.file_search.format_search_results(results)
                return f"Found {len(results)} files:\n\n{formatted_results}"
            else:
                return f"No files found matching '{query}'"
                
        except Exception as e:
            logger.error(f"Error in file search: {e}")
            return f"Error searching files: {str(e)}"
    
    async def _handle_email_commands(self, message: str) -> str:
        """Handle email-related commands"""
        try:
            message_lower = message.lower()
            
            # Check emails
            if any(keyword in message_lower for keyword in ['check email', 'read email', 'show email', 'check mail']):
                emails = self.email_manager.get_recent_emails(max_results=5)
                if emails:
                    summary = self.email_manager.format_emails_summary(emails)
                    return f"Recent emails:\n\n{summary}"
                else:
                    return "No recent emails found."
            
            # Send email
            elif 'send email' in message_lower or 'compose email' in message_lower:
                # This would need more sophisticated parsing for email composition
                return "Email composition not yet implemented. Please use the web interface for now."
            
            # Search emails
            elif 'search email' in message_lower:
                # Extract search query
                match = re.search(r'search email (.+)', message_lower)
                if match:
                    query = match.group(1)
                    emails = self.email_manager.search_emails(query, max_results=5)
                    if emails:
                        summary = self.email_manager.format_emails_summary(emails)
                        return f"Email search results for '{query}':\n\n{summary}"
                    else:
                        return f"No emails found matching '{query}'"
                else:
                    return "Please specify what to search for in emails."
            
            else:
                return "Email commands: 'check emails', 'search email [query]', 'send email'"
                
        except Exception as e:
            logger.error(f"Error in email commands: {e}")
            return f"Error processing email command: {str(e)}"
    
    async def _handle_system_commands(self, message: str) -> str:
        """Handle system-related commands"""
        message_lower = message.lower()
        
        if 'status' in message_lower:
            return self.get_system_status()
        
        elif 'mode' in message_lower:
            if 'online' in message_lower:
                self.llm_manager.set_mode("online")
                return "Switched to online mode (OpenAI)"
            elif 'offline' in message_lower:
                self.llm_manager.set_mode("offline")
                return "Switched to offline mode (Ollama)"
            else:
                current_mode = self.llm_manager.current_mode
                return f"Current mode: {current_mode}. Use 'switch to online/offline mode'"
        
        elif 'help' in message_lower:
            return self._get_help_message()
        
        return None
    
    def get_system_status(self) -> str:
        """Get system status information"""
        status_parts = []
        
        # LLM Status
        llm_status = f"🤖 LLM: {self.llm_manager.current_mode.upper()}"
        status_parts.append(llm_status)
        
        # Whisper Status
        whisper_status = "🎤 Whisper: ✅ Available" if self.speech_recognition.is_whisper_available() else "🎤 Whisper: ❌ Not available"
        status_parts.append(whisper_status)
        
        # Email Status
        email_status = "📧 Email: ✅ Connected" if self.email_manager.is_authenticated() else "📧 Email: ❌ Not connected"
        status_parts.append(email_status)
        
        # Hotkey Status
        hotkey_status = "⌨️ Hotkey: ✅ Active" if self.hotkey_manager.is_listening() else "⌨️ Hotkey: ❌ Inactive"
        status_parts.append(hotkey_status)
        
        # Telegram Status
        telegram_status = "📱 Telegram: ✅ Active" if self.telegram_bot.application else "📱 Telegram: ❌ Inactive"
        status_parts.append(telegram_status)
        
        # Hotkey combination
        hotkey_combo = self.hotkey_manager.get_current_combination()
        status_parts.append(f"🔑 Hotkey: {hotkey_combo}")
        
        return "\n".join(status_parts)
    
    def _get_help_message(self) -> str:
        """Get help message"""
        return (
            "🤖 **AI Assistant Help**\n\n"
            "**File Operations:**\n"
            "• 'Search for [filename]' - Find files\n"
            "• 'Find all PDF files' - Search by type\n"
            "• 'Look for documents' - General search\n\n"
            "**Email Operations:**\n"
            "• 'Check emails' - Read recent emails\n"
            "• 'Search email [query]' - Search emails\n"
            "• 'Send email' - Compose email\n\n"
            "**System Commands:**\n"
            "• 'Switch to online mode' - Use OpenAI\n"
            "• 'Switch to offline mode' - Use Ollama\n"
            "• 'System status' - Check status\n"
            "• 'Help' - Show this help\n\n"
            "**Voice Commands:**\n"
            "• Press Ctrl+Alt+A to activate voice input\n"
            "• Send voice messages via Telegram\n\n"
            "**Examples:**\n"
            "• 'Search for my documents'\n"
            "• 'Check recent emails'\n"
            "• 'What's the weather like?'\n"
            "• 'Switch to online mode'"
        )

def main():
    """Main function to run the AI agent"""
    try:
        agent = AIAgent()
        agent.start()
        
        # Keep the main thread alive
        try:
            while agent.is_running:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            agent.stop()
            
    except Exception as e:
        logger.error(f"Error in main: {e}")

if __name__ == "__main__":
    main()



