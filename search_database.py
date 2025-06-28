#!/usr/bin/env python3
"""
Simple script to search the SQLite fragments database
"""

import sqlite3
import json
from pathlib import Path

DB_PATH = Path("cortex/data/fragments.db")

def search_fragments(search_term="", show_all=False, limit=10):
    """Search fragments by content."""
    if not DB_PATH.exists():
        print("❌ Database not found at:", DB_PATH)
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if show_all:
        query = "SELECT * FROM fragments ORDER BY created_at DESC LIMIT ?"
        params = [limit]
    else:
        query = "SELECT * FROM fragments WHERE content LIKE ? ORDER BY created_at DESC LIMIT ?"
        params = [f"%{search_term}%", limit]
    
    cursor.execute(query, params)
    fragments = cursor.fetchall()
    conn.close()
    
    if not fragments:
        print("🔍 No fragments found")
        return
    
    print(f"📊 Found {len(fragments)} fragments:")
    print("=" * 80)
    
    for i, fragment in enumerate(fragments, 1):
        id, content, source, created_at, metadata, processed, memory_id = fragment
        
        print(f"\n{i}. Fragment ID: {id[:8]}...")
        print(f"   📝 Content: {content[:100]}{'...' if len(content) > 100 else ''}")
        print(f"   📂 Source: {source}")
        print(f"   📅 Created: {created_at}")
        print(f"   ✅ Processed: {'Yes' if processed else 'No'}")
        if memory_id:
            print(f"   🧠 Memory ID: {memory_id[:8]}...")

def show_sessions():
    """Show all sessions."""
    if not DB_PATH.exists():
        print("❌ Database not found at:", DB_PATH)
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM sessions ORDER BY created_at DESC")
    sessions = cursor.fetchall()
    conn.close()
    
    if not sessions:
        print("🔍 No sessions found")
        return
    
    print(f"📊 Found {len(sessions)} sessions:")
    print("=" * 80)
    
    for i, session in enumerate(sessions, 1):
        id, name, created_at, metadata = session
        print(f"\n{i}. Session ID: {id[:8]}...")
        print(f"   📝 Name: {name or 'Unnamed'}")
        print(f"   📅 Created: {created_at}")

def show_stats():
    """Show database statistics."""
    if not DB_PATH.exists():
        print("❌ Database not found at:", DB_PATH)
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Count fragments
    cursor.execute("SELECT COUNT(*) FROM fragments")
    total_fragments = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM fragments WHERE processed = TRUE")
    processed_fragments = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM sessions")
    total_sessions = cursor.fetchone()[0]
    
    conn.close()
    
    print("📊 Database Statistics:")
    print("=" * 40)
    print(f"📝 Total fragments: {total_fragments}")
    print(f"✅ Processed fragments: {processed_fragments}")
    print(f"⏳ Unprocessed fragments: {total_fragments - processed_fragments}")
    print(f"📂 Total sessions: {total_sessions}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("🧠 Engram Database Search")
        print("=" * 40)
        print("Usage:")
        print("  python search_database.py stats              - Show database stats")
        print("  python search_database.py all               - Show all fragments")
        print("  python search_database.py sessions          - Show all sessions")
        print("  python search_database.py search <term>     - Search fragments")
        print("\nExamples:")
        print("  python search_database.py search 'meeting'")
        print("  python search_database.py search 'project'")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "stats":
        show_stats()
    elif command == "all":
        search_fragments(show_all=True, limit=50)
    elif command == "sessions":
        show_sessions()
    elif command == "search" and len(sys.argv) > 2:
        search_term = " ".join(sys.argv[2:])
        search_fragments(search_term, limit=20)
    else:
        print("❌ Invalid command. Use 'stats', 'all', 'sessions', or 'search <term>'") 