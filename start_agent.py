#!/usr/bin/env python3
"""
Simple AI Agent startup script
Run this in your terminal: python3 start_agent.py
"""

import sys
import os

def main():
    print("🤖 Starting AI Agent...")
    print("=" * 40)
    
    try:
        # Test imports
        print("📦 Testing imports...")
        import requests
        print("✅ requests")
        import openai
        print("✅ openai")
        import telegram
        print("✅ python-telegram-bot")
        import pynput
        print("✅ pynput")
        import sounddevice
        print("✅ sounddevice")
        import pydub
        print("✅ pydub")
        import numpy
        print("✅ numpy")
        import google.auth
        print("✅ google-auth")
        import googleapiclient
        print("✅ google-api-python-client")
        import speech_recognition
        print("✅ SpeechRecognition")
        
        print("\n✅ All packages imported successfully!")
        
        # Test configuration
        print("\n⚙️ Testing configuration...")
        from config import Config
        config = Config()
        print("✅ Configuration loaded")
        
        if config.TELEGRAM_TOKEN:
            print("✅ Telegram token set")
        else:
            print("❌ Telegram token missing")
            
        if config.OPENAI_API_KEY:
            print("✅ OpenAI API key set")
        else:
            print("❌ OpenAI API key missing")
        
        # Test Whisper
        print("\n🎤 Testing Whisper.cpp...")
        if os.path.exists(config.WHISPER_EXECUTABLE):
            print("✅ Whisper executable found")
        else:
            print(f"❌ Whisper executable not found: {config.WHISPER_EXECUTABLE}")
        
        if os.path.exists(config.WHISPER_MODEL_PATH):
            print("✅ Whisper model found")
        else:
            print(f"❌ Whisper model not found: {config.WHISPER_MODEL_PATH}")
        
        print("\n🎉 All tests passed! Starting AI Agent...")
        print("=" * 40)
        
        # Start the agent
        from ai_agent import main as agent_main
        agent_main()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install missing packages: pip install --break-system-packages <package_name>")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Check the error message above for details.")

if __name__ == "__main__":
    main()

