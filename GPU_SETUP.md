# GPU Setup Guide - Project Starter Pro 2

## Overview

This project is configured to use **NVIDIA GPUs** for accelerated AI workloads including:
- ✅ PyTorch model inference and training
- ✅ Transformer models (Hugging Face)
- ✅ Vector embeddings (Sentence-Transformers)
- ✅ LLM inference (local models)
- ✅ Image processing (TorchVision)
- ✅ Audio processing (TorchAudio)

## Prerequisites

### 1. NVIDIA GPU
- NVIDIA GPU with CUDA support (Compute Capability 3.5+)
- Recommended: RTX 3060 or better (12GB+ VRAM for LLMs)

### 2. NVIDIA Driver
- Version 525.60.13 or newer
- Check: `nvidia-smi`

### 3. Docker with NVIDIA Runtime
- Docker Engine 19.03+
- nvidia-docker2 package

## Installation

### Step 1: Install NVIDIA Driver

**Ubuntu/Debian:**
```bash
# Check current driver
nvidia-smi

# If not installed, install latest driver
sudo apt update
sudo apt install -y nvidia-driver-535
sudo reboot

# Verify after reboot
nvidia-smi
```

**Expected output:**
```
+-----------------------------------------------------------------------------+
| NVIDIA-SMI 535.xx.xx    Driver Version: 535.xx.xx    CUDA Version: 12.2   |
|-------------------------------+----------------------+----------------------+
| GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
| Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
|===============================+======================+======================|
|   0  NVIDIA GeForce ...  Off  | 00000000:01:00.0  On |                  N/A |
```

### Step 2: Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in
```

### Step 3: Install NVIDIA Container Toolkit

**Ubuntu/Debian:**
```bash
# Add NVIDIA package repository
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
    sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# Install nvidia-docker2
sudo apt-get update
sudo apt-get install -y nvidia-docker2

# Restart Docker
sudo systemctl restart docker
```

### Step 4: Verify NVIDIA Docker

```bash
# Test GPU access in container
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

If this works, you're ready! ✅

## Quick Start

### Automated Setup

```bash
chmod +x verify-gpu.sh
./verify-gpu.sh
```

This script will:
1. ✅ Check NVIDIA Docker runtime
2. ✅ Check NVIDIA driver
3. ✅ Build Docker containers
4. ✅ Start all services
5. ✅ Test GPU access in backend
6. ✅ Test GPU access in Celery worker

### Manual Setup

```bash
# Build containers
docker compose build --no-cache

# Start services
docker compose up -d

# Verify GPU access
docker compose exec backend python -c "import torch; print(torch.cuda.is_available())"
```

## Testing GPU Access

### PyTorch CUDA Test

```bash
docker compose exec backend python << 'EOF'
import torch

print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda}")
print(f"GPU count: {torch.cuda.device_count()}")

for i in range(torch.cuda.device_count()):
    print(f"\nGPU {i}: {torch.cuda.get_device_name(i)}")
    props = torch.cuda.get_device_properties(i)
    print(f"  Memory: {props.total_memory / 1024**3:.2f} GB")
    print(f"  Compute Capability: {props.major}.{props.minor}")
EOF
```

### Transformers GPU Test

```bash
docker compose exec backend python << 'EOF'
from transformers import pipeline
import torch

# Create a simple pipeline
classifier = pipeline("sentiment-analysis", device=0 if torch.cuda.is_available() else -1)

# Test inference
result = classifier("I love using GPU acceleration!")
print(f"Result: {result}")
print(f"Device: {'GPU' if torch.cuda.is_available() else 'CPU'}")
EOF
```

### Monitor GPU Usage

```bash
# Real-time monitoring
watch -n 1 nvidia-smi

# Or inside container
docker compose exec backend nvidia-smi

# Continuous monitoring
docker compose exec backend bash -c "while true; do nvidia-smi; sleep 2; done"
```

## Configuration

### docker-compose.yml

The GPU configuration is already set up:

```yaml
services:
  backend:
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=compute,utility
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    runtime: nvidia
```

### Limit GPU Access

To use specific GPUs:

```yaml
environment:
  - NVIDIA_VISIBLE_DEVICES=0,1  # Only use GPU 0 and 1
```

To limit memory:

```yaml
deploy:
  resources:
    limits:
      memory: 16G
    reservations:
      devices:
        - driver: nvidia
          device_ids: ['0']  # Only GPU 0
          capabilities: [gpu]
```

## Performance Optimization

### 1. Enable TensorFloat-32 (TF32)

```python
import torch
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True
```

### 2. Use Mixed Precision

```python
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()

with autocast():
    # Your model forward pass
    output = model(input)
```

### 3. Optimize Batch Size

```python
# Find optimal batch size
import torch

def find_optimal_batch_size(model, input_shape):
    batch_size = 1
    while True:
        try:
            torch.cuda.empty_cache()
            dummy_input = torch.randn(batch_size, *input_shape).cuda()
            model(dummy_input)
            batch_size *= 2
        except RuntimeError:
            return batch_size // 2
```

### 4. Use Gradient Checkpointing

```python
from transformers import AutoModel

model = AutoModel.from_pretrained("bert-base-uncased")
model.gradient_checkpointing_enable()
```

## Troubleshooting

### GPU Not Detected

**Check NVIDIA driver:**
```bash
nvidia-smi
```

**Check Docker runtime:**
```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

**Check container GPU access:**
```bash
docker compose exec backend nvidia-smi
```

### Out of Memory (OOM)

**Clear GPU cache:**
```python
import torch
torch.cuda.empty_cache()
```

**Reduce batch size:**
```python
# In your code
batch_size = 8  # Try smaller values: 4, 2, 1
```

**Use gradient accumulation:**
```python
accumulation_steps = 4
for i, batch in enumerate(dataloader):
    loss = model(batch)
    loss = loss / accumulation_steps
    loss.backward()
    
    if (i + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

### CUDA Version Mismatch

**Check versions:**
```bash
# Host CUDA version
nvidia-smi

# Container PyTorch CUDA version
docker compose exec backend python -c "import torch; print(torch.version.cuda)"
```

**Solution:** PyTorch CUDA version should be <= Driver CUDA version

### Permission Denied

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Log out and back in
```

## Benchmarking

### GPU vs CPU Performance

```bash
docker compose exec backend python << 'EOF'
import torch
import time

# Create large tensor
size = 10000
a = torch.randn(size, size)
b = torch.randn(size, size)

# CPU benchmark
start = time.time()
c_cpu = torch.matmul(a, b)
cpu_time = time.time() - start

# GPU benchmark
if torch.cuda.is_available():
    a_gpu = a.cuda()
    b_gpu = b.cuda()
    torch.cuda.synchronize()
    
    start = time.time()
    c_gpu = torch.matmul(a_gpu, b_gpu)
    torch.cuda.synchronize()
    gpu_time = time.time() - start
    
    print(f"CPU time: {cpu_time:.4f}s")
    print(f"GPU time: {gpu_time:.4f}s")
    print(f"Speedup: {cpu_time/gpu_time:.2f}x")
else:
    print("GPU not available")
EOF
```

## Best Practices

### 1. Always Check GPU Availability

```python
import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
```

### 2. Clear Cache Regularly

```python
import torch
import gc

def clear_memory():
    gc.collect()
    torch.cuda.empty_cache()
```

### 3. Use DataLoader with pin_memory

```python
from torch.utils.data import DataLoader

loader = DataLoader(
    dataset,
    batch_size=32,
    pin_memory=True,  # Faster GPU transfer
    num_workers=4
)
```

### 4. Profile GPU Usage

```python
import torch.profiler as profiler

with profiler.profile(
    activities=[profiler.ProfilerActivity.CPU, profiler.ProfilerActivity.CUDA],
    record_shapes=True
) as prof:
    model(input)

print(prof.key_averages().table(sort_by="cuda_time_total"))
```

## Summary

**✅ What You Have:**
- GPU-enabled Docker containers
- PyTorch with CUDA support
- All AI frameworks with GPU acceleration
- Automated verification script

**🚀 Quick Commands:**
```bash
# Setup and verify
./verify-gpu.sh

# Monitor GPU
nvidia-smi

# Test GPU in container
docker compose exec backend python -c "import torch; print(torch.cuda.is_available())"
```

**📊 Expected Performance:**
- 10-100x speedup for deep learning
- 5-20x speedup for transformer inference
- 3-10x speedup for embeddings generation

**🎯 Ready for:**
- Local LLM inference (Llama, Mistral, etc.)
- Fine-tuning models
- Batch embeddings generation
- Image/audio processing
- Real-time inference

