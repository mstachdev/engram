from flask import Blueprint, request, send_from_directory
import base64
import os
from .database import get_fragments, get_sessions, create_session
from .processor import add_fragments_from_input, add_fragments_from_file, process_fragments_to_memory

# Import shared utilities from the llm directory
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
try:
    from llm.responses import success_response, error_response, validation_error, server_error
    from llm.client import create_llm_client
    cortex_llm = create_llm_client("cortex")
except ImportError:
    # Fallback for when api module is not available
    from flask import jsonify
    def success_response(data, message=None):
        response = {"success": True, "data": data}
        if message:
            response["message"] = message
        return jsonify(response)
    
    def error_response(error, status_code=400):
        return jsonify({"success": False, "error": error}), status_code
    
    def validation_error(message, field=None):
        return error_response(f"Validation error: {message}", 400)
    
    def server_error(message="Internal server error"):
        return error_response(message, 500)
    
    # Simple LLM client fallback
    class SimpleLLMClient:
        def query(self, prompt, system_message=None, max_tokens=1000, temperature=0.7):
            # This would need to be implemented if shared client is not available
            return None
        def get_available_models(self):
            return None
    
    cortex_llm = SimpleLLMClient()

# Create blueprint for cortex routes
cortex_bp = Blueprint('cortex', __name__, url_prefix='/api/cortex')

@cortex_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for cortex module."""
    return success_response({"status": "healthy", "module": "cortex"})

@cortex_bp.route('/fragments', methods=['POST'])
def add_fragments():
    """Add fragments from text input."""
    data = request.get_json()
    
    if not data or 'text' not in data:
        return validation_error("Text input required", "text")
    
    text = data['text']
    session_id = data.get('session_id')
    source = data.get('source', 'web_input')
    
    try:
        result = add_fragments_from_input(text, source, session_id)
        
        if 'error' in result:
            return error_response(result['error'])
        
        return success_response(result, "Fragments added successfully")
    except Exception as e:
        return server_error(f"Error adding fragments: {str(e)}")

@cortex_bp.route('/fragments/file', methods=['POST'])
def upload_file():
    """Upload file and extract fragments."""
    data = request.get_json()
    
    if not data or 'file_content' not in data or 'filename' not in data:
        return validation_error("File content and filename required")
    
    try:
        # Decode base64 file content
        file_content = base64.b64decode(data['file_content']).decode('utf-8')
        filename = data['filename']
        session_id = data.get('session_id')
        
        result = add_fragments_from_file(file_content, filename, session_id)
        
        if 'error' in result:
            return error_response(result['error'])
        
        return success_response(result, f"File {filename} processed successfully")
        
    except Exception as e:
        return server_error(f"Error processing file: {str(e)}")

@cortex_bp.route('/fragments', methods=['GET'])
def get_fragments_endpoint():
    """Get fragments from database."""
    session_id = request.args.get('session_id')
    processed = request.args.get('processed')
    limit = request.args.get('limit', type=int)
    
    # Convert processed string to boolean
    if processed is not None:
        processed = processed.lower() == 'true'
    
    try:
        fragments = get_fragments(session_id, processed, limit)
        return success_response({"fragments": fragments})
    except Exception as e:
        return server_error(f"Error retrieving fragments: {str(e)}")

@cortex_bp.route('/fragments/process', methods=['POST'])
def process_fragments():
    """Process selected fragments into memory using hippocampus."""
    data = request.get_json()
    
    if not data or 'fragment_ids' not in data:
        return validation_error("Fragment IDs required", "fragment_ids")
    
    fragment_ids = data['fragment_ids']
    session_id = data.get('session_id')
    
    if not fragment_ids:
        return validation_error("At least one fragment ID required", "fragment_ids")
    
    try:
        result = process_fragments_to_memory(fragment_ids, session_id)
        
        if 'error' in result:
            return error_response(result['error'])
        
        return success_response(result, "Fragments processed into memory")
    except Exception as e:
        return server_error(f"Error processing fragments: {str(e)}")

@cortex_bp.route('/memory/build', methods=['POST'])
def build_memory():
    """Build memory from raw content using vLLM (moved from Flutter)."""
    data = request.get_json()
    
    if not data or 'content' not in data:
        return validation_error("Content required", "content")
    
    content = data['content']
    source = data.get('source', 'text_input')
    
    try:
        # Use cortex LLM client to build memory
        system_message = "You are helping build memories from fragments of text. Try to infer what the user is writing about. Then, complete the thoughts so they are full sentences. Your task is add text to make the fragments the user provides seem like a complete journal entry. Do not add any new details but try to add words so there is clarity."
        
        prompt = f"Text to build into memory:\n{content}"
        
        built_content = cortex_llm.query(
            prompt=prompt,
            system_message=system_message,
            max_tokens=1000,
            temperature=0.7
        )
        
        if built_content is None:
            return server_error("Failed to generate memory content")
        
        return success_response({
            "built_content": built_content,
            "source": source,
            "original_content": content
        }, "Memory built successfully")
        
    except Exception as e:
        return server_error(f"Memory building failed: {str(e)}")

@cortex_bp.route('/sessions', methods=['GET'])
def get_sessions_endpoint():
    """Get all sessions."""
    try:
        sessions = get_sessions()
        return success_response({"sessions": sessions})
    except Exception as e:
        return server_error(f"Error retrieving sessions: {str(e)}")

@cortex_bp.route('/sessions', methods=['POST'])
def create_session_endpoint():
    """Create a new session."""
    data = request.get_json()
    
    name = data.get('name') if data else None
    metadata = data.get('metadata') if data else None
    
    try:
        session_id = create_session(name, metadata)
        return success_response({
            "session_id": session_id, 
            "name": name
        }, "Session created successfully")
    except Exception as e:
        return server_error(f"Error creating session: {str(e)}")

@cortex_bp.route('/sessions/<session_id>/fragments', methods=['GET'])
def get_session_fragments(session_id):
    """Get fragments for a specific session."""
    processed = request.args.get('processed')
    limit = request.args.get('limit', type=int)
    
    if processed is not None:
        processed = processed.lower() == 'true'
    
    try:
        fragments = get_fragments(session_id, processed, limit)
        return success_response({
            "fragments": fragments, 
            "session_id": session_id
        })
    except Exception as e:
        return server_error(f"Error retrieving session fragments: {str(e)}")

@cortex_bp.route('/models', methods=['GET'])
def get_available_models():
    """Get available models from vLLM server."""
    try:
        models = cortex_llm.get_available_models()
        if models is None:
            return server_error("Could not retrieve models from vLLM server")
        return success_response(models)
    except Exception as e:
        return server_error(f"Error retrieving models: {str(e)}")
