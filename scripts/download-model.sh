#!/bin/bash
# Script to download AI model for vLLM

set -e

MODEL_NAME="${VLLM_MODEL:-meta-llama/Meta-Llama-3-8B-Instruct}"
MODEL_DIR="/models"
AUTO_DOWNLOAD="${AUTO_DOWNLOAD_MODEL:-true}"

echo "==================================="
echo "vLLM Model Download Script"
echo "==================================="
echo "Model: $MODEL_NAME"
echo "Directory: $MODEL_DIR"
echo "Auto-download: $AUTO_DOWNLOAD"
echo "==================================="

# Extract model name (last part after /)
MODEL_FOLDER=$(basename "$MODEL_NAME")
MODEL_PATH="$MODEL_DIR/$MODEL_FOLDER"

# Check if model already exists
if [ -d "$MODEL_PATH" ] && [ "$(ls -A $MODEL_PATH)" ]; then
    echo "✓ Model already exists at: $MODEL_PATH"
    echo "✓ Skipping download"
    exit 0
fi

# Check if auto-download is enabled
if [ "$AUTO_DOWNLOAD" != "true" ]; then
    echo "⚠ Auto-download is disabled (AUTO_DOWNLOAD_MODEL=false)"
    echo "⚠ Please download the model manually to: $MODEL_PATH"
    echo ""
    echo "You can download using:"
    echo "  huggingface-cli download $MODEL_NAME --local-dir $MODEL_PATH"
    exit 1
fi

# Download model
echo "📥 Downloading model: $MODEL_NAME"
echo "📁 Destination: $MODEL_PATH"
echo ""

# Check if hf CLI is available
if ! command -v hf &> /dev/null; then
    echo "⚠ Hugging Face CLI not found. Installing..."
    pip install -U "huggingface_hub[cli]"
fi

# Download the model
echo "⏳ Starting download (this may take a while)..."

# Use HF_TOKEN if available
if [ -n "$HF_TOKEN" ]; then
    echo "🔑 Using Hugging Face token for authentication"
    huggingface-cli login --token "$HF_TOKEN" 2>/dev/null || hf auth login --token "$HF_TOKEN"
fi

# Use new hf command, fallback to old huggingface-cli if needed
hf download "$MODEL_NAME" --local-dir "$MODEL_PATH" 2>/dev/null || \
    huggingface-cli download "$MODEL_NAME" --local-dir "$MODEL_PATH"

echo ""
echo "✓ Model downloaded successfully!"
echo "✓ Location: $MODEL_PATH"
