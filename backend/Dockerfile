# syntax=docker/dockerfile:1
FROM python:3.13-slim

WORKDIR /app

# -----------------------------
# System dependencies
# -----------------------------
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# Requirements (cache-friendly)
# -----------------------------
COPY backend/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# -----------------------------
# Core backend dependencies
# -----------------------------
RUN pip install --no-cache-dir \
    fastapi uvicorn sqlalchemy[asyncio] asyncpg \
    pydantic-settings celery redis alembic \
    python-jose[cryptography] passlib[bcrypt]

# -----------------------------
# AI & Multi-Agent Frameworks
# -----------------------------
RUN pip install --no-cache-dir \
    scrapegraph-ai langchain llama-index haystack-ai litellm \
    tiktoken transformers sentence-transformers chromadb faiss-cpu \
    autogen-agent crewai langgraph openai-swarm metagpt superagi \
    taskweaver atomic-agents smolagents semantic-kernel rasa \
    huggingface-hub datasets evaluate \
    weaviate-client pinecone-client milvus

# -----------------------------
# GPU Support (optional / auto)
# -----------------------------
# Enables GPU visibility when container runs with --gpus all or runtime: nvidia
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility

# Install PyTorch with CUDA (fails gracefully on non-GPU systems)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cu121 || true

# -----------------------------
# App directories
# -----------------------------
RUN mkdir -p /models /data/langgraph_state /app/superagi/config /app/taskweaver/data

# -----------------------------
# Copy backend source
# -----------------------------
COPY backend /app/backend

# -----------------------------
# Expose FastAPI port
# -----------------------------
EXPOSE 8000

# -----------------------------
# Start FastAPI app
# -----------------------------
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
