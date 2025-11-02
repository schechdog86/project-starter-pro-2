# Docker Setup Guide - Project Starter Pro 2

## Overview

This Docker setup provides a complete, isolated environment for Project Starter Pro 2 with:
- ✅ Python 3.11 (solves all dependency conflicts)
- ✅ All AI frameworks (LangChain, LlamaIndex, LiteLLM, AutoGen, CrewAI, etc.)
- ✅ PostgreSQL 16 database
- ✅ Redis cache & message broker
- ✅ Celery worker for background tasks
- ✅ Health checks and auto-restart
- ✅ Production-ready configuration

## Prerequisites

1. **Docker** (version 20.10+)
   - Install: https://docs.docker.com/get-docker/
   - Verify: `docker --version`

2. **Docker Compose** (version 2.0+)
   - Usually included with Docker Desktop
   - Verify: `docker compose version`

## Quick Start

### 1. One-Command Setup

```bash
chmod +x docker-setup.sh
./docker-setup.sh
```

This script will:
- ✅ Check Docker installation
- ✅ Create necessary directories
- ✅ Build all Docker images
- ✅ Start all services
- ✅ Run health checks

### 2. Manual Setup

If you prefer manual control:

```bash
# Create directories
mkdir -p data projects logs

# Build images (first time only, takes 10-20 minutes)
docker compose build

# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

## Services

### Backend API (FastAPI)
- **URL:** http://localhost:8000
- **Container:** project-starter-pro-backend
- **Port:** 8000
- **Health Check:** http://localhost:8000/health

### PostgreSQL Database
- **Host:** localhost
- **Port:** 5432
- **User:** psp_user
- **Password:** psp_pass
- **Database:** psp
- **Container:** postgres

### Redis Cache
- **Host:** localhost
- **Port:** 6379
- **Container:** redis

### Celery Worker
- **Container:** celery-worker
- **Concurrency:** 4 workers

## Common Commands

### Start/Stop Services

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Stop and remove volumes (⚠️ deletes data)
docker compose down -v

# Restart a specific service
docker compose restart backend
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f celery
docker compose logs -f db

# Last 100 lines
docker compose logs --tail=100 backend
```

### Rebuild Images

```bash
# Rebuild all images
docker compose build --no-cache

# Rebuild and restart
docker compose up --build -d

# Rebuild specific service
docker compose build backend
```

### Execute Commands in Containers

```bash
# Open shell in backend container
docker compose exec backend bash

# Run Python shell
docker compose exec backend python

# Run database migrations
docker compose exec backend alembic upgrade head

# Create a new migration
docker compose exec backend alembic revision --autogenerate -m "description"
```

### Database Operations

```bash
# Connect to PostgreSQL
docker compose exec db psql -U psp_user -d psp

# Backup database
docker compose exec db pg_dump -U psp_user psp > backup.sql

# Restore database
docker compose exec -T db psql -U psp_user psp < backup.sql
```

### Monitor Resources

```bash
# View resource usage
docker stats

# View specific container
docker stats project-starter-pro-backend
```

## Testing the Setup

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T00:00:00Z"
}
```

### 2. Test AI Frameworks

```bash
docker compose exec backend python << 'PY'
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
        print(f'✅ {fw}')
    except:
        print(f'❌ {fw}')
PY
```

### 3. Test Database Connection

```bash
docker compose exec backend python << 'PY'
from backend.app.db import SessionLocal
from backend.app.models import User

db = SessionLocal()
print(f"✅ Database connected: {db.bind.url}")
db.close()
PY
```

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker compose logs

# Check specific service
docker compose logs backend

# Restart services
docker compose restart
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
ports:
  - "8001:8000"  # Use port 8001 instead
```

### Out of Disk Space

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove everything (⚠️ careful!)
docker system prune -a --volumes
```

### Database Connection Issues

```bash
# Check if database is healthy
docker compose ps db

# View database logs
docker compose logs db

# Restart database
docker compose restart db
```

### Rebuild from Scratch

```bash
# Stop everything
docker compose down -v

# Remove images
docker rmi $(docker images -q project-starter-pro*)

# Rebuild
docker compose build --no-cache

# Start
docker compose up -d
```

## Environment Variables

Create a `.env` file in the project root:

```bash
# Database
DB_TYPE=postgres
DB_HOST=db
DB_PORT=5432
DB_USER=psp_user
DB_PASS=psp_pass
DB_NAME=psp

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
CLAUDE_API_KEY=sk-ant-...
DEEPSEEK_API_KEY=sk-...
FIRECRAWL_API_KEY=fc-...
SCRAPEGRAPH_API_KEY=sg-...
GITHUB_TOKEN=ghp_...

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
```

## Production Deployment

### 1. Update docker-compose.yml

```yaml
services:
  backend:
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

### 2. Use Docker Swarm or Kubernetes

For production, consider:
- Docker Swarm for simple deployments
- Kubernetes for complex, scalable deployments
- Managed services (AWS ECS, Google Cloud Run, Azure Container Instances)

### 3. Security Checklist

- ✅ Use secrets management (Docker secrets, Vault)
- ✅ Enable HTTPS/TLS
- ✅ Set up firewall rules
- ✅ Use non-root users (already configured)
- ✅ Regular security updates
- ✅ Monitor logs and metrics

## Performance Optimization

### 1. Multi-stage Builds

Already implemented in Dockerfile to reduce image size.

### 2. Layer Caching

```bash
# Use BuildKit for better caching
DOCKER_BUILDKIT=1 docker compose build
```

### 3. Resource Limits

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

## Summary

**✅ Advantages of Docker Setup:**
- No Python version conflicts
- Isolated dependencies
- Reproducible builds
- Easy deployment
- Scalable architecture
- Production-ready

**📊 Build Time:**
- First build: 10-20 minutes
- Subsequent builds: 2-5 minutes (with cache)

**💾 Disk Space:**
- Images: ~3-4 GB
- Volumes: Depends on data

**🚀 Ready to Use:**
```bash
./docker-setup.sh
curl http://localhost:8000/health
```

