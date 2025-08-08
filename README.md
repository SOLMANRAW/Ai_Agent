# 🤖 AI Agent

A comprehensive AI assistant that can search files, manage emails, process voice commands, and run both online (Gemini) and offline (Ollama) language models.

## ✨ Features

- **🔍 File Search**: Search for files across your device with natural language
- **📧 Email Management**: Read and send emails through Gmail integration
- **🎤 Voice Recognition**: Process voice commands using Whisper.cpp
- **🤖 Dual LLM Support**: Toggle between Gemini (online) and Ollama Mistral 7B (offline)
- **📱 Telegram Bot**: Interact via Telegram with voice and text messages
- **⌨️ Hotkey Activation**: Global hotkey (Ctrl+Alt+A) for voice input
- **🔒 Privacy**: Run completely offline with local models

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Git
- Ollama (for offline mode)
- Telegram Bot Token
- Gemini API Key (for online mode)


### Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd Ai_Agent
   ```

2. **Run the setup script**:
   ```bash
   ./setup.sh
   ```

3. **Configure your environment**:
   ```bash
   # Edit the .env file with your API keys
   nano .env
   ```

4. **Download Whisper model**:
   ```bash
   wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo-q5_0.bin -O models/ggml-large-v3-turbo-q5_0.bin
   ```

5. **Build Whisper.cpp**:
   ```bash
   cd whisper.cpp && make
   cd ..
   ```

6. **Install Ollama and pull model**:
   ```bash
   # Install Ollama from https://ollama.ai
   ollama pull mistral:7b
   ```

7. **Run the AI Agent**:
   ```bash
   python ai_agent.py
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Telegram Bot Configuration
TELEGRAM_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Ollama Configuration (optional)
OLLAMA_BASE_URL=http://localhost:11434

# Gmail Configuration (optional)
GMAIL_CREDENTIALS_FILE=credentials.json
GMAIL_TOKEN_FILE=token.json

# Whisper Configuration (optional)
WHISPER_MODEL_PATH=models/ggml-large-v3-turbo-q5_0.bin
WHISPER_CPP_PATH=./whisper.cpp
```

### Getting API Keys

#### Telegram Bot
1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create a new bot with `/newbot`
3. Get your bot token and chat ID

#### OpenAI
1. Sign up at [OpenAI](https://openai.com)
2. Get your API key from the dashboard

#### Gmail (Optional)
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a project and enable Gmail API
3. Download `credentials.json`

## 🎯 Usage

### Telegram Commands

- `/start` - Initialize the bot
- `/help` - Show help information
- `/mode online` - Switch to OpenAI
- `/mode offline` - Switch to Ollama
- `/status` - Check system status

### Voice Commands

- Press **Ctrl+Alt+A** for hotkey activation
- Send voice messages via Telegram
- Natural language processing for all commands

### Text Commands

#### File Operations
- "Search for documents"
- "Find all PDF files"
- "Look for my photos"

#### Email Operations
- "Check emails"
- "Search email from John"
- "Show recent emails"

#### System Commands
- "Switch to online mode"
- "Switch to offline mode"
- "System status"
- "Help"

### Examples

```
User: "Search for my resume"
Bot: "Found 2 files:
1. resume.pdf (245KB) - /home/user/Documents/resume.pdf
2. resume_updated.pdf (312KB) - /home/user/Downloads/resume_updated.pdf"

User: "Check emails"
Bot: "Recent emails:
1. From: john@example.com
   Subject: Meeting Tomorrow
   Date: 2024-01-15
   Snippet: Hi, let's meet tomorrow at 2 PM..."

User: "What's the weather like?"
Bot: "I don't have access to real-time weather data, but I can help you with file searches, emails, and other tasks!"
```

>>>>>>> 252d052 (Add comprehensive AI agent with Telegram bot, OpenAI/HuggingFace integration, file search, and voice recognition)
## 🏗️ Architecture

```
AI Agent
├── LLM Manager (Gemini/Ollama)
├── Speech Recognition (Whisper.cpp)
├── File Search Module
├── Email Manager (Gmail)
├── Telegram Bot
└── Hotkey Manager
```

### Modules

- **`llm_manager.py`**: Handles Gemini and Ollama integration
- **`speech_recognition.py`**: Whisper.cpp integration for voice transcription
- **`file_search.py`**: File system search and management
- **`email_manager.py`**: Gmail API integration
- **`telegram_bot.py`**: Telegram bot interface
- **`hotkey_manager.py`**: Global hotkey management

## 🔧 Development

### Project Structure

```
Ai_Agent/
├── ai_agent.py          # Main AI agent class
├── config.py            # Configuration management
├── requirements.txt     # Python dependencies
├── setup.sh            # Setup script
├── modules/            # Core modules
│   ├── __init__.py
│   ├── llm_manager.py
│   ├── speech_recognition.py
│   ├── file_search.py
│   ├── email_manager.py
│   ├── telegram_bot.py
│   └── hotkey_manager.py
├── whisper.cpp/        # Whisper.cpp library
├── models/             # AI models
└── .env               # Environment variables
```

### Adding New Features

1. Create a new module in `modules/`
2. Import and initialize in `ai_agent.py`
3. Add configuration in `config.py`
4. Update the main processing logic

## 🐛 Troubleshooting

### Common Issues

**Whisper.cpp not found**
```bash
cd whisper.cpp && make
```

**Ollama not responding**
```bash
ollama serve
ollama pull mistral:7b
```

**Telegram bot not working**
- Check your bot token in `.env`
- Ensure the bot is started with `/start`

**Gmail authentication failed**
- Download `credentials.json` from Google Cloud Console
- Place it in the project root

### Logs

Check the console output for detailed logs. The agent uses Python's logging module with INFO level by default.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Whisper.cpp](https://github.com/ggerganov/whisper.cpp) for speech recognition
- [Ollama](https://ollama.ai) for local LLM inference
- [Gemini](https://console.cloud.google.com) for GPT models
- [python-telegram-bot](https://python-telegram-bot.readthedocs.io/) for Telegram integration

## 📞 Support

If you encounter any issues or have questions:

1. Check the troubleshooting section
2. Review the logs for error messages
3. Open an issue on GitHub
4. Check the documentation

---

**ENJOY**

