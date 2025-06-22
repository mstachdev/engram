#!/usr/bin/env python3
"""
Engram - A memory and AI application

This is the main entry point for the Engram application.
Cortex is the AI/LLM module within Engram.
"""

import sys
from cortex.llm import complete_memory

def main():
    """
    Main entry point for the Engram application.
    """
    print("=" * 50)
    print("Welcome to Engram")
    print("=" * 50)
    print()
    
    if len(sys.argv) < 2:
        print("Usage: python main.py <command> [args...]")
        print()
        print("Available commands:")
        print("  memory <fragments...>  - Create a memory from fragments")
        print("  test                   - Test the LLM connection")
        print()
        print("Make sure the vLLM server is running:")
        print("  ./cortex/launch_vllm_server.sh /path/to/your/model")
        return
    
    command = sys.argv[1]
    
    if command == "memory":
        if len(sys.argv) < 3:
            print("Error: Please provide fragments for the memory")
            print("Example: python main.py memory 'walked dog' 'sunny day' 'park'")
            return
        
        fragments = sys.argv[2:]
        print(f"Creating memory from fragments: {fragments}")
        print()
        
        memory = complete_memory(fragments)
        if memory:
            print("Generated Memory:")
            print("-" * 30)
            print(memory)
        else:
            print("Failed to generate memory. Is the vLLM server running?")
    
    elif command == "test":
        print("Testing LLM connection...")
        from cortex.llm import LLMClient
        
        try:
            client = LLMClient()
            print(f"✓ Connected to model: {client.model_name}")
            
            response = client.query("Hello! Please respond with 'Connection successful!'")
            if response:
                print("✓ LLM query successful!")
                print(f"Response: {response}")
            else:
                print("✗ LLM query failed")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    else:
        print(f"Unknown command: {command}")
        print("Run 'python main.py' for usage information.")

if __name__ == "__main__":
    main() 