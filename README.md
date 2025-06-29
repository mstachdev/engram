# Engram - Save you

An app to store your memories. 
Write fragments - free form, free word order. 
AI structures the fragments into "engrams".
Talk to your engrams / talk to yourself.

## Architecture

**Engram** has a modular architecture with three main modules:

### 🧠 **Cortex** (Information Processing)
- **Purpose**: Handles information intake and memory building
- **Functions**: 
  - Processes raw text input and uploaded files
  - Extracts meaningful fragments from unstructured data
  - Stores fragments in SQLite database for fast access
  - **NEW**: Builds memories from fragments using vLLM (moved from Flutter client)
- **Database**: SQLite (fragments.db) - can sync to cloud for mobile apps
- **API**: `/api/cortex/*` endpoints
- **Analogy**: Like the brain's sensory cortex that processes incoming information

### 🌊 **Hippocampus** (Memory Consolidation)  
- **Purpose**: Advanced memory management and querying
- **Functions**:
  - Stores structured memories (engrams) with embeddings
  - Enables semantic search and retrieval
  - Natural language memory queries
  - Memory completion and enhancement
- **Database**: Letta (vector database) - for semantic memory storage
- **API**: `/api/hippocampus/*` endpoints
- **Analogy**: Like the brain's hippocampus that consolidates episodic memories

### 👁️ **Vision** (Visual Processing) - *Coming Soon*
- **Purpose**: Image and visual content processing
- **Functions**:
  - Image analysis and description
  - OCR (text extraction from images)
  - Visual memory creation
- **API**: `/api/vision/*` endpoints (placeholder)
- **Analogy**: Like the brain's visual cortex

### 📱 **Data Flow**
```
Raw Input → Cortex (extract fragments + build memories) → Hippocampus (consolidate + query) → Long-term Storage
```

### 🔧 **Technical Architecture**
- **Modular API**: Each module has its own `api.py` with Flask Blueprints
- **Centralized vLLM**: All LLM communication goes through Flask backend (security)
- **Shared Utilities**: Common LLM client and response formatting in `/llm`
- **Unified Dependencies**: Single `requirements.txt` for the entire project

## Project Structure
```
engram/
│
├── main_app.py                  # UNIFIED: Web application launcher with modular API
├── search_database.py           # Database search utility
├── fragments.txt                # Fragment storage file
├── requirements.txt             # UNIFIED: All project dependencies
├── TODO.md                      # Project todo list
├── murrinhpatha-free-word-order-article-2023.pdf  # Research document
├── llm/                         # NEW: LLM utilities and vLLM management
│   ├── __init__.py
│   ├── client.py                # Unified LLM client for all modules
│   ├── responses.py             # Standardized API responses
│   └── start_vllm.py            # Python script to launch vLLM server
├── cortex/                      # Cortex module (information processing)
│   ├── __init__.py
│   ├── api.py                   # UPDATED: Flask Blueprint with all endpoints
│   ├── database.py              # SQLite fragment storage
│   ├── processor.py             # Fragment extraction logic
│   └── data/                    # SQLite database storage
│       └── fragments.db         # Fragment database
├── hippocampus/                 # Hippocampus module (memory consolidation)
│   ├── __init__.py
│   ├── api.py                   # NEW: Flask Blueprint with memory endpoints
│   ├── llm.py                   # LLM client for vLLM server
│   ├── memory.py                # Letta memory storage
│   ├── completion.py            # Memory building logic
│   ├── query.py                 # Memory retrieval
│   └── data/                    # Letta database storage
├── vision/                      # NEW: Vision module (placeholder)
│   ├── __init__.py
│   └── api.py                   # Flask Blueprint with vision endpoints
├── flutter_app/                 # Flutter web app
│   ├── lib/
│   │   └── main.dart            # UPDATED: Uses new API endpoints
│   ├── web/                     # Web assets
│   │   ├── index.html
│   │   ├── manifest.json
│   │   ├── favicon.png
│   │   └── icons/               # App icons
│   ├── test/
│   │   └── widget_test.dart     # Flutter tests
│   ├── pubspec.yaml             # Flutter dependencies
│   ├── pubspec.lock
│   ├── analysis_options.yaml
│   └── README.md                # Flutter app documentation
├── venv/                        # Python virtual environment
├── .gitignore
└── README.md
```

## Setup

### 1. Install Dependencies
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Start the vLLM Server 
```bash
python llm/start_vllm.py --model /path/to/your/model
```

**Alternative (legacy shell script - removed):**
The shell script has been replaced by the Python version for better cross-platform support.

## Usage

### 🌐 Web Interface
Start the web application:
```bash
python main_app.py
```
Then open your browser to: `http://localhost:5000`

**Features:**
1. **Add Fragments**: Enter text or upload files
2. **Review Fragments**: See extracted fragments in the collection
3. **Select & Process**: Choose fragments to build into memories
4. **View Results**: See the AI-generated narrative memory

### 💻 Simplified Interface
The CLI has been removed to simplify the project. All functionality is now available through the web interface at `http://localhost:5000`.

### 🔌 API Endpoints

**NEW Modular API Structure (http://localhost:5000):**

**Global:**
- `GET /api/health` - System health check

**Cortex Module (`/api/cortex/`):**
- `POST /api/cortex/fragments` - Add fragments from text
- `POST /api/cortex/fragments/file` - Upload file and extract fragments  
- `GET /api/cortex/fragments` - Get stored fragments
- `POST /api/cortex/memory/build` - **NEW**: Build memory from content (moved from Flutter)
- `GET /api/cortex/sessions` - Get all sessions
- `POST /api/cortex/sessions` - Create new session
- `GET /api/cortex/models` - Get available vLLM models

**Hippocampus Module (`/api/hippocampus/`):**
- `POST /api/hippocampus/memories` - Create new memory
- `GET /api/hippocampus/memories` - Get stored memories
- `POST /api/hippocampus/memories/query` - Query memories semantically
- `GET /api/hippocampus/health` - Hippocampus module status

**Vision Module (`/api/vision/`):**
- `GET /api/vision/health` - Vision module status (placeholder)

## Configuration
- **GPU Memory**: Modify `llm/start_vllm.py` (default: 80% VRAM)
- **Model Path**: Pass as argument to vLLM launcher
- **API Port**: Change port in `main_app.py`
- **Database Paths**: Modify paths in `cortex/database.py` and `hippocampus/memory.py`

## Quick Start

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Start vLLM server**: `python llm/start_vllm.py --model /path/to/model`
3. **Start the web interface**:
   - **Web**: `python main_app.py` → http://localhost:5000

## What's New in This Version

### 🔄 **Major Refactoring - Simplified Modular Architecture**
- **Moved vLLM calls from Flutter to Flask**: Better security and architecture
- **Flask Blueprints**: Each module (`cortex`, `hippocampus`, `vision`) has its own API namespace
- **Unified LLM Client**: All modules use shared LLM utilities in `/llm`
- **Single Requirements File**: Simplified dependency management
- **Python vLLM Launcher**: Replace shell script with Python for better cross-platform support
- **Simplified Entry Point**: Single `main_app.py` handles everything (removed CLI and separate API files)

### 🛡️ **Security & Architecture Improvements**
- **No Direct vLLM Access**: Flutter app no longer calls vLLM directly
- **Centralized API**: All AI operations go through Flask backend
- **Modular Design**: Easy to add new modules (vision, audio, etc.)
- **Better Error Handling**: Standardized API responses across all modules

### 📱 **Flutter App Updates**
- **New API Endpoints**: Updated to use `/api/cortex/memory/build` instead of direct vLLM
- **Better Error Messages**: Improved user feedback
- **Maintained Functionality**: All existing features work the same way

## Mobile App Development
The Flutter app is in development. The SQLite-based cortex database is designed for easy cloud synchronization, making it perfect for mobile applications.

## Neuroanatomical Accuracy
This architecture mirrors how the human brain processes and stores memories:
- **Cortex**: Processes sensory input → extracts relevant information
- **Hippocampus**: Consolidates information → creates episodic memories  
- **Storage**: Distributed between working memory (cortex) and long-term memory (hippocampus)

## Requirements
- Python 3.9+
- vLLM (for hippocampus)
- Flask + SQLite (for cortex)
- 8GB+ VRAM recommended

## License
MIT 