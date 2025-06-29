import uuid
import json
import os
from datetime import datetime
from dateutil import tz
from llm.client import create_llm_client

# Try to import Letta with the new API
try:
    from letta_client import LettaClient
    from letta_client.schemas import Memory as LettaMemory
    # Initialize Letta client with new API
    letta_client = LettaClient()
    print("✓ Letta client initialized successfully")
except ImportError:
    print("⚠️ Letta client not available, using fallback storage")
    letta_client = None
    LettaMemory = None

# Fallback file-based storage
MEMORY_FILE = "data/memories.json"

def _ensure_data_dir():
    """Ensure the data directory exists."""
    os.makedirs("data", exist_ok=True)

def _load_memories():
    """Load memories from JSON file."""
    _ensure_data_dir()
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return []

def _save_memories(memories):
    """Save memories to JSON file."""
    _ensure_data_dir()
    with open(MEMORY_FILE, 'w') as f:
        json.dump(memories, f, indent=2)

# Initialize LLM client for hippocampus module
hippocampus_llm = create_llm_client("hippocampus")

def make_memory(text, source, fragments=None, metadata=None, embedding=None):
    """
    Create a memory dict with all required fields.
    """
    return {
        "id": str(uuid.uuid4()),
        "text": text,
        "created_at": datetime.now(tz=tz.UTC).isoformat(),
        "embedding": embedding,  # Can be None if not yet embedded
        "source": source,
        "fragments": fragments or [],
        "metadata": metadata or {},
    }

def add_memory(memory):
    """
    Store a memory using Letta client or JSON fallback.
    """
    if letta_client and LettaMemory:
        try:
            # Use Letta client
            letta_mem = LettaMemory(
                id=memory["id"],
                text=memory["text"],
                metadata=memory.get("metadata", {}),
                embedding=memory.get("embedding")
            )
            letta_client.add_memory(letta_mem)
            print(f"Memory stored in Letta: {memory['id']}")
            return
        except Exception as e:
            print(f"Letta storage failed, using fallback: {e}")
    
    # Fallback to JSON storage
    memories = _load_memories()
    memories.append(memory)
    _save_memories(memories)
    print(f"Memory stored in JSON: {memory['id']}")

def get_memories(limit=None, source=None):
    """
    Get memories from JSON storage with optional filtering.
    """
    memories = _load_memories()
    
    # Filter by source if specified
    if source:
        memories = [m for m in memories if m.get('source') == source]
    
    # Apply limit if specified
    if limit:
        memories = memories[:limit]
    
    return memories

def search_memories(query, top_k=5):
    """
    Search for relevant memories using Letta or simple text matching fallback.
    """
    if letta_client:
        try:
            # Use Letta's vector search
            results = letta_client.search_memories(query, top_k=top_k)
            print(f"Letta search returned {len(results)} results")
            return results
        except Exception as e:
            print(f"Letta search failed, using fallback: {e}")
    
    # Fallback to simple text search
    memories = _load_memories()
    query_lower = query.lower()
    matching_memories = []
    
    for memory in memories:
        text = memory.get('text', '').lower()
        if query_lower in text:
            matching_memories.append(memory)
    
    return matching_memories[:top_k]

def complete_memory(fragments, max_tokens=128):
    """
    Given a list of fragments/words, generate a structured memory using the LLM.
    """
    prompt = (
        "You are an assistant that helps users log memories. "
        "Given the following unordered words or fragments, reconstruct a coherent, embellished memory or story. "
        "Fragments: " + ", ".join(fragments) + "\nMemory: "
    )
    
    return hippocampus_llm.query(prompt, max_tokens=max_tokens)

def process_fragments(fragments, source="user", metadata=None):
    """
    Take a list of fragments, generate a structured memory, and store it.
    """
    memory_text = complete_memory(fragments)
    memory = make_memory(
        text=memory_text,
        source=source,
        fragments=fragments,
        metadata=metadata
    )
    add_memory(memory)
    return memory 