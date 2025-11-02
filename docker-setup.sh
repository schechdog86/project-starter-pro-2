#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# Docker Setup Script for Project Starter Pro 2
# ============================================================

echo "============================================================"
echo "🐳 Project Starter Pro 2 - Docker Setup"
echo "============================================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose:"
    echo "   https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker version: $(docker --version)"
echo "✅ Docker Compose version: $(docker compose version)"
echo ""

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data projects logs
echo "✅ Directories created"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ .env file created. Please update it with your API keys."
    else
        echo "❌ .env.example not found. Please create .env manually."
        exit 1
    fi
else
    echo "✅ .env file found"
fi
echo ""

# Stop and remove existing containers
echo "🛑 Stopping existing containers (if any)..."
docker compose down -v 2>/dev/null || true
echo ""

# Build images
echo "🔨 Building Docker images..."
echo "   This will take 10-20 minutes on first run..."
echo ""
docker compose build --no-cache

echo ""
echo "============================================================"
echo "✅ Build complete!"
echo "============================================================"
echo ""

# Start services
echo "🚀 Starting services..."
docker compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service status
echo ""
echo "📊 Service Status:"
docker compose ps

echo ""
echo "============================================================"
echo "✅ Docker Setup Complete!"
echo "============================================================"
echo ""
echo "📋 Services:"
echo "   - Backend API:  http://localhost:8000"
echo "   - PostgreSQL:   localhost:5432"
echo "   - Redis:        localhost:6379"
echo ""
echo "🔍 Useful Commands:"
echo "   - View logs:           docker compose logs -f"
echo "   - View backend logs:   docker compose logs -f backend"
echo "   - Stop services:       docker compose down"
echo "   - Restart services:    docker compose restart"
echo "   - Rebuild:             docker compose up --build -d"
echo ""
echo "🧪 Test the API:"
echo "   curl http://localhost:8000/health"
echo ""

