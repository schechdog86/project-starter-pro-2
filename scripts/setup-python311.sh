#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# PYTHON 3.11 SETUP SCRIPT
# ============================================================
# This script installs Python 3.11 and creates a virtual environment
# with all required AI frameworks and dependencies
# ============================================================

echo "============================================================"
echo "🐍 PYTHON 3.11 SETUP FOR PROJECT STARTER PRO 2"
echo "============================================================"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
   echo "⚠️  Please do not run this script as root"
   echo "   Run: bash scripts/setup-python311.sh"
   exit 1
fi

# Install Python 3.11
echo "📦 Installing Python 3.11..."
sudo apt update -qq
sudo apt install -y python3.11 python3.11-venv python3.11-dev build-essential

echo ""
echo "✅ Python 3.11 installed:"
python3.11 --version

# Remove old venv if exists
if [ -d ".venv" ]; then
    echo ""
    echo "🗑️  Removing old virtual environment..."
    rm -rf .venv
fi

# Create virtual environment
echo ""
echo "🔧 Creating Python 3.11 virtual environment..."
python3.11 -m venv .venv

# Activate virtual environment
echo ""
echo "✅ Activating virtual environment..."
source .venv/bin/activate

# Verify Python version
echo ""
echo "🔍 Verifying Python version in venv:"
python --version

# Upgrade pip
echo ""
echo "📦 Upgrading pip, setuptools, wheel..."
python -m pip install --upgrade pip setuptools wheel

echo ""
echo "============================================================"
echo "✅ PYTHON 3.11 VIRTUAL ENVIRONMENT READY!"
echo "============================================================"
echo ""
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo ""
echo "🚀 Next steps:"
echo "   1. Activate the environment:"
echo "      source .venv/bin/activate"
echo ""
echo "   2. Install core packages:"
echo "      pip install -r backend/requirements-core.txt"
echo ""
echo "   3. Install additional frameworks (optional):"
echo "      pip install metagpt semantic-kernel atomic-agents smolagents"
echo ""
echo "============================================================"

