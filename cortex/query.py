# Placeholder for future query logic

def query_memories(query_text, top_k=5):
    from .memory import search_memories
    return search_memories(query_text, top_k=top_k) 