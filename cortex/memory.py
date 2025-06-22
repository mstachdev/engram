import uuid
from datetime import datetime
from dateutil import tz
from letta import Letta, Memory as LettaMemory

# Initialize Letta DB (in-memory for now, or specify a file path)
db = Letta("data/memories.letta")

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
    Store a memory in Letta DB.
    """
    # Letta expects a Memory object
    letta_mem = LettaMemory(
        id=memory["id"],
        text=memory["text"],
        metadata=memory["metadata"],
        embedding=memory["embedding"]
    )
    db.add(letta_mem)

def search_memories(query, top_k=5):
    """
    Search for relevant memories using Letta's vector search.
    """
    return db.search(query, top_k=top_k) 