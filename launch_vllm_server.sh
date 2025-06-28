#!/bin/bash

MODEL_PATH="${VLLM_MODEL_PATH}"
if [ -n "$1" ]; then
  MODEL_PATH="$1"
fi

if [ -z "${MODEL_PATH}" ]; then
  echo "Error: Please provide a model path as an argument or set the VLLM_MODEL_PATH environment variable."
  exit 1
fi

echo "Launching vLLM server with model: ${MODEL_PATH}"

python -m vllm.entrypoints.openai.api_server \
    --model "${MODEL_PATH}" \
    --gpu-memory-utilization 0.8 \
    --max-model-len 2048 \
    --enforce-eager