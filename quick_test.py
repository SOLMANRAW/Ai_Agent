#!/usr/bin/env python3
"""
Quick test to check AI Agent setup status
"""

import os
import sys

def test_imports():
    """Test if required packages can be imported"""
    print("🔧 Testing imports...")
    
    packages = [
        ('requests', 'requests'),
        ('openai', 'openai'),
        ('telegram', 'python-telegram-bot'),
        ('pynput', 'pynput'),
        ('sounddevice', 'sounddevice'),
        ('pydub', 'pydub'),
        ('numpy', 'numpy')
    ]
    
    for module_name, package_name in packages:
        try:
            __import__(module_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - MISSING")
    
    print()

def test_config():
    """Test configuration loading"""
    print("⚙️ Testing configuration...")
    try:
        from config import Config
        config = Config()
        print("✅ Configuration loaded")
        
        # Check key settings
        if config.TELEGRAM_TOKEN:
            print("✅ Telegram token set")
        else:
            print("❌ Telegram token missing")
            
        if config.OPENAI_API_KEY:
            print("✅ OpenAI API key set")
        else:
            print("❌ OpenAI API key missing")
            
    except Exception as e:
        print(f"❌ Configuration error: {e}")
    
    print()

def test_whisper():
    """Test Whisper setup"""
    print("🎤 Testing Whisper.cpp...")
    
    try:
        from config import Config
        config = Config()
        
        # Check executable
        if os.path.exists(config.WHISPER_EXECUTABLE):
            print("✅ Whisper executable found")
        else:
            print(f"❌ Whisper executable not found: {config.WHISPER_EXECUTABLE}")
        
        # Check model
        if os.path.exists(config.WHISPER_MODEL_PATH):
            print("✅ Whisper model found")
        else:
            print(f"❌ Whisper model not found: {config.WHISPER_MODEL_PATH}")
            
    except Exception as e:
        print(f"❌ Whisper test error: {e}")
    
    print()

def test_ollama():
    """Test Ollama setup"""
    print("🤖 Testing Ollama...")
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if any("mistral" in model.get("name", "") for model in models):
                print("✅ Ollama running with Mistral model")
            else:
                print("⚠️ Ollama running but Mistral model not found")
        else:
            print("❌ Ollama API not responding")
    except Exception as e:
        print(f"❌ Ollama not running: {e}")
    
    print()

def main():
    """Run all tests"""
    print("🤖 AI Agent Quick Test")
    print("=" * 30)
    
    test_imports()
    test_config()
    test_whisper()
    test_ollama()
    
    print("🎯 Test completed!")
    print("\nNext steps:")
    print("1. Install Ollama: https://ollama.ai")
    print("2. Pull Mistral model: ollama pull mistral:7b")
    print("3. Run the agent: python3 run.py")

if __name__ == "__main__":
    main()



