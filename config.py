import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Telegram Bot Configuration
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    
    # Gemini Configuration
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')
    
    # Ollama Configuration
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = "mistral:7b"
    
    # Gmail Configuration
    GMAIL_CREDENTIALS_FILE = os.getenv('GMAIL_CREDENTIALS_FILE', 'credentials.json')
    GMAIL_TOKEN_FILE = os.getenv('GMAIL_TOKEN_FILE', 'token.json')
    
    # Whisper Configuration
    WHISPER_MODEL_PATH = os.getenv('WHISPER_MODEL_PATH', 'models/ggml-large-v3-turbo-q5_0.bin')
    WHISPER_CPP_PATH = os.getenv('WHISPER_CPP_PATH', './whisper.cpp')
    WHISPER_EXECUTABLE = os.getenv('WHISPER_EXECUTABLE', './whisper.cpp/build/bin/whisper-cli')
    
    # Hotkey Configuration
    HOTKEY_COMBINATION = ['ctrl', 'alt', 'a']  # Ctrl+Alt+A
    
    # File Search Configuration
    SEARCH_PATHS = [
        os.path.expanduser("~/Documents"),
        os.path.expanduser("~/Downloads"),
        os.path.expanduser("~/Desktop"),
        os.path.expanduser("~/Pictures"),
        os.path.expanduser("~/Music"),
        os.path.expanduser("~/Videos")
    ]
    
    # Agent Configuration
    DEFAULT_MODE = "gemini"  # Use Google Gemini
    MAX_FILE_SEARCH_RESULTS = 10
    MAX_EMAIL_RESULTS = 5
    
    # Audio Configuration
    AUDIO_SAMPLE_RATE = 16000
    AUDIO_CHANNELS = 1
    AUDIO_FORMAT = "wav"
    
    def get(self, key, default=None):
        # Get configuration value with optional default
        return getattr(self, key, default)

    @classmethod
    def validate(cls):
        # Validate that all required configuration is present
        required_vars = [
            'TELEGRAM_TOKEN'
        ]
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}"
            )
        return True
