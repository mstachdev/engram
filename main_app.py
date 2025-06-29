#!/usr/bin/env python3
"""
Engram Web App - Flask Web Interface Launcher

This launches the web application for fragment input and memory creation.
"""

import sys
import os
from flask import Flask, send_from_directory
from flask_cors import CORS

def main():
    print("=" * 60)
    print("🧠 Engram Web Application")
    print("=" * 60)
    print()
    
    # Check if modules are available
    modules_status = []
    
    try:
        from modules.cortex.api import cortex_bp
        print("✓ Cortex module available")
        modules_status.append("cortex")
    except ImportError as e:
        print(f"⚠️  Cortex module not available: {e}")
    
    try:
        from modules.hippocampus.api import hippocampus_bp
        print("✓ Hippocampus module available")
        modules_status.append("hippocampus")
    except ImportError as e:
        print(f"⚠️  Hippocampus module not available: {e}")
        
    try:
        from modules.vision.api import vision_bp
        print("✓ Vision module available")
        modules_status.append("vision")
    except ImportError as e:
        print(f"⚠️  Vision module not available: {e}")
    
    print(f"Starting Engram Modular API with {len(modules_status)} modules...")
    print()
    print("🌐 Web Interface: http://localhost:5000")
    print("📱 Mobile friendly: Access from any device on your network")
    print()
    print("Modules loaded:", ", ".join(modules_status))
    print()
    print("Features available:")
    print("  • Fragment extraction from text input")
    print("  • File upload and processing")
    print("  • Memory building with vLLM (moved from client)")
    print("  • Memory consolidation via hippocampus")
    print("  • Session management")
    print("  • Vision processing (placeholder)")
    print()
    print("API Endpoints:")
    print("  Global:")
    print("    GET  /api/health                    - System health check")
    print("  Cortex:")
    print("    POST /api/cortex/fragments          - Add fragments from text")
    print("    POST /api/cortex/fragments/file     - Upload file and extract fragments")
    print("    GET  /api/cortex/fragments          - Get stored fragments")
    print("    POST /api/cortex/memory/build       - Build memory from content")
    print("    GET  /api/cortex/sessions           - Get all sessions")
    print("    POST /api/cortex/sessions           - Create new session")
    print("  Hippocampus:")
    print("    POST /api/hippocampus/memories      - Create new memory")
    print("    GET  /api/hippocampus/memories      - Get memories")
    print("    POST /api/hippocampus/memories/query - Query memories")
    print("  Vision:")
    print("    GET  /api/vision/health             - Vision module status")
    print()
    print("Prerequisites:")
    print("  1. Start vLLM server: python llm/start_vllm.py --model /path/to/model")
    print("  2. Install dependencies: pip install -r requirements.txt")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Start the Flask server
        app = create_app()
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except ImportError as e:
        print(f"❌ Error importing modular API: {e}")
        print("Make sure Flask and other dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down Engram web server...")
        print("Thanks for using Engram!")
        
    except Exception as e:
        print(f"❌ Error starting web server: {e}")
        sys.exit(1)

def create_app():
    """Create and configure the Flask application."""
    # Add the project root to the path
    sys.path.append(os.path.dirname(__file__))
    
    from modules.cortex.api import cortex_bp
    from modules.hippocampus.api import hippocampus_bp
    from modules.vision.api import vision_bp
    from llm.responses import success_response
    
    app = Flask(__name__)
    CORS(app)  # Enable CORS for Flutter web app
    
    # Register module blueprints
    app.register_blueprint(cortex_bp)
    app.register_blueprint(hippocampus_bp)
    app.register_blueprint(vision_bp)
    
    # Root health check
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Global health check endpoint."""
        return success_response({
            "status": "healthy", 
            "service": "engram-api",
            "modules": ["cortex", "hippocampus", "vision"]
        })
    
    # Serve Flutter web app
    @app.route('/')
    def index():
        """Serve the Flutter web app."""
        flutter_build_path = os.path.join(
            os.path.dirname(__file__), 
            'flutter_app', 'build', 'web'
        )
        return send_from_directory(flutter_build_path, 'index.html')

    @app.route('/<path:filename>')
    def flutter_static(filename):
        """Serve Flutter web app static files."""
        flutter_build_path = os.path.join(
            os.path.dirname(__file__), 
            'flutter_app', 'build', 'web'
        )
        try:
            return send_from_directory(flutter_build_path, filename)
        except:
            # If file not found, serve index.html for Flutter routing
            return send_from_directory(flutter_build_path, 'index.html')
    
    return app

if __name__ == "__main__":
    main() 