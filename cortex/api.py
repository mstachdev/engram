from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import base64
import json
import os
from .database import get_fragments, get_sessions, create_session
from .processor import (
    add_fragments_from_input, 
    add_fragments_from_file, 
    process_fragments_to_memory
)

app = Flask(__name__)
CORS(app)  # Enable CORS for Flutter web app

# Serve Flutter web app
@app.route('/')
def index():
    """Serve the Flutter web app."""
    flutter_build_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'flutter_app', 'build', 'web')
    return send_from_directory(flutter_build_path, 'index.html')

@app.route('/<path:filename>')
def flutter_static(filename):
    """Serve Flutter web app static files."""
    flutter_build_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'flutter_app', 'build', 'web')
    try:
        return send_from_directory(flutter_build_path, filename)
    except:
        # If file not found, serve index.html for Flutter routing
        return send_from_directory(flutter_build_path, 'index.html')

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "cortex"})

@app.route('/fragments', methods=['POST'])
def add_fragments():
    """Add fragments from text input."""
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({"error": "Text input required"}), 400
    
    text = data['text']
    session_id = data.get('session_id')
    source = data.get('source', 'web_input')
    
    result = add_fragments_from_input(text, source, session_id)
    
    if 'error' in result:
        return jsonify(result), 400
    
    return jsonify(result)

@app.route('/fragments/file', methods=['POST'])
def upload_file():
    """Upload file and extract fragments."""
    data = request.get_json()
    
    if not data or 'file_content' not in data or 'filename' not in data:
        return jsonify({"error": "File content and filename required"}), 400
    
    try:
        # Decode base64 file content
        file_content = base64.b64decode(data['file_content']).decode('utf-8')
        filename = data['filename']
        session_id = data.get('session_id')
        
        result = add_fragments_from_file(file_content, filename, session_id)
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"Error processing file: {str(e)}"}), 400

@app.route('/fragments', methods=['GET'])
def get_fragments_endpoint():
    """Get fragments from database."""
    session_id = request.args.get('session_id')
    processed = request.args.get('processed')
    limit = request.args.get('limit', type=int)
    
    # Convert processed string to boolean
    if processed is not None:
        processed = processed.lower() == 'true'
    
    fragments = get_fragments(session_id, processed, limit)
    return jsonify({"fragments": fragments})

@app.route('/fragments/process', methods=['POST'])
def process_fragments():
    """Process selected fragments into memory."""
    data = request.get_json()
    
    if not data or 'fragment_ids' not in data:
        return jsonify({"error": "Fragment IDs required"}), 400
    
    fragment_ids = data['fragment_ids']
    session_id = data.get('session_id')
    
    if not fragment_ids:
        return jsonify({"error": "At least one fragment ID required"}), 400
    
    result = process_fragments_to_memory(fragment_ids, session_id)
    
    if 'error' in result:
        return jsonify(result), 400
    
    return jsonify(result)

@app.route('/sessions', methods=['GET'])
def get_sessions_endpoint():
    """Get all sessions."""
    sessions = get_sessions()
    return jsonify({"sessions": sessions})

@app.route('/sessions', methods=['POST'])
def create_session_endpoint():
    """Create a new session."""
    data = request.get_json()
    
    name = data.get('name') if data else None
    metadata = data.get('metadata') if data else None
    
    session_id = create_session(name, metadata)
    return jsonify({"session_id": session_id, "name": name})

@app.route('/sessions/<session_id>/fragments', methods=['GET'])
def get_session_fragments(session_id):
    """Get fragments for a specific session."""
    processed = request.args.get('processed')
    limit = request.args.get('limit', type=int)
    
    if processed is not None:
        processed = processed.lower() == 'true'
    
    fragments = get_fragments(session_id, processed, limit)
    return jsonify({"fragments": fragments, "session_id": session_id})

def run_api(host='localhost', port=5000, debug=True):
    """Run the Flask API server."""
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_api() 