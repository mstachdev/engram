#!/usr/bin/env python3
"""
Script to start the vLLM server for Engram.
This replaces the existing launch_vllm_server.sh with a Python version.
"""

import subprocess
import sys
import os
import argparse
import time

def start_vllm_server(model_path: str, host: str = "localhost", port: int = 8000, gpu_memory_utilization: float = 0.8):
    """
    Start the vLLM server with specified parameters.
    
    Args:
        model_path: Path to the model directory
        host: Host to bind the server to
        port: Port to run the server on
        gpu_memory_utilization: GPU memory utilization ratio
    """
    
    print(f"Starting vLLM server...")
    print(f"Model: {model_path}")
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"GPU Memory Utilization: {gpu_memory_utilization}")
    print()
    
    # Check if model path exists
    if not os.path.exists(model_path):
        print(f"Error: Model path '{model_path}' does not exist!")
        sys.exit(1)
    
    # Build the vLLM command
    cmd = [
        "python", "-m", "vllm.entrypoints.openai.api_server",
        "--model", model_path,
        "--host", host,
        "--port", str(port),
        "--gpu-memory-utilization", str(gpu_memory_utilization),
        "--max-model-len", "2048",
        "--enforce-eager",
        "--served-model-name", os.path.basename(model_path.rstrip('/'))
    ]
    
    print("Running command:")
    print(" ".join(cmd))
    print()
    print("Server will be available at:")
    print(f"  http://{host}:{port}/v1/models")
    print(f"  http://{host}:{port}/v1/chat/completions")
    print()
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Start the vLLM server with real-time output
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Print output in real-time
        if process.stdout:
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    print(output.strip())
        
        # Wait for process to complete
        process.wait()
        
    except KeyboardInterrupt:
        print("\nShutting down vLLM server...")
        if 'process' in locals():
            process.terminate()
            process.wait()
    except FileNotFoundError:
        print("Error: vLLM is not installed or not in PATH")
        print("Install with: pip install vllm")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Start vLLM server for Engram")
    parser.add_argument(
        "--model", 
        default="../models/Qwen2.5-3B-Instruct-GPTQ-Int8/",
        help="Path to the model directory (default: ../models/Qwen2.5-3B-Instruct-GPTQ-Int8/)"
    )
    parser.add_argument(
        "--host", 
        default="localhost",
        help="Host to bind server to (default: localhost)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000,
        help="Port to run server on (default: 8000)"
    )
    parser.add_argument(
        "--gpu-memory-utilization", 
        type=float, 
        default=0.8,
        help="GPU memory utilization ratio (default: 0.8)"
    )
    
    args = parser.parse_args()
    
    start_vllm_server(
        model_path=args.model,
        host=args.host,
        port=args.port,
        gpu_memory_utilization=args.gpu_memory_utilization
    )

if __name__ == "__main__":
    main() 