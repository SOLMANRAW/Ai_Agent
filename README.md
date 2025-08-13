# AI Agent

**A comprehensive AI assistant that can search files, manage emails, process voice commands, and run both online (Gemini) and offline (Ollama) language models.**

# Features

    File Search: Search for files across your device with natural language
    Email Management: Send emails through Gmail integration
    Voice Recognition: Process voice commands using Whisper.cpp
    Dual LLM Support: Toggle between Gemini (online) and Ollama Mistral 7B (offline)
    Telegram Bot: Interact via Telegram with voice and text messages
    Hotkey Activation: Global hotkey (Ctrl+Alt+A) for voice input
    Privacy: Run completely offline with local models


# Prerequisites:

    Python 3.8+
    Git
    Ollama (for offline mode)
    Telegram Bot Token
    Gemini API Key (for online mode)


# Installation

  **Clone the repository**

    git clone <your-repo-url>
    cd Ai_Agent

  **Install python dependencies**

    pip install -r requirements.txt

  **Run the setup script**

    ./setup.sh

  **Configure your environment**

    # Edit the .env file with your API keys
    nano .env

  **Download Whisper model**

    wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo-q5_0.bin -O models/ggml-large-v3-turbo-q5_0.bin

  **Build Whisper.cpp**

    cd whisper.cpp && make
    cd ..

  **Install Ollama and pull model**

    # Install Ollama from https://ollama.ai
    ollama pull mistral:7b

  **Run the AI Agent**

    python start_agent.py

# Configuration:

 **Create a .env file with the following variables:**

 **Telegram Bot Configuration:**

    TELEGRAM_TOKEN=your_telegram_bot_token_here
    TELEGRAM_CHAT_ID=your_telegram_chat_id_here

 **Gemini Configuration:**

    GEMINI_API_KEY=your_gemini_api_key_here

 **Ollama Configuration:**

    OLLAMA_BASE_URL=http://localhost:11434

 **Gmail Configuration:**

    GMAIL_CREDENTIALS_FILE=credentials.json
    GMAIL_TOKEN_FILE=token.json

 **Whisper Configuration:**

    WHISPER_MODEL_PATH=models/ggml-large-v3-turbo-q5_0.bin
    WHISPER_CPP_PATH=./whisper.cpp

**Getting API Keys:**

**Telegram Bot**

    Message @BotFather on Telegram
    Create a new bot with /newbot
    Get your bot token and chat ID

**Gemini**

    Go to Google Cloud Console
    Get your API key 

**Gmail**

    Go to Google Cloud Console
    Create a project and enable Gmail API
    Download credentials.json

**Usage:**

**Telegram Commands:**

    /start - Initialize the bot
    /help - Show help information
    /mode online - Switch to Gemini
    /mode offline - Switch to Ollama
    /status - Check system status

**Voice Commands:**

    To search for files use the format:

    “Find the file called report”
    “Locate budget.xlsx”
    “Search for the file named notes”
    “Find resume.pdf”

    To send an email use the format:

    "Send an email to mrx@example.com subject: Test message: This is a test"


# Architecture

**AI Agent:**

    LLM Manager (Gemini/Ollama)

    Speech Recognition (Whisper.cpp)

    File Search Module

    Email Manager (Gmail)

    Telegram Bot

    Hotkey Manager

**Modules:**

    llm_manager.py: Handles Gemini and Ollama integration

    speech_recognition.py: Whisper.cpp integration for voice transcription

    file_search.py: File system search and management

    email_manager.py: Gmail API integration

    telegram_bot.py: Telegram bot interface

    hotkey_manager.py: Global hotkey management


# Development

**Adding New Features:**

    Create a new module in modules/
    Import and initialize in ai_agent.py
    Add configuration in config.py
    Update the main processing logic


# Troubleshooting

**Common Issues:**

    Whisper.cpp not found

    cd whisper.cpp && make

    Ollama not responding

    ollama serve
    ollama pull mistral:7b

**Telegram bot not working:**

    Check your bot token in .env
    Ensure the bot is started with /start

**Gmail authentication failed:**

    Download credentials.json from Google Cloud Console
    Place it in the project root

**Logs:**

    Check the console output for detailed logs. The agent uses Python's logging module with INFO level by default.

# Contributing

    Fork the repository
    Create a feature branch
    Make your changes
    Add tests if applicable
    Submit a pull request

# License

    This project is licensed under the MIT License - see the LICENSE file for details.

# Acknowledgments

    Whisper.cpp for speech recognition
    Ollama for local LLM inference
    Gemini for GPT models
    python-telegram-bot for Telegram integration


# Support

**If you encounter any issues or have questions:**

    Check the troubleshooting section
    Review the logs for error messages
    Open an issue on GitHub
    Check the documentation


**ENJOY**

