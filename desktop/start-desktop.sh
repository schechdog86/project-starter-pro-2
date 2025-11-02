#!/usr/bin/env bash
set -euo pipefail

# Project Starter Pro 2 - Desktop App Launcher
# Handles installation and startup of the Electron desktop app

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================================"
echo "🚀 Project Starter Pro 2 - Desktop App"
echo "============================================================"
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 20 LTS"
    echo "   https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "⚠️  Node.js version $NODE_VERSION detected. Recommended: 20 LTS"
fi

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm"
    exit 1
fi

# Install Electron dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Electron dependencies..."
    npm install
    echo "✅ Electron dependencies installed"
    echo ""
fi

# Install React UI dependencies if needed
if [ ! -d "react-ui/node_modules" ]; then
    echo "📦 Installing React UI dependencies..."
    cd react-ui
    npm install
    cd ..
    echo "✅ React UI dependencies installed"
    echo ""
fi

# Check if backend is running
echo "🔍 Checking backend status..."
if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
    echo "✅ Backend is running"
else
    echo "⚠️  Backend is not running"
    echo ""
    echo "Would you like to start the backend? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "🐳 Starting Docker backend..."
        cd ..
        docker compose up -d
        echo "⏳ Waiting for backend to be ready..."
        sleep 5
        cd desktop
        echo "✅ Backend started"
    else
        echo "⚠️  Some features may not work without the backend"
    fi
fi

echo ""
echo "============================================================"
echo "🎯 Starting Desktop App..."
echo "============================================================"
echo ""
echo "Development mode:"
echo "  - React dev server: http://localhost:5173"
echo "  - Hot reload enabled"
echo "  - DevTools open"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Start React dev server in background
cd react-ui
npm run dev &
REACT_PID=$!

# Wait for React dev server
echo "⏳ Waiting for React dev server..."
sleep 3

# Start Electron
cd ..
npm run dev:electron

# Cleanup on exit
kill $REACT_PID 2>/dev/null || true

