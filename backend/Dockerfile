# syntax=docker/dockerfile:1
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies for AI packages
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (caching optimization)
COPY backend/requirements.txt .

# Install Python dependencies
# Split into layers for better caching
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install core backend dependencies first
RUN pip install --no-cache-dir \
    fastapi uvicorn sqlalchemy[asyncio] asyncpg \
    pydantic-settings celery redis alembic \
    python-jose[cryptography] passlib[bcrypt]

# Install AI and multi-agent frameworks
RUN pip install --no-cache-dir \
    scrapegraph-ai langchain llama-index haystack-ai litellm \
    tiktoken transformers sentence-transformers chromadb faiss-cpu \
    autogen-agent crewai langgraph openai-swarm metagpt superagi \
    taskweaver atomic-agents smolagents semantic-kernel rasa \
    huggingface-hub datasets evaluate \
    weaviate-client pinecone-client milvus

# Create directories for AI models and data
RUN mkdir -p /models /data/langgraph_state /app/superagi/config /app/taskweaver/data

# Copy application code
COPY backend /app/backend

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI using Uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

