# Engram - Save you

An app to store your memories. 
Write fragments - free form, free word order. 
AI structures the fragments into "engrams".
Talk to your engrams / talk to yourself.

## Architecture

**Engram** has two main modules:

### 🧠 **Cortex** (Information Processing)
- **Purpose**: Handles information intake
- **Functions**: 
  - Processes raw text input and uploaded files
  - Extracts meaningful fragments from unstructured data
  - Stores fragments in SQLite database for fast access
- **Database**: SQLite (fragments.db) - can sync to cloud for mobile apps
- **Analogy**: Like the brain's sensory cortex that processes incoming information

### 🌊 **Hippocampus** (Memory Building)  
- **Purpose**: Builds fragments into structured, narrative memories (called "engrams")
- **Functions**:
  - Uses LLM to fill gaps and embellish fragments into memories (called "engrams")
  - Stores engrams with embeddings
  - Enables semantic search and retrieval
- **Database**: Letta (vector database) - for semantic memory storage
- **Analogy**: Like the brain's hippocampus that consolidates episodic memories

### 📱 **Data Flow**
```
Raw Input → Cortex (extract fragments) → Hippocampus (build fragments into memory/engram) → Long-term Storage
```

## Project Structure
```
engram/
│
├── main_cli.py                  # CLI interface launcher
├── main_app.py                  # Web application launcher
├── launch_vllm_server.sh        # vLLM server launcher
├── search_database.py           # Database search utility
├── fragments.txt                # Fragment storage file
├── TODO.md                      # Project todo list
├── murrinhpatha-free-word-order-article-2023.pdf  # Research document
├── cortex/                      # Cortex module (information processing)
│   ├── __init__.py
│   ├── api.py                   # Flask API server
│   ├── database.py              # SQLite fragment storage
│   ├── processor.py             # Fragment extraction logic
│   ├── requirements.txt         # Cortex dependencies
│   └── data/                    # SQLite database storage
│       └── fragments.db         # Fragment database
├── hippocampus/                 # Hippocampus module (memory building)
│   ├── __init__.py
│   ├── llm.py                   # LLM client for vLLM server
│   ├── memory.py                # Letta memory storage
│   ├── completion.py            # Memory building logic
│   ├── query.py                 # Memory retrieval
│   ├── requirements.txt         # Hippocampus dependencies
│   └── data/                    # Letta database storage
├── flutter_app/                 # Flutter mobile app
│   ├── lib/
│   │   └── main.dart            # Main Flutter app with BuildMemoryPage
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
3. **Select & Process**: Choose fragments to build into memories
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