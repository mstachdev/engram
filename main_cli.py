#!/usr/bin/env python3
"""
Engram CLI - Command Line Interface for Memory Creation

This provides a command-line interface for:
- Adding fragments directly from command line
- Creating memories from fragments
- Testing the hippocampus connection
"""

import sys
import argparse
from hippocampus.llm import complete_memory, LLMClient
from cortex.processor import add_fragments_from_input, process_fragments_to_memory
from cortex.database import get_fragments

def main():
    parser = argparse.ArgumentParser(
        description="Engram CLI - Brain-inspired memory system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main_cli.py                                    # Interactive mode
  python main_cli.py memory "walked dog" "sunny day"   # Direct memory creation
  python main_cli.py add "Had coffee this morning."    # Add fragments to database
  python main_cli.py process --all                     # Process stored fragments
  python main_cli.py test                              # Test hippocampus connection
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Memory command - create memory directly from fragments
    memory_parser = subparsers.add_parser('memory', help='Create memory from fragments')
    memory_parser.add_argument('fragments', nargs='+', help='Fragment texts to combine into memory')
    
    # Add command - add fragments to database
    add_parser = subparsers.add_parser('add', help='Add fragments from text')
    add_parser.add_argument('text', help='Text to extract fragments from')
    add_parser.add_argument('--source', default='cli', help='Source identifier')
    add_parser.add_argument('--session', help='Session name')
    
    # Process command - process stored fragments into memories
    process_parser = subparsers.add_parser('process', help='Process fragments into memories')
    process_parser.add_argument('--ids', nargs='+', help='Specific fragment IDs to process')
    process_parser.add_argument('--all', action='store_true', help='Process all unprocessed fragments')
    process_parser.add_argument('--limit', type=int, default=10, help='Max fragments to process at once')
    
    # List command - show stored fragments
    list_parser = subparsers.add_parser('list', help='List stored fragments')
    list_parser.add_argument('--processed', action='store_true', help='Show processed fragments')
    list_parser.add_argument('--limit', type=int, default=20, help='Max fragments to show')
    
    # Test command - test hippocampus connection
    test_parser = subparsers.add_parser('test', help='Test hippocampus LLM connection')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🧠 Engram CLI - Brain Memory System")
    print("=" * 60)
    print()
    
    # If no command specified, start interactive mode
    if not args.command:
        interactive_mode()
        return
    
    if args.command == 'memory':
        create_memory_from_fragments(args.fragments)
    elif args.command == 'add':
        add_text_fragments(args.text, args.source, args.session)
    elif args.command == 'process':
        process_stored_fragments(args.ids, args.all, args.limit)
    elif args.command == 'list':
        list_fragments(args.processed, args.limit)
    elif args.command == 'test':
        test_hippocampus()

def create_memory_from_fragments(fragments):
    """Create memory directly from provided fragments."""
    print(f"🧩 Creating memory from {len(fragments)} fragments:")
    for i, fragment in enumerate(fragments, 1):
        print(f"  {i}. {fragment}")
    print()
    print("🧠 Sending to hippocampus for consolidation...")
    print()
    
    memory = complete_memory(fragments)
    if memory:
        print("✅ Generated Memory:")
        print("=" * 50)
        print(memory)
        print("=" * 50)
    else:
        print("❌ Failed to generate memory. Is the vLLM server running?")
        print("   Start it with: ./launch_vllm_server.sh /path/to/model")

def add_text_fragments(text, source, session_name):
    """Add fragments from text to the database."""
    print(f"📝 Adding fragments from text (source: {source})...")
    if session_name:
        print(f"📁 Session: {session_name}")
    print()
    
    result = add_fragments_from_input(text, source, session_name)
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Added {result['fragments_added']} fragments to database")
        if 'fragments' in result:
            print("\n🧩 Extracted fragments:")
            for i, fragment in enumerate(result['fragments'], 1):
                print(f"  {i}. {fragment}")
        
        # Ask if user wants to process them immediately
        if result['fragments_added'] > 0:
            print()
            process_now = input("🤔 Process these fragments into memory now? (y/n): ").lower()
            if process_now == 'y':
                # Get the most recent fragments and process them
                fragments = get_fragments(processed=False, limit=result['fragments_added'])
                if fragments:
                    fragment_ids = [f['id'] for f in fragments[-result['fragments_added']:]]
                    print()
                    result = process_fragments_to_memory(fragment_ids)
                    if 'error' not in result:
                        print(f"✅ Successfully processed fragments into memory!")
                        if 'memory' in result and result['memory']:
                            print("\n🧠 Consolidated Memory:")
                            print("=" * 50)
                            print(result['memory'].get('text', 'Memory created successfully'))
                            print("=" * 50)

def process_stored_fragments(fragment_ids, process_all, limit):
    """Process stored fragments into memories."""
    if fragment_ids:
        print(f"🔄 Processing {len(fragment_ids)} specific fragments...")
        result = process_fragments_to_memory(fragment_ids)
    elif process_all:
        print(f"🔍 Looking for unprocessed fragments (limit: {limit})...")
        # Get unprocessed fragments
        fragments = get_fragments(processed=False, limit=limit)
        if not fragments:
            print("📭 No unprocessed fragments found.")
            return
        
        fragment_ids = [f['id'] for f in fragments]
        print(f"📋 Found {len(fragment_ids)} unprocessed fragments:")
        for i, fragment in enumerate(fragments, 1):
            print(f"  {i:2d}. {fragment['content'][:60]}...")
        print()
        
        confirm = input(f"🤔 Process all {len(fragment_ids)} fragments into memory? (y/n): ").lower()
        if confirm != 'y':
            print("❌ Processing cancelled.")
            return
        
        print("🧠 Processing fragments...")
        result = process_fragments_to_memory(fragment_ids)
    else:
        print("❌ Please specify --ids or --all")
        return
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
    else:
        print(f"✅ Successfully processed {result['processed_fragments']} fragments")
        if 'memory' in result and result['memory']:
            print("\n🧠 Consolidated Memory:")
            print("=" * 50)
            print(result['memory'].get('text', 'Memory created successfully'))
            print("=" * 50)

def list_fragments(show_processed, limit):
    """List stored fragments."""
    print(f"🔍 Loading fragments...")
    fragments = get_fragments(processed=show_processed, limit=limit)
    
    if not fragments:
        status = "processed" if show_processed else "unprocessed"
        print(f"📭 No {status} fragments found.")
        return
    
    status = "processed" if show_processed else "unprocessed"
    print(f"📋 Showing {len(fragments)} {status} fragments:")
    print()
    
    for i, fragment in enumerate(fragments, 1):
        print(f"{i:2d}. {fragment['content']}")
        print(f"    📍 ID: {fragment['id']} | 📁 Source: {fragment['source']} | 🕒 {fragment['created_at']}")
        print()

def test_hippocampus():
    """Test the hippocampus LLM connection."""
    print("🔍 Testing Hippocampus LLM connection...")
    try:
        client = LLMClient()
        print(f"✅ Connected to model: {client.model_name}")
        
        print("🧠 Sending test query...")
        response = client.query("Hello! Please respond with 'Connection successful!'")
        if response:
            print("✅ Hippocampus LLM query successful!")
            print(f"📝 Response: {response}")
        else:
            print("❌ Hippocampus LLM query failed")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure the vLLM server is running:")
        print("   ./launch_vllm_server.sh /path/to/model")

def interactive_mode():
    """Interactive mode for adding fragments and creating memories."""
    print("🎯 Interactive Memory Creation Mode")
    print("=" * 60)
    print("Welcome! This mode lets you:")
    print("  • Add fragments one by one or in bulk")
    print("  • See your fragment collection")
    print("  • Process fragments into consolidated memories")
    print("  • Test the hippocampus connection")
    print()
    print("Commands:")
    print("  'add <text>'     - Add fragments from text")
    print("  'memory <f1> <f2>' - Create memory directly from fragments")
    print("  'list'           - Show stored fragments")
    print("  'process'        - Process stored fragments into memory")
    print("  'test'           - Test hippocampus connection")
    print("  'help'           - Show this help")
    print("  'quit' or 'exit' - Exit interactive mode")
    print("=" * 60)
    
    while True:
        try:
            command = input("\n🧠 Engram> ").strip()
            
            if not command:
                continue
                
            if command.lower() in ['quit', 'exit', 'q']:
                print("👋 Thanks for using Engram CLI!")
                break
                
            elif command.lower() == 'help':
                print("\n📖 Available commands:")
                print("  add <text>       - Extract fragments from text and add to database")
                print("  memory <f1> <f2> - Create memory directly from fragment texts")
                print("  list             - Show stored fragments")
                print("  process          - Process stored fragments into memory")
                print("  test             - Test hippocampus connection")
                print("  help             - Show this help")
                print("  quit/exit        - Exit interactive mode")
                
            elif command.lower() == 'list':
                list_fragments(False, 20)
                
            elif command.lower() == 'process':
                fragments = get_fragments(processed=False, limit=20)
                if not fragments:
                    print("📭 No unprocessed fragments found.")
                    print("💡 Use 'add <text>' to add some fragments first.")
                else:
                    print(f"📋 Found {len(fragments)} unprocessed fragments:")
                    for i, fragment in enumerate(fragments, 1):
                        print(f"  {i:2d}. {fragment['content'][:60]}...")
                    
                    confirm = input(f"\n🤔 Process all {len(fragments)} fragments? (y/n): ").lower()
                    if confirm == 'y':
                        fragment_ids = [f['id'] for f in fragments]
                        result = process_fragments_to_memory(fragment_ids)
                        if 'error' not in result:
                            print(f"✅ Successfully processed {result['processed_fragments']} fragments!")
                            if 'memory' in result and result['memory']:
                                print("\n🧠 Consolidated Memory:")
                                print("=" * 50)
                                print(result['memory'].get('text', 'Memory created successfully'))
                                print("=" * 50)
                        else:
                            print(f"❌ Error: {result['error']}")
                
            elif command.lower() == 'test':
                test_hippocampus()
                
            elif command.lower().startswith('add '):
                text = command[4:].strip()
                if text:
                    add_text_fragments(text, 'interactive_cli', None)
                else:
                    print("❌ Please provide text after 'add'")
                    print("   Example: add I had coffee this morning")
                    
            elif command.lower().startswith('memory '):
                fragments_text = command[7:].strip()
                if fragments_text:
                    # Split by quotes or spaces
                    fragments = []
                    if '"' in fragments_text:
                        # Parse quoted fragments
                        import shlex
                        try:
                            fragments = shlex.split(fragments_text)
                        except:
                            fragments = fragments_text.split()
                    else:
                        fragments = fragments_text.split()
                    
                    if fragments:
                        create_memory_from_fragments(fragments)
                    else:
                        print("❌ Please provide fragment texts")
                else:
                    print("❌ Please provide fragments after 'memory'")
                    print("   Example: memory \"walked dog\" \"sunny day\" \"beautiful park\"")
                    
            else:
                print(f"❓ Unknown command: {command}")
                print("💡 Type 'help' for available commands")
            
        except KeyboardInterrupt:
            print("\n\n👋 Exiting Engram CLI...")
            break
        except EOFError:
            print("\n\n👋 Exiting Engram CLI...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 