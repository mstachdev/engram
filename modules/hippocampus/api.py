from flask import Blueprint, request
import os
import sys
from .memory import make_memory, add_memory, get_memories, search_memories
from .query import query_memory
from .memory import process_fragments

# Import shared utilities from the llm directory
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from llm.responses import success_response, error_response, validation_error, server_error
from llm.client import create_llm_client
hippocampus_llm = create_llm_client("hippocampus")

# Create blueprint for hippocampus routes
hippocampus_bp = Blueprint('hippocampus', __name__, url_prefix='/api/hippocampus')

@hippocampus_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for hippocampus module."""
    return success_response({"status": "healthy", "module": "hippocampus"})

@hippocampus_bp.route('/memories', methods=['POST'])
def create_memory():
    """Create a new memory from text."""
    data = request.get_json()
    
    if not data or 'text' not in data:
        return validation_error("Text content required", "text")
    
    text = data['text']
    source = data.get('source', 'direct_input')
    fragments = data.get('fragments', [])
    metadata = data.get('metadata', {})
    
    try:
        memory = make_memory(
            text=text,
            source=source,
            fragments=fragments,
            metadata=metadata
        )
        
        add_memory(memory)
        
        return success_response(memory, "Memory created successfully")
    except Exception as e:
        return server_error(f"Error creating memory: {str(e)}")

@hippocampus_bp.route('/memories', methods=['GET'])
def get_memories_endpoint():
    """Get memories from the database."""
    limit = request.args.get('limit', type=int)
    source = request.args.get('source')
    
    try:
        memories = get_memories(limit=limit, source=source)
        return success_response({"memories": memories})
    except Exception as e:
        return server_error(f"Error retrieving memories: {str(e)}")

@hippocampus_bp.route('/memories/search', methods=['POST'])
def search_memories_endpoint():
    """Search memories by query."""
    data = request.get_json()
    
    if not data or 'query' not in data:
        return validation_error("Search query required", "query")
    
    query = data['query']
    limit = data.get('limit', 10)
    
    try:
        results = search_memories(query, limit=limit)
        return success_response({"results": results, "query": query})
    except Exception as e:
        return server_error(f"Error searching memories: {str(e)}")

@hippocampus_bp.route('/memories/query', methods=['POST'])
def query_memory_endpoint():
    """Query memories using natural language."""
    data = request.get_json()
    
    if not data or 'question' not in data:
        return validation_error("Question required", "question")
    
    question = data['question']
    
    try:
        # Use hippocampus LLM client for memory querying
        response = query_memory(question, llm_client=hippocampus_llm)
        
        if response is None:
            return server_error("Failed to process memory query")
        
        return success_response({
            "question": question,
            "response": response
        }, "Memory query processed successfully")
    except Exception as e:
        return server_error(f"Error processing memory query: {str(e)}")

@hippocampus_bp.route('/fragments/process', methods=['POST'])
def process_fragments_endpoint():
    """Process fragments into a structured memory."""
    data = request.get_json()
    
    if not data or 'fragments' not in data:
        return validation_error("Fragments required", "fragments")
    
    fragments = data['fragments']
    source = data.get('source', 'fragment_processing')
    metadata = data.get('metadata', {})
    
    if not isinstance(fragments, list) or not fragments:
        return validation_error("Fragments must be a non-empty list", "fragments")
    
    try:
        memory = process_fragments(
            fragments=fragments,
            source=source,
            metadata=metadata
        )
        
        return success_response(memory, "Fragments processed into memory successfully")
    except Exception as e:
        return server_error(f"Error processing fragments: {str(e)}")


@hippocampus_bp.route('/models', methods=['GET'])
def get_available_models():
    """Get available models from vLLM server."""
    try:
        models = hippocampus_llm.get_available_models()
        if models is None:
            return server_error("Could not retrieve models from vLLM server")
        return success_response(models)
    except Exception as e:
        return server_error(f"Error retrieving models: {str(e)}")

# Legacy functions for backward compatibility and standalone usage
from flask import Flask
from flask_cors import CORS

def create_standalone_app():
    """Create a standalone Flask app with just hippocampus functionality."""
    app = Flask(__name__)
    CORS(app)
    
    app.register_blueprint(hippocampus_bp)
    
    return app

def run_api(host='localhost', port=5001, debug=True):
    """Run the standalone hippocampus API server."""
    app = create_standalone_app()
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_api() 