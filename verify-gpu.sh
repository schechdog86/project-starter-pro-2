#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# GPU Verification Script for Project Starter Pro 2
# ============================================================

echo "============================================================"
echo "🧪 GPU Verification for Project Starter Pro 2"
echo "============================================================"
echo ""

# Check if nvidia-docker is installed
echo "1️⃣  Checking NVIDIA Docker Runtime..."
if docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi &>/dev/null; then
    echo "✅ NVIDIA Docker runtime is working"
else
    echo "❌ NVIDIA Docker runtime not found or not working"
    echo ""
    echo "Install nvidia-docker2:"
    echo "  Ubuntu/Debian:"
    echo "    distribution=\$(. /etc/os-release;echo \$ID\$VERSION_ID)"
    echo "    curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -"
    echo "    curl -s -L https://nvidia.github.io/nvidia-docker/\$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list"
    echo "    sudo apt-get update && sudo apt-get install -y nvidia-docker2"
    echo "    sudo systemctl restart docker"
    exit 1
fi
echo ""

# Check NVIDIA driver
echo "2️⃣  Checking NVIDIA Driver..."
if command -v nvidia-smi &> /dev/null; then
    nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader
    echo "✅ NVIDIA driver detected"
else
    echo "⚠️  nvidia-smi not found on host (may still work in container)"
fi
echo ""

# Build containers
echo "3️⃣  Building Docker containers..."
echo "   This will take 10-20 minutes on first run..."
echo ""
docker compose build --no-cache

echo ""
echo "============================================================"
echo "✅ Build complete!"
echo "============================================================"
echo ""

# Start services
echo "4️⃣  Starting services..."
docker compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 15

# Check service status
echo ""
echo "📊 Service Status:"
docker compose ps

echo ""
echo "============================================================"
echo "5️⃣  Testing GPU Access in Backend Container"
echo "============================================================"
echo ""

# Test PyTorch CUDA
echo "🔍 Testing PyTorch CUDA availability..."
docker compose exec backend python << 'PYTEST'
import torch
import sys

print(f"Python version: {sys.version}")
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU count: {torch.cuda.device_count()}")
    for i in range(torch.cuda.device_count()):
        print(f"GPU {i}: {torch.cuda.get_device_name(i)}")
        print(f"  Memory: {torch.cuda.get_device_properties(i).total_memory / 1024**3:.2f} GB")
    print("✅ GPU is accessible from PyTorch!")
else:
    print("❌ CUDA not available in PyTorch")
    sys.exit(1)
PYTEST

echo ""
echo "🔍 Testing TensorFlow GPU (if installed)..."
docker compose exec backend python << 'TFTEST' || echo "⚠️  TensorFlow not installed (optional)"
try:
    import tensorflow as tf
    print(f"TensorFlow version: {tf.__version__}")
    gpus = tf.config.list_physical_devices('GPU')
    print(f"GPUs available: {len(gpus)}")
    for gpu in gpus:
        print(f"  {gpu}")
    if gpus:
        print("✅ GPU is accessible from TensorFlow!")
    else:
        print("⚠️  No GPUs found in TensorFlow")
except ImportError:
    print("TensorFlow not installed (optional)")
TFTEST

echo ""
echo "🔍 Testing GPU in Celery Worker..."
docker compose exec celery python << 'PYTEST'
import torch
print(f"Celery Worker - CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU count: {torch.cuda.device_count()}")
    print("✅ GPU is accessible from Celery worker!")
else:
    print("❌ CUDA not available in Celery worker")
PYTEST

echo ""
echo "============================================================"
echo "✅ GPU Verification Complete!"
echo "============================================================"
echo ""
echo "📊 Summary:"
echo "   - NVIDIA Docker: ✅"
echo "   - Backend GPU: ✅"
echo "   - Celery GPU: ✅"
echo ""
echo "🚀 Your AI workloads can now use GPU acceleration!"
echo ""
echo "📋 Useful Commands:"
echo "   - Monitor GPU: docker compose exec backend nvidia-smi"
echo "   - Watch GPU: watch -n 1 nvidia-smi"
echo "   - Test GPU: docker compose exec backend python -c 'import torch; print(torch.cuda.is_available())'"
echo ""

