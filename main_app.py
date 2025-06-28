#!/usr/bin/env python3
"""
Engram Web App - Flask Web Interface Launcher

This launches the web application for fragment input and memory creation.
"""

import sys
import os
from cortex.api import run_api

def main():
    print("=" * 60)
    print("🧠 Engram Web Application")
    print("=" * 60)
    print()
    
    # Check if hippocampus is available
    try:
        from hippocampus.llm import LLMClient
        print("✓ Hippocampus module available")
    except ImportError as e:
        print(f"⚠️  Hippocampus module not available: {e}")
        print("   Memory consolidation features may not work")
    
    print("Starting Cortex Web Interface...")
    print()
    print("🌐 Web Interface: http://localhost:5000")
    print("📱 Mobile friendly: Access from any device on your network")
    print()
    print("Features available:")
    print("  • Fragment extraction from text input")
    print("  • File upload and processing")
    print("  • Fragment selection and management")
    print("  • Memory consolidation via hippocampus")
    print("  • Session management")
    print()
    print("API Endpoints:")
    print("  POST /fragments        - Add fragments from text")
    print("  POST /fragments/file   - Upload file and extract fragments")
    print("  GET  /fragments        - Get stored fragments")
    print("  POST /fragments/process - Process fragments into memory")
    print("  GET  /sessions         - Get all sessions")
    print("  POST /sessions         - Create new session")
    print()
    print("Prerequisites:")
    print("  1. Start vLLM server: ./launch_vllm_server.sh /path/to/model")
    print("  2. Install dependencies: pip install -r requirements.txt")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Start the Flask server
        run_api(host='0.0.0.0', port=5000, debug=False)
        
    except ImportError as e:
        print(f"❌ Error importing cortex API: {e}")
        print("Make sure Flask and other dependencies are installed:")
        print("  pip install -r cortex/requirements.txt")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down Engram web server...")
        print("Thanks for using Engram!")
        
    except Exception as e:
        print(f"❌ Error starting web server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 