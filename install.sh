#!/usr/bin/env bash
set -euo pipefail

echo "============================================================"
echo "🚀 INSTALLING WITH PYTHON 3.11"
echo "============================================================"
echo ""

# Step 1: Install Python 3.11
echo "Step 1: Installing Python 3.11..."
sudo apt update -qq
sudo apt install -y python3.11 python3.11-venv python3.11-dev build-essential

echo ""
echo "✅ Python 3.11 installed:"
python3.11 --version

# Step 2: Remove old venv
echo ""
echo "Step 2: Removing old virtual environment..."
rm -rf .venv

# Step 3: Create new venv
echo ""
echo "Step 3: Creating Python 3.11 virtual environment..."
python3.11 -m venv .venv

# Step 4: Activate and upgrade pip
echo ""
echo "Step 4: Activating virtual environment and upgrading pip..."
source .venv/bin/activate
python --version
python -m pip install --upgrade pip setuptools wheel

# Step 5: Install core packages
echo ""
echo "============================================================"
echo "🚀 Step 5: Installing CORE packages"
echo "============================================================"
echo "This will install:"
echo "  - FastAPI, SQLAlchemy, Celery, Redis"
echo "  - LangChain, LlamaIndex, LiteLLM"
echo "  - OpenAI, Anthropic, Cohere"
echo "  - ScrapeGraphAI, Firecrawl, Playwright"
echo "  - PyAutogen, CrewAI, LangGraph"
echo "  - Transformers, PyTorch, ChromaDB, FAISS"
echo ""
echo "⏱️  This will take 10-20 minutes..."
echo ""

pip install -r backend/requirements-core.txt

# Step 6: Verify installation
echo ""
echo "============================================================"
echo "✅ Verifying installation..."
echo "============================================================"

python << 'PY'
import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print("")

frameworks = [
    ('fastapi', 'FastAPI'),
    ('langchain', 'LangChain'),
    ('llama_index', 'LlamaIndex'),
    ('litellm', 'LiteLLM'),
    ('scrapegraphai', 'ScrapeGraphAI'),
    ('firecrawl', 'Firecrawl'),
    ('transformers', 'Transformers'),
    ('chromadb', 'ChromaDB'),
    ('faiss', 'FAISS'),
    ('pyautogen', 'AutoGen'),
    ('crewai', 'CrewAI'),
    ('langgraph', 'LangGraph'),
]

installed = []
missing = []

for module, name in frameworks:
    try:
        __import__(module)
        installed.append(name)
        print(f'✅ {name}')
    except Exception as e:
        missing.append(name)
        print(f'❌ {name} - {str(e)[:50]}')

print(f'\n📊 Summary: {len(installed)}/{len(frameworks)} frameworks installed')

if missing:
    print(f'\n⚠️  Missing: {", ".join(missing)}')
else:
    print('\n🎉 All core frameworks successfully installed!')
PY

echo ""
echo "============================================================"
echo "✅ INSTALLATION COMPLETE!"
echo "============================================================"
echo ""
echo "To activate the environment in the future:"
echo "  source .venv/bin/activate"
echo ""

