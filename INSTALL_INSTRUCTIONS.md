# Installation Instructions for Project Starter Pro 2

## Problem: Python 3.13 Compatibility Issues

The current installation is failing because **Python 3.13 is too new** (released Oct 2024). Most AI frameworks don't support it yet:
- MetaGPT, Semantic Kernel, Firecrawl, and others have dependency conflicts
- Pip is backtracking through hundreds of package versions trying to find compatible combinations
- This can take hours and often fails

## Solution: Use Python 3.11

Python 3.11 is the **recommended version** for AI/ML frameworks in 2025.

### Step 1: Install Python 3.11

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3.11-dev build-essential
```

### Step 2: Create Virtual Environment

```bash
# Remove old venv if exists
rm -rf .venv

# Create new venv with Python 3.11
python3.11 -m venv .venv

# Activate it
source .venv/bin/activate

# Verify version
python --version  # Should show Python 3.11.x
```

### Step 3: Upgrade pip

```bash
python -m pip install --upgrade pip setuptools wheel
```

### Step 4: Install Core Packages First

Install the essential packages that work well together:

```bash
pip install -r backend/requirements-core.txt
```

This installs:
- FastAPI, SQLAlchemy, Celery, Redis (backend)
- LangChain, LlamaIndex, LiteLLM (core AI)
- OpenAI, Anthropic, Cohere (LLM clients)
- ScrapeGraphAI, Firecrawl, Playwright (scraping)
- PyAutogen, CrewAI, LangGraph (multi-agent)
- Transformers, PyTorch, ChromaDB, FAISS (ML/vectors)

### Step 5: Install Additional Frameworks (Optional)

After core packages are installed, add optional frameworks one by one:

```bash
# MetaGPT (hierarchical agents)
pip install metagpt

# Semantic Kernel (Microsoft AI skills)
pip install semantic-kernel

# Atomic Agents (schema-based)
pip install atomic-agents

# Smolagents (lightweight)
pip install smolagents

# Haystack (NLP framework)
pip install haystack-ai

# Selenium & Scrapy (additional scraping)
pip install selenium scrapy

# Google Gemini
pip install google-generativeai

# Additional vector DBs
pip install weaviate-client pinecone-client qdrant-client
```

### Step 6: Verify Installation

```bash
python << 'PY'
import sys
print(f"Python version: {sys.version}")

frameworks = [
    'fastapi', 'langchain', 'llama_index', 'litellm',
    'scrapegraphai', 'firecrawl', 'transformers',
    'chromadb', 'faiss', 'pyautogen', 'crewai', 'langgraph'
]

for fw in frameworks:
    try:
        __import__(fw)
        print(f"✅ {fw}")
    except:
        print(f"❌ {fw}")
PY
```

## Alternative: Use Docker

If you prefer Docker, create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements-core.txt .
RUN pip install --no-cache-dir -r requirements-core.txt

COPY . .

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Files Created

1. **`backend/requirements.txt`** - Complete list of all frameworks (153 lines)
2. **`backend/requirements-core.txt`** - Essential packages with version constraints (75 lines)
3. **`scripts/setup-python311.sh`** - Automated setup script

## Summary

**Current Issue:** Python 3.13 + complex dependencies = dependency resolution hell

**Solution:** Python 3.11 + staged installation = success

**Time Estimate:**
- Python 3.11 setup: 2-3 minutes
- Core packages install: 10-15 minutes
- Optional packages: 5-10 minutes
- **Total: ~20-30 minutes**

vs. Python 3.13 which may never complete or take hours.

