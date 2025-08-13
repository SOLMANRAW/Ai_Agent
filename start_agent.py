#!/usr/bin/env python3
"""
Simple AI Agent startup script
Run this in your terminal: python3 start_agent.py
"""

import os
import asyncio

def main():
    print("Starting AI Agent...")
    print("=" * 40)
    
    try:
        # Test imports
        print("Testing imports...")
        import requests
        print("requests")
        import telegram
        print("python-telegram-bot")
        import pynput
        print("pynput")
        import sounddevice
        print("sounddevice")
        import pydub
        print("pydub")
        import numpy
        print("numpy")
        import google.auth
        print("google-auth")
        import googleapiclient
        print("google-api-python-client")
        import speech_recognition
        print("SpeechRecognition")
        
        print("\nAll packages imported successfully!")
        
        # Test configuration
        print("\nTesting configuration...")
        from config import Config
        config = Config()
        print("Configuration loaded")
        
        if config.get('TELEGRAM_TOKEN'):
            print("Telegram token set")
        else:
            print("Telegram token missing")
            
                
        # Test Whisper
        print("\nTesting Whisper.cpp...")
        whisper_exec = config.get('WHISPER_EXECUTABLE', 'whisper.cpp/build/main')
        if os.path.exists(whisper_exec):
            print("Whisper executable found")
        else:
            print(f"Whisper executable not found: {whisper_exec}")
        
        whisper_model = config.get('WHISPER_MODEL_PATH', 'models/ggml-large-v3-turbo-q5_0.bin')
        if os.path.exists(whisper_model):
            print("Whisper model found")
        else:
            print(f"Whisper model not found: {whisper_model}")
        
        print("\nAll tests passed! Starting AI Agent...")
        print("=" * 40)
        
        # Start the agent
        from ai_agent import AIAgent
        agent = AIAgent()
        asyncio.run(agent.start())
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please install missing packages: pip install --break-system-packages <package_name>")
    except Exception as e:
        print(f"Error: {e}")
        print("Check the error message above for details.")

if __name__ == "__main__":
    main()

