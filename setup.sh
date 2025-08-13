#!/bin/bash

echo "AI Agent Setup Script"
echo "========================"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "Python 3 found"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp env_example.txt .env
    echo "Please edit .env file with your API keys and configuration"
fi

# Create models directory
echo "Creating models directory..."
mkdir -p models

# Check if whisper.cpp exists
if [ ! -d "whisper.cpp" ]; then
    echo "whisper.cpp directory not found. Please clone it:"
    echo "   git clone https://github.com/ggerganov/whisper.cpp.git"
    echo "   cd whisper.cpp && make"
fi

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo " Ollama not found. Please install it from https://ollama.ai"
    echo "   Then run: ollama pull mistral:7b"
fi

echo ""
echo "Setup completed!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys"
echo "2. Download whisper model: wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo-q5_0.bin -O models/ggml-large-v3-turbo-q5_0.bin"
echo "3. Build whisper.cpp: cd whisper.cpp && make"
echo "4. Install Ollama and pull model: ollama pull mistral:7b"
echo "5. Run the agent: python ai_agent.py"
echo ""
echo "For Gmail integration, download credentials.json from Google Cloud Console"



