#!/usr/bin/env python3
"""
Test script to verify AI Agent setup
"""

import os
import sys
import logging
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_config():
    """Test configuration loading"""
    print("🔧 Testing configuration...")
    try:
        config = Config()
        print("✅ Configuration loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_dependencies():
    """Test if all required packages are installed"""
    print("\n📦 Testing dependencies...")
    
    required_packages = [
        'telegram',
        'openai',
        'requests',
        'google.auth',
        'pynput',
        'sounddevice',
        'numpy',
        'pydub'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies installed")
    return True

def test_whisper():
    """Test Whisper.cpp setup"""
    print("\n🎤 Testing Whisper.cpp...")
    
    config = Config()
    whisper_path = config.WHISPER_CPP_PATH
    model_path = config.WHISPER_MODEL_PATH
    
    # Check whisper.cpp directory
    if not os.path.exists(whisper_path):
        print(f"❌ Whisper.cpp directory not found: {whisper_path}")
        print("   Run: git clone https://github.com/ggerganov/whisper.cpp.git")
        return False
    
    # Check whisper main executable
    whisper_main = os.path.join(whisper_path, "main")
    if not os.path.exists(whisper_main):
        print(f"❌ Whisper main executable not found: {whisper_main}")
        print("   Run: cd whisper.cpp && make")
        return False
    
    # Check model file
    if not os.path.exists(model_path):
        print(f"❌ Whisper model not found: {model_path}")
        print("   Run: wget https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-large-v3-turbo-q5_0.bin -O models/ggml-large-v3-turbo-q5_0.bin")
        return False
    
    print("✅ Whisper.cpp setup complete")
    return True

def test_ollama():
    """Test Ollama setup"""
    print("\n🤖 Testing Ollama...")
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if any("mistral" in model.get("name", "") for model in models):
                print("✅ Ollama running with Mistral model")
                return True
            else:
                print("⚠️  Ollama running but Mistral model not found")
                print("   Run: ollama pull mistral:7b")
                return False
        else:
            print("❌ Ollama API not responding")
            return False
    except Exception as e:
        print(f"❌ Ollama not running: {e}")
        print("   Install from: https://ollama.ai")
        print("   Then run: ollama serve")
        return False

def test_environment():
    """Test environment variables"""
    print("\n🔐 Testing environment variables...")
    
    config = Config()
    required_vars = ['TELEGRAM_TOKEN', 'OPENAI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        value = getattr(config, var)
        if not value:
            missing_vars.append(var)
            print(f"❌ {var} - MISSING")
        else:
            print(f"✅ {var} - SET")
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("   Edit your .env file")
        return False
    
    print("✅ All required environment variables set")
    return True

def main():
    """Run all tests"""
    print("🤖 AI Agent Setup Test")
    print("=" * 30)
    
    tests = [
        ("Configuration", test_config),
        ("Dependencies", test_dependencies),
        ("Whisper.cpp", test_whisper),
        ("Ollama", test_ollama),
        ("Environment", test_environment)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test failed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 30)
    print("📊 Test Results:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Your AI Agent is ready to run.")
        print("   Run: python ai_agent.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues above before running the agent.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)



