#!/usr/bin/env python3
"""
Test script that writes output to file
"""

import sys
import os

def test_imports():
    """Test if required packages can be imported"""
    results = []
    results.append("🔧 Testing imports...")
    
    packages = [
        ('requests', 'requests'),
        ('openai', 'openai'),
        ('telegram', 'python-telegram-bot'),
        ('pynput', 'pynput'),
        ('sounddevice', 'sounddevice'),
        ('pydub', 'pydub'),
        ('numpy', 'numpy'),
        ('google.auth', 'google-auth'),
        ('googleapiclient', 'google-api-python-client'),
        ('speech_recognition', 'SpeechRecognition')
    ]
    
    for module_name, package_name in packages:
        try:
            __import__(module_name)
            results.append(f"✅ {package_name}")
        except ImportError:
            results.append(f"❌ {package_name} - MISSING")
    
    return results

def test_config():
    """Test configuration loading"""
    results = []
    results.append("\n⚙️ Testing configuration...")
    try:
        from config import Config
        config = Config()
        results.append("✅ Configuration loaded")
        
        # Check key settings
        if config.TELEGRAM_TOKEN:
            results.append("✅ Telegram token set")
        else:
            results.append("❌ Telegram token missing")
            
        if config.OPENAI_API_KEY:
            results.append("✅ OpenAI API key set")
        else:
            results.append("❌ OpenAI API key missing")
            
    except Exception as e:
        results.append(f"❌ Configuration error: {e}")
    
    return results

def test_whisper():
    """Test Whisper setup"""
    results = []
    results.append("\n🎤 Testing Whisper.cpp...")
    
    try:
        from config import Config
        config = Config()
        
        # Check executable
        if os.path.exists(config.WHISPER_EXECUTABLE):
            results.append("✅ Whisper executable found")
        else:
            results.append(f"❌ Whisper executable not found: {config.WHISPER_EXECUTABLE}")
        
        # Check model
        if os.path.exists(config.WHISPER_MODEL_PATH):
            results.append("✅ Whisper model found")
        else:
            results.append(f"❌ Whisper model not found: {config.WHISPER_MODEL_PATH}")
            
    except Exception as e:
        results.append(f"❌ Whisper test error: {e}")
    
    return results

def main():
    """Run all tests and write to file"""
    all_results = []
    all_results.append("🤖 AI Agent Complete Test")
    all_results.append("=" * 40)
    
    all_results.extend(test_imports())
    all_results.extend(test_config())
    all_results.extend(test_whisper())
    
    all_results.append("\n🎯 Test completed!")
    all_results.append("\nNext steps:")
    all_results.append("1. Install Ollama: https://ollama.ai")
    all_results.append("2. Pull Mistral model: ollama pull mistral:7b")
    all_results.append("3. Run the agent: python3 run.py")
    
    # Write results to file
    with open('test_results.txt', 'w') as f:
        f.write('\n'.join(all_results))
    
    print("Test completed! Check test_results.txt for results.")

if __name__ == "__main__":
    main()



