import re
from typing import List, Dict, Any
from .database import add_fragment, get_fragments, mark_fragments_processed

def extract_fragments_from_text(text: str, source: str = "text_input") -> List[str]:
    """
    Extract meaningful fragments from raw text input.
    This is a simple implementation that can be enhanced with NLP.
    """
    # Remove extra whitespace and split by common delimiters
    fragments = []
    
    # Split by sentences first
    sentences = re.split(r'[.!?]+', text)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # For short sentences, keep as single fragment
        if len(sentence.split()) <= 5:
            fragments.append(sentence)
        else:
            # For longer sentences, split by commas and conjunctions
            parts = re.split(r'[,;]|\sand\s|\sor\s|\sbut\s', sentence)
            for part in parts:
                part = part.strip()
                if part and len(part.split()) >= 2:  # At least 2 words
                    fragments.append(part)
    
    return [f for f in fragments if f]

def extract_fragments_from_file(file_content: str, filename: str) -> List[str]:
    """
    Extract fragments from uploaded file content.
    Can be enhanced to handle different file types.
    """
    source = f"file:{filename}"
    
    # For now, treat file content as text
    return extract_fragments_from_text(file_content, source)

def process_fragments_to_memory(fragment_ids: List[str], session_id: str = None) -> Dict[str, Any]:
    """
    Process a set of fragments into a consolidated memory using the hippocampus.
    """
    # Get fragments from database
    fragments_data = []
    for frag_id in fragment_ids:
        frags = get_fragments()
        fragment = next((f for f in frags if f['id'] == frag_id), None)
        if fragment:
            fragments_data.append(fragment)
    
    if not fragments_data:
        return {"error": "No fragments found"}
    
    # Extract just the content for hippocampus processing
    fragment_contents = [f['content'] for f in fragments_data]
    
    # Import hippocampus functions (the renamed cortex module)
    try:
        from hippocampus.completion import process_fragments
        
        # Process fragments into memory
        memory = process_fragments(
            fragment_contents, 
            source="cortex_processing",
            metadata={
                "session_id": session_id,
                "fragment_count": len(fragment_contents),
                "original_fragments": fragment_ids
            }
        )
        
        # Mark fragments as processed
        mark_fragments_processed(fragment_ids, memory.get('id'))
        
        return {
            "success": True,
            "memory": memory,
            "processed_fragments": len(fragment_ids)
        }
        
    except ImportError as e:
        return {"error": f"Could not import hippocampus module: {e}"}
    except Exception as e:
        return {"error": f"Error processing fragments: {e}"}

def add_fragments_from_input(text: str, source: str = "user_input", session_id: str = None) -> Dict[str, Any]:
    """
    Add fragments from user input text.
    """
    fragments = extract_fragments_from_text(text, source)
    
    if not fragments:
        return {"error": "No fragments could be extracted from input"}
    
    fragment_ids = []
    for fragment in fragments:
        frag_id = add_fragment(
            content=fragment,
            source=source,
            session_id=session_id
        )
        fragment_ids.append(frag_id)
    
    return {
        "success": True,
        "fragments_added": len(fragments),
        "fragment_ids": fragment_ids,
        "fragments": fragments
    }

def add_fragments_from_file(file_content: str, filename: str, session_id: str = None) -> Dict[str, Any]:
    """
    Add fragments from uploaded file.
    """
    fragments = extract_fragments_from_file(file_content, filename)
    
    if not fragments:
        return {"error": "No fragments could be extracted from file"}
    
    fragment_ids = []
    source = f"file:{filename}"
    
    for fragment in fragments:
        frag_id = add_fragment(
            content=fragment,
            source=source,
            session_id=session_id
        )
        fragment_ids.append(frag_id)
    
    return {
        "success": True,
        "fragments_added": len(fragments),
        "fragment_ids": fragment_ids,
        "fragments": fragments,
        "filename": filename
    } 