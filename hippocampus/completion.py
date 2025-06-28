from .llm import complete_memory
from .memory import make_memory, add_memory

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