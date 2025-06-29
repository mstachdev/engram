# Query logic for natural language memory queries

def query_memories(query_text, top_k=5):
    """Search memories using simple text matching."""
    from .memory import search_memories
    return search_memories(query_text, top_k=top_k)

def query_memory(question, llm_client=None):
    """
    Process a natural language question about memories using LLM.
    This is different from search - it uses LLM to understand and answer questions.
    """
    from .memory import search_memories
    
    # First, search for relevant memories
    relevant_memories = search_memories(question, top_k=5)
    
    if not relevant_memories:
        return "I don't have any memories related to that question."
    
    if llm_client is None:
        # Simple fallback - just return the most relevant memory
        return relevant_memories[0].get('text', 'No memory text available')
    
    # Use LLM to synthesize an answer from relevant memories
    memory_texts = [mem.get('text', '') for mem in relevant_memories]
    context = "\n".join([f"Memory {i+1}: {text}" for i, text in enumerate(memory_texts)])
    
    prompt = f"""Based on these memories, answer the following question:

Question: {question}

Relevant memories:
{context}

Answer:"""
    
    try:
        response = llm_client.query(prompt, max_tokens=200, temperature=0.7)
        return response
    except Exception as e:
        print(f"LLM query failed: {e}")
        # Fallback to simple response
        return f"Based on your memories: {memory_texts[0] if memory_texts else 'No relevant memories found'}" 