import os
import tempfile
import logging
from typing import Optional
from telegram import Update, Voice
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, ContextTypes
)

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, config, llm_manager, email_manager=None):
        self.config = config
        self.llm_manager = llm_manager
        self.email_manager = email_manager
        self.application = None
        self._setup_bot()

    def _setup_bot(self):
        # Setup Telegram bot
        if not self.config.get('TELEGRAM_TOKEN'):
            logger.error("Telegram token not configured")
            return
        try:
            self.application = (
                Application.builder().token(self.config.get('TELEGRAM_TOKEN')).build()
            )
            # Add handlers
            self.application.add_handler(CommandHandler("start", self._start_command))
            self.application.add_handler(CommandHandler("help", self._help_command))
            self.application.add_handler(CommandHandler("mode", self._mode_command))
            self.application.add_handler(CommandHandler("status", self._status_command))
            self.application.add_handler(CommandHandler("send", self._send_email_command))
            # Add message handlers
            self.application.add_handler(
                MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_text)
            )
            self.application.add_handler(
                MessageHandler(filters.VOICE, self._handle_voice)
            )
            logger.info("Telegram bot setup completed")
        except Exception as e:
            logger.error(f"Error setting up Telegram bot: {e}")

    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = str(update.effective_chat.id)
        allowed = self.config.get('TELEGRAM_CHAT_ID')
        if allowed and chat_id != allowed:
            await update.message.reply_text("❌ Unauthorized user")
            return
        welcome_message = (
            "🤖 Hello Sol! I'm your AI Assistant.\n\n\n"
            "I am designed to help you with your daily tasks and answer any questions you have.\n\n "
            "You can use me both with online and offline mode.\n\n Use /help to view the help menu.\n\n\n"
            "Is there anything I can help you with?"
        )
        await update.message.reply_text(welcome_message)

    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = str(update.effective_chat.id)
        allowed = self.config.get('TELEGRAM_CHAT_ID')
        if allowed and chat_id != allowed:
            await update.message.reply_text("❌ Unauthorized user")
            return
        help_message = (
            "📚 Help\n\n\n"
            "You can ask me anything with text or voice.\n\n"
            "/start: To start the AI assistant\n\n"
            "/status: To check the status of the AI\n\n"
            "/mode online|offline: To toggle between online and offline AI mode\n\n"
            "/help: To view the help menu\n\n"
            "/send mrx@example.com Subject | body: Use this format to send an email through text or say "
            "'Send an email to mrx@example.com subject: Test message: This is a test'\n\n"
        )
        await update.message.reply_text(help_message)

    async def _mode_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = str(update.effective_chat.id)
        allowed = self.config.get('TELEGRAM_CHAT_ID')
        if allowed and chat_id != allowed:
            await update.message.reply_text("❌ Unauthorized user")
            return
        if not context.args:
            current_mode = self.llm_manager.current_mode
            await update.message.reply_text(f"Current mode: {current_mode}")
            return
        mode = context.args[0].lower()
        resp = self.llm_manager.switch_mode(mode)
        await update.message.reply_text(resp)

    async def _status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = str(update.effective_chat.id)
        allowed = self.config.get('TELEGRAM_CHAT_ID')
        if allowed and chat_id != allowed:
            await update.message.reply_text("❌ Unauthorized user")
            return
        status = self.llm_manager.get_status()
        txt = (
            f"Current Mode: {status['current_mode']}\n"
            f"Status: {'working' if status.get('gemini_available') else 'not working'}"
        )
        await update.message.reply_text(txt)

    async def _send_email_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = str(update.effective_chat.id)
        allowed = self.config.get('TELEGRAM_CHAT_ID')
        if allowed and chat_id != allowed:
            await update.message.reply_text("❌ Unauthorized user")
            return
        if not self.email_manager or not self.email_manager.service:
            await update.message.reply_text(
                "❌ Email not configured. Complete Gmail OAuth first."
            )
            return
        try:
            args_text = (update.message.text or '').split(' ', 1)
            if len(args_text) < 2:
                await update.message.reply_text("Usage: /send to@example.com Subject | body")
                return
            payload = args_text[1].strip()
            # Expect: to@example.com Subject | body
            if ' ' not in payload or '|' not in payload:
                await update.message.reply_text("Usage: /send to@example.com Subject | body")
                return
            to_part, rest = payload.split(' ', 1)
            subject_part, body_part = [s.strip() for s in rest.split('|', 1)]
            ok = self.email_manager.send_email(
                to=to_part, subject=subject_part, body=body_part
            )
            await update.message.reply_text(
                "✅ Email sent" if ok else "❌ Failed to send email"
            )
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            await update.message.reply_text("❌ Error sending email")

    async def _handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            chat_id = str(update.effective_chat.id)
            allowed = self.config.get('TELEGRAM_CHAT_ID')
            if allowed and chat_id != allowed:
                await update.message.reply_text("❌ Unauthorized user")
                return
            user_message = update.message.text
            response = self.llm_manager.get_response(user_message, chat_id)
            await update.message.reply_text(response)
        except Exception as e:
            logger.error(f"Error handling text: {e}")
            await update.message.reply_text("❌ Error processing message")

    async def _handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            chat_id = str(update.effective_chat.id)
            allowed = self.config.get('TELEGRAM_CHAT_ID')
            if allowed and chat_id != allowed:
                await update.message.reply_text("❌ Unauthorized user")
                return
            voice: Voice = update.message.voice
            file = await context.bot.get_file(voice.file_id)
            with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as tmp:
                await file.download_to_drive(custom_path=tmp.name)
                voice_path = tmp.name
            from modules.speech_recognition import SpeechRecognition
            sr = SpeechRecognition(self.config)
            transcription = sr.transcribe_voice_message(voice_path)
            os.unlink(voice_path)
            if transcription and not transcription.lower().startswith("error"):
                import re
                logger.info(f"Voice transcription: {transcription}")
                to, subject, body = None, None, None
                # Try main pattern (accepts colon or comma as separator)
                email_pattern = re.compile(
                    r"send an email to ([\w\.-]+@[\w\.-]+)[\s\.,;:]*subject[,:\s]+(.+?)[\s\.,;:]*message[,:\s]+(.+)",
                    re.IGNORECASE | re.DOTALL
                )
                match = email_pattern.search(transcription)
                if not match:
                    # Fallback: look for lines/phrases with comma or colon
                    email_match = re.search(
                        r"send an email to ([\w\.-]+@[\w\.-]+)",
                        transcription, re.IGNORECASE
                    )
                    subject_match = re.search(
                        r"subject[,:\s]+(.+?)(?:message[,:\s]+|$)",
                        transcription, re.IGNORECASE | re.DOTALL
                    )
                    message_match = re.search(
                        r"message[,:\s]+(.+)",
                        transcription, re.IGNORECASE | re.DOTALL
                    )
                    if email_match and subject_match and message_match:
                        to = email_match.group(1).strip()
                        subject = subject_match.group(1).strip().replace('\n', ' ').replace('\r', ' ')
                        body = message_match.group(1).strip()
                else:
                    to = match.group(1).strip()
                    subject = match.group(2).strip().replace('\n', ' ').replace('\r', ' ')
                    body = match.group(3).strip()
                if to and subject and body and self.email_manager and self.email_manager.service:
                    logger.info(f"Parsed email: to={to}, subject={subject}, body={body}")
                    ok = self.email_manager.send_email(
                        to=to, subject=subject, body=body
                    )
                    await update.message.reply_text(
                        f"✅ Email sent to {to}" if ok else "❌ Failed to send email"
                    )
                else:
                    resp = self.llm_manager.get_response(transcription, chat_id)
                    await update.message.reply_text(resp)
            else:
                await update.message.reply_text("Could not transcribe voice note")
        except Exception as e:
            logger.error(f"Error handling voice: {e}")
            await update.message.reply_text("Error processing voice message")

    async def start(self):
        if not self.application:
            logger.error("Telegram bot not properly initialized")
            return
        try:
            logger.info("Starting Telegram bot...")
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            logger.info("Telegram bot started successfully")
        except Exception as e:
            logger.error(f"Error starting Telegram bot: {e}")
            raise

    async def stop(self):
        if self.application:
            try:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
                logger.info("Telegram bot stopped")
            except Exception as e:
                logger.error(f"Error stopping Telegram bot: {e}")

    async def send_message(self, message: str, chat_id: Optional[str] = None):
        # Send a message to a specific chat
        if not self.application:
            return
        target_chat_id = chat_id or self.config.get('TELEGRAM_CHAT_ID')
        if not target_chat_id:
            return
        try:
            await self.application.bot.send_message(
                chat_id=target_chat_id, text=message
            )
        except Exception as e:
            logger.error(f"Error sending message: {e}")



