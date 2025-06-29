from flask import Blueprint, request
import os
import sys

# Import shared utilities from the llm directory
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from llm.responses import success_response, error_response, validation_error, server_error
from llm.client import create_llm_client
vision_llm = create_llm_client("vision")

# Create blueprint for vision routes
vision_bp = Blueprint('vision', __name__, url_prefix='/api/vision')

@vision_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for vision module."""
    return success_response({
        "status": "healthy", 
        "module": "vision",
        "note": "Vision module is not yet implemented"
    })

@vision_bp.route('/analyze', methods=['POST'])
def analyze_image():
    """Analyze an image using vision models (placeholder)."""
    data = request.get_json()
    
    if not data or 'image' not in data:
        return validation_error("Image data required", "image")
    
    # TODO: Implement image analysis
    return success_response({
        "analysis": "Image analysis not yet implemented",
        "note": "This endpoint is a placeholder for future vision functionality"
    }, "Analysis placeholder")

@vision_bp.route('/describe', methods=['POST'])
def describe_image():
    """Generate a description of an image (placeholder)."""
    data = request.get_json()
    
    if not data or 'image' not in data:
        return validation_error("Image data required", "image")
    
    # TODO: Implement image description using vision_llm
    return success_response({
        "description": "Image description not yet implemented",
        "note": "This endpoint is a placeholder for future vision functionality"
    }, "Description placeholder")

@vision_bp.route('/extract', methods=['POST'])
def extract_text():
    """Extract text from an image using OCR (placeholder)."""
    data = request.get_json()
    
    if not data or 'image' not in data:
        return validation_error("Image data required", "image")
    
    # TODO: Implement OCR functionality
    return success_response({
        "extracted_text": "OCR not yet implemented",
        "note": "This endpoint is a placeholder for future OCR functionality"
    }, "OCR placeholder")

@vision_bp.route('/models', methods=['GET'])
def get_available_models():
    """Get available vision models (placeholder)."""
    try:
        # TODO: When vision models are available, use vision_llm.get_available_models()
        return success_response({
            "models": [],
            "note": "Vision models not yet configured"
        })
    except Exception as e:
        return server_error(f"Error retrieving vision models: {str(e)}")

# Legacy functions for backward compatibility and standalone usage
from flask import Flask
from flask_cors import CORS

def create_standalone_app():
    """Create a standalone Flask app with just vision functionality."""
    app = Flask(__name__)
    CORS(app)
    
    app.register_blueprint(vision_bp)
    
    return app

def run_api(host='localhost', port=5002, debug=True):
    """Run the standalone vision API server."""
    app = create_standalone_app()
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    run_api() 