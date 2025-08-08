#!/usr/bin/env python3
"""
AI Agent Launcher
"""

import sys
import os
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Main launcher function"""
    print("🤖 Starting AI Agent...")
    print("=" * 40)
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please run ./setup.sh first or create a .env file")
        print("You can copy from env_example.txt as a template")
        return 1
    
    # Try to import and run the agent
    try:
        from ai_agent import main as agent_main
        agent_main()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please install dependencies: pip install -r requirements.txt")
        return 1
    except KeyboardInterrupt:
        print("\n👋 AI Agent stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error starting AI Agent: {e}")
        print("Run python test_setup.py to diagnose issues")
        return 1

if __name__ == "__main__":
    sys.exit(main())
