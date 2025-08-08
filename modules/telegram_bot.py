import os
import tempfile
import logging
from typing import Optional
from telegram import Update, Voice
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, config, ai_agent):
        self.config = config
        self.ai_agent = ai_agent
        self.application = None
        self._setup_bot()
    
    def _setup_bot(self):
        """Setup Telegram bot"""
        if not self.config.TELEGRAM_TOKEN:
            logger.error("Telegram token not configured")
            return
        
        try:
            self.application = Application.builder().token(self.config.TELEGRAM_TOKEN).build()
            
            # Add handlers
            self.application.add_handler(CommandHandler("start", self._start_command))
            self.application.add_handler(CommandHandler("help", self._help_command))
            self.application.add_handler(CommandHandler("mode", self._mode_command))
            self.application.add_handler(CommandHandler("status", self._status_command))
            
            # Add message handlers
            self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_text))
            self.application.add_handler(MessageHandler(filters.VOICE, self._handle_voice))
            
            logger.info("Telegram bot setup completed")
            
        except Exception as e:
            logger.error(f"Error setting up Telegram bot: {e}")
    
    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = (
            "🤖 Hello! I'm your AI Assistant.\n\n"
            "I can help you with:\n"
            "• File search and management\n"
            "• Email reading and sending\n"
            "• Voice and text processing\n"
            "• General questions and tasks\n\n"
            "Send me a message or voice note to get started!\n\n"
            "Commands:\n"
            "/help - Show this help\n"
            "/mode - Switch between online/offline\n"
            "/status - Check system status"
        )
        await update.message.reply_text(welcome_message)
    
    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = (
            "📚 **AI Assistant Help**\n\n"
            "**Text Commands:**\n"
            "• Ask questions or give instructions\n"
            "• 'Search for file X' - Find files\n"
            "• 'Check emails' - Read recent emails\n"
            "• 'Send email to X' - Compose email\n\n"
            "**Voice Commands:**\n"
            "• Send voice messages for hands-free operation\n"
            "• Voice will be transcribed and processed\n\n"
            "**System Commands:**\n"
            "/mode online - Use OpenAI\n"
            "/mode offline - Use local Ollama\n"
            "/status - System status\n"
            "/help - This help\n\n"
            "**Examples:**\n"
            "• 'Find all PDF files'\n"
            "• 'Show recent emails'\n"
            "• 'Send email to john@example.com'\n"
            "• 'What's the weather like?'"
        )
        await update.message.reply_text(help_message, parse_mode='Markdown')
    
    async def _mode_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /mode command"""
        if not context.args:
            current_mode = self.ai_agent.llm_manager.current_mode
            await update.message.reply_text(f"Current mode: {current_mode}\nUse: /mode online or /mode offline")
            return
        
        mode = context.args[0].lower()
        if mode not in ["online", "offline"]:
            await update.message.reply_text("Invalid mode. Use 'online' or 'offline'")
            return
        
        try:
            self.ai_agent.llm_manager.set_mode(mode)
            await update.message.reply_text(f"✅ Switched to {mode} mode")
        except Exception as e:
            await update.message.reply_text(f"❌ Error switching mode: {str(e)}")
    
    async def _status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        status = self.ai_agent.get_system_status()
        await update.message.reply_text(status)
    
    async def _handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        try:
            user_message = update.message.text
            user_id = update.effective_user.id
            
            # Check if user is authorized
            if self.config.TELEGRAM_CHAT_ID and str(user_id) != self.config.TELEGRAM_CHAT_ID:
                await update.message.reply_text("❌ Unauthorized access")
                return
            
            logger.info(f"Received text message from {user_id}: {user_message}")
            
            # Send typing indicator
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
            # Process with AI agent
            response = await self.ai_agent.process_text_message(user_message)
            
            # Send response
            await update.message.reply_text(response)
            
        except Exception as e:
            logger.error(f"Error handling text message: {e}")
            await update.message.reply_text(f"❌ Error processing message: {str(e)}")
    
    async def _handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice messages"""
        try:
            user_id = update.effective_user.id
            
            # Check if user is authorized
            if self.config.TELEGRAM_CHAT_ID and str(user_id) != self.config.TELEGRAM_CHAT_ID:
                await update.message.reply_text("❌ Unauthorized access")
                return
            
            voice: Voice = update.message.voice
            logger.info(f"Received voice message from {user_id}")
            
            # Send typing indicator
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
            # Download voice file
            voice_file = await context.bot.get_file(voice.file_id)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as temp_file:
                await voice_file.download_to_drive(temp_file.name)
                temp_path = temp_file.name
            
            try:
                # Transcribe voice message
                transcription = self.ai_agent.speech_recognition.transcribe_voice_message(temp_path)
                
                if transcription and transcription != "Error transcribing voice message":
                    # Send transcription
                    await update.message.reply_text(f"🎤 **Transcription:** {transcription}")
                    
                    # Process with AI agent
                    response = await self.ai_agent.process_text_message(transcription)
                    await update.message.reply_text(response)
                else:
                    await update.message.reply_text("❌ Could not transcribe voice message")
                    
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            logger.error(f"Error handling voice message: {e}")
            await update.message.reply_text(f"❌ Error processing voice message: {str(e)}")
    
    def start(self):
        """Start the Telegram bot"""
        if not self.application:
            logger.error("Telegram bot not properly initialized")
            return
        
        try:
            logger.info("Starting Telegram bot...")
            self.application.run_polling(allowed_updates=Update.ALL_TYPES)
        except Exception as e:
            logger.error(f"Error starting Telegram bot: {e}")
    
    async def send_message(self, message: str, chat_id: Optional[str] = None):
        """Send a message to Telegram"""
        if not self.application:
            return
        
        try:
            target_chat_id = chat_id or self.config.TELEGRAM_CHAT_ID
            if target_chat_id:
                await self.application.bot.send_message(chat_id=target_chat_id, text=message)
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
    
    def stop(self):
        """Stop the Telegram bot"""
        if self.application:
            self.application.stop()
            logger.info("Telegram bot stopped")



