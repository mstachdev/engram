# Engram

The app is called Engram. 

"Cortex" is the first module / use case. The purpose of cortex is to piece together memories from fragments (user inputs). These fragments can have free word order to enable easy and fast entry. The llm in the cortex will figure out the relationship between words in this free order and create a short story. This created short story is intended to be a helpful embellishment on the memory. So, cortex takes free-word-order fragments of text and structures a candidate memory.

## Features
- Fast, easy memory entry using unordered words/fragments
- The `cortex` module reconstructs and embellishes memories from fragments using an LLM
- Memories stored with metadata and embeddings for search and RAG
- Query interface to retrieve relevant memories
- Automatic metadata collection (hostname, user, git commit, timestamps, etc.)
- Local vLLM server integration with automatic model name detection

## Project Structure
```
engram/
│
├── main.py                      # Main entry point for the Engram app
├── cortex/                      # Cortex module for memory reconstruction
│   ├── __init__.py
│   ├── llm.py                   # LLM client for vLLM server communication
│   ├── memory.py                # Memory data model and Letta storage
│   ├── completion.py            # Text completion logic
│   ├── query.py                 # Query logic
│   ├── launch_vllm_server.sh    # Shell script to launch vLLM server
│   ├── main.py                  # Cortex-specific entry point
│   ├── requirements.txt         # Python dependencies
│   └── data/                    # Data storage directory
│       └── memories.letta       # Letta database for memories
├── .gitignore                   # Git ignore file (excludes venvs, metadata, etc.)
└── README.md                    # This file
```

## Setup
1. Create a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate      # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r cortex/requirements.txt
   ```

3. Make the launch script executable (Linux/Mac):
   ```bash
   chmod +x cortex/launch_vllm_server.sh
   ```

## Usage

### 1. Start the vLLM Server
First, launch the vLLM server with your model:
```bash
./cortex/launch_vllm_server.sh /path/to/your/safetensors/model
```

The server will:
- Load your model with GPU memory utilization set to 0.8 (for 8GB VRAM)
- Start listening on `http://localhost:8000/v1`
- Automatically save metadata about the server launch to `cortex/metadata/`

### 2. Use the Engram App
In a separate terminal, run the main application:

**Test the connection:**
```bash
python main.py test
```

**Create a memory from fragments:**
```bash
python main.py memory "walked dog" "sunny day" "beautiful park"
```

**Get help:**
```bash
python main.py
```

## Configuration
- **GPU Memory**: The vLLM server is configured to use 80% of GPU memory (0.8). You can modify this in `cortex/launch_vllm_server.sh`
- **Model Path**: Pass the model path as an argument to the launch script, or set the `VLLM_MODEL_PATH` environment variable
- **Server URL**: The LLM client automatically connects to `http://localhost:8000/v1` and detects the model name

## Metadata Collection
The system automatically collects metadata for each server launch and memory creation:
- Timestamps (UTC)
- Hostname and user information
- Git commit hash (for reproducibility)
- Process IDs
- Python and vLLM versions
- Model paths and configurations

## Requirements
- Python 3.9+
- vLLM
- OpenAI Python client
- Letta
- 8GB+ VRAM (configured for 80% utilization)

## License
MIT 