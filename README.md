# Engram

A memory system using free text with free word order - with AI building the memories and helping access.

## Architecture

**Engram** has two main modules:

### 🧠 **Cortex** (Information Processing)
- **Purpose**: Handles information intake
- **Functions**: 
  - Processes raw text input and uploaded files
  - Extracts meaningful fragments from unstructured data
  - Stores fragments in SQLite database for fast access
  - Provides web interface for user interaction
- **Database**: SQLite (fragments.db) - can sync to cloud for mobile apps
- **Analogy**: Like the brain's sensory cortex that processes incoming information

### 🌊 **Hippocampus** (Memory Consolidation)  
- **Purpose**: Consolidates fragments into structured, narrative memories
- **Functions**:
  - Takes fragments from cortex and creates coherent stories
  - Uses LLM to fill gaps and embellish memories
  - Stores consolidated memories with embeddings
  - Enables semantic search and retrieval
- **Database**: Letta (vector database) - for semantic memory storage
- **Analogy**: Like the brain's hippocampus that consolidates episodic memories

### 📱 **Data Flow**
```
Raw Input → Cortex (extract fragments) → Hippocampus (consolidate memory) → Long-term Storage
```

## Database Architecture

### **Cortex Database (SQLite)**
- **Content**: Raw fragments, metadata, processing status
- **Purpose**: Fast input, temporary storage, preprocessing  
- **Tables**: fragments, sessions, fragment_sessions
- **Benefits**: Local storage, can sync to cloud (Firebase/Supabase)

### **Hippocampus Database (Letta)**
- **Content**: Consolidated memories with semantic embeddings
- **Purpose**: Long-term storage, similarity search, RAG
- **Benefits**: Vector search, semantic retrieval, AI-ready

## Features
- 🧩 **Fragment Extraction**: Automatic extraction from text and files
- 🌐 **Web Interface**: Modern, responsive UI for fragment input
- 💻 **CLI Interface**: Interactive command-line interface
- 📁 **File Upload**: Support for text files, documents
- 🔄 **Session Management**: Group related fragments together
- 🧠 **Memory Consolidation**: AI-powered story creation from fragments
- 🔍 **Smart Search**: Vector-based semantic memory retrieval
- 📊 **Metadata Tracking**: Automatic timestamps, sources, processing status
- 🚀 **Mobile Ready**: SQLite + cloud sync architecture

## Project Structure
```
engram/
│
├── main_cli.py                  # CLI interface launcher
├── main_app.py                  # Web application launcher
├── launch_vllm_server.sh        # vLLM server launcher
├── cortex/                      # Cortex module (information processing)
│   ├── __init__.py
│   ├── api.py                   # Flask API server
│   ├── database.py              # SQLite fragment storage
│   ├── processor.py             # Fragment extraction logic
│   ├── requirements.txt         # Cortex dependencies
│   ├── static/                  # Web interface
│   │   └── index.html           # Modern web UI
│   └── data/                    # SQLite database storage
│       └── fragments.db         # Fragment database
├── hippocampus/                 # Hippocampus module (memory consolidation)
│   ├── __init__.py
│   ├── llm.py                   # LLM client for vLLM server
│   ├── memory.py                # Letta memory storage
│   ├── completion.py            # Memory consolidation logic
│   ├── query.py                 # Memory retrieval
│   ├── requirements.txt         # Hippocampus dependencies
│   └── data/                    # Letta database
│       └── memories.letta       # Consolidated memories
├── flutter_app/                 # Flutter mobile app (in development)
├── requirements.txt             # Combined dependencies
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

### 2. Start the vLLM Server (Hippocampus)
```bash
./launch_vllm_server.sh /path/to/your/model
```

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
3. **Select & Process**: Choose fragments to consolidate into memories
4. **View Results**: See the AI-generated narrative memory

### 💻 Command Line Interface
Start the interactive CLI:
```bash
python main_cli.py
```

**Interactive Commands:**
- `add <text>` - Add fragments from text
- `memory <fragment1> <fragment2>` - Create memory directly from fragments
- `list` - Show stored fragments
- `process` - Process stored fragments into memory
- `test` - Test hippocampus connection
- `help` - Show available commands
- `quit` - Exit

**Direct Commands:**
```bash
python main_cli.py memory "walked dog" "sunny day" "beautiful park"
python main_cli.py add "Had coffee this morning. Weather was nice."
python main_cli.py process --all
python main_cli.py test
python main_cli.py list
```

### 🔌 API Endpoints

**Cortex API (http://localhost:5000):**
- `POST /fragments` - Add fragments from text
- `POST /fragments/file` - Upload file and extract fragments  
- `GET /fragments` - Get stored fragments
- `POST /fragments/process` - Process fragments → hippocampus
- `GET /sessions` - Get all sessions
- `POST /sessions` - Create new session

## Configuration
- **GPU Memory**: Modify `launch_vllm_server.sh` (default: 80% VRAM)
- **Model Path**: Set `VLLM_MODEL_PATH` environment variable
- **API Port**: Change port in `main_app.py`
- **Database Paths**: Modify paths in `cortex/database.py` and `hippocampus/memory.py`

## Quick Start

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Start vLLM server**: `./launch_vllm_server.sh /path/to/model`
3. **Choose your interface**:
   - **Web**: `python main_app.py` → http://localhost:5000
   - **CLI**: `python main_cli.py` → Interactive mode

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