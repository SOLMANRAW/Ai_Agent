#!/usr/bin/env python3
"""
Test Hugging Face API integration
"""

import sys
import os

def test_huggingface():
    print("🤖 Testing Hugging Face API Integration...")
    print("=" * 50)
    
    try:
        # Test imports
        print("📦 Testing imports...")
        import requests
        print("✅ requests")
        
        # Test configuration
        print("\n⚙️ Testing configuration...")
        from config import Config
        config = Config()
        print("✅ Configuration loaded")
        
        if config.HUGGINGFACE_TOKEN:
            print("✅ Hugging Face token found")
        else:
            print("❌ Hugging Face token missing - please add to .env file")
            return False
        
        # Test LLM Manager
        print("\n🧠 Testing LLM Manager...")
        from modules.llm_manager import LLMManager
        llm = LLMManager(config)
        print("✅ LLM Manager initialized")
        
        # Test Hugging Face mode
        print("\n🆓 Testing Hugging Face API...")
        llm.set_mode("huggingface")
        
        test_prompt = "Hello! Can you tell me a short joke?"
        print(f"📝 Test prompt: {test_prompt}")
        
        response = llm.get_response(test_prompt)
        print(f"🤖 Response: {response}")
        
        if "Error" not in response:
            print("✅ Hugging Face API working!")
            return True
        else:
            print(f"❌ Hugging Face API error: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_huggingface()
    if success:
        print("\n🎉 Hugging Face integration successful!")
        print("You can now use your AI agent with free unlimited API!")
    else:
        print("\n❌ Hugging Face integration failed!")
        print("Please check your token and try again.")

