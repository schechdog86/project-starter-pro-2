# GitHub Actions CI/CD

This directory contains GitHub Actions workflows for automated testing, building, and deployment.

## 📋 Workflows

### 1. `docker-publish.yml` - Simple Docker Build & Push

**Triggers:**
- Push to `main` branch
- Manual workflow dispatch

**What it does:**
- Builds the FastAPI backend Docker image
- Pushes to GitHub Container Registry (GHCR)
- Verifies the pushed image

**Image location:**
```
ghcr.io/schechtereddie/project-starter-pro-2-backend:latest
```

---

### 2. `ci-cd.yml` - Full CI/CD Pipeline

**Triggers:**
- Push to `main` branch
- Pull requests to `main`
- Manual workflow dispatch

**Jobs:**

#### **Test Job**
- Sets up Python 3.13
- Installs dependencies
- Runs linting (ruff)
- Checks code formatting (black)

#### **Build and Push Job** (only on main branch)
- Builds both backend and Celery images
- Pushes to GHCR with multiple tags:
  - `latest` (for main branch)
  - `main-<sha>` (commit-specific)
  - `main` (branch name)
- Uses Docker layer caching for faster builds
- Verifies pushed images

**Image locations:**
```
ghcr.io/schechtereddie/project-starter-pro-2-backend:latest
ghcr.io/schechtereddie/project-starter-pro-2-celery:latest
```

---

## 🚀 Usage

### Automatic Triggers

Workflows run automatically when you:
```bash
git push origin main
```

### Manual Trigger

1. Go to GitHub → Actions
2. Select workflow (e.g., "CI/CD Pipeline")
3. Click "Run workflow"
4. Select branch
5. Click "Run workflow" button

---

## 📦 Pulling Images

### Pull Latest Images

```bash
# Backend
docker pull ghcr.io/schechtereddie/project-starter-pro-2-backend:latest

# Celery
docker pull ghcr.io/schechtereddie/project-starter-pro-2-celery:latest
```

### Pull Specific Commit

```bash
# Replace <sha> with commit hash
docker pull ghcr.io/schechtereddie/project-starter-pro-2-backend:main-<sha>
```

---

## 🔐 Authentication

### For GitHub Actions (Automatic)

GitHub Actions uses `GITHUB_TOKEN` automatically - no setup needed!

### For Local Development

```bash
# Create a Personal Access Token (PAT) with `read:packages` scope
# Then login:
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

---

## 🛠️ Using Images in Production

### Update docker-compose.yml

Instead of building locally, use pre-built images:

```yaml
version: "3.9"

services:
  backend:
    image: ghcr.io/schechtereddie/project-starter-pro-2-backend:latest
    # Remove 'build' section
    container_name: psp-backend
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
      - redis

  celery:
    image: ghcr.io/schechtereddie/project-starter-pro-2-celery:latest
    # Remove 'build' section
    container_name: psp-celery
    env_file:
      - .env
    depends_on:
      - backend
      - redis
      - db
```

Then:
```bash
docker compose pull
docker compose up -d
```

---

## 📊 Workflow Status

Check workflow status:
- **GitHub**: Repository → Actions tab
- **Badge**: Add to README.md:

```markdown
![CI/CD](https://github.com/schechtereddie/project-starter-pro-2/actions/workflows/ci-cd.yml/badge.svg)
```

---

## 🔍 Debugging Failed Workflows

### View Logs

1. Go to Actions tab
2. Click on failed workflow run
3. Click on failed job
4. Expand failed step to see logs

### Common Issues

**Issue**: Docker build fails
```
Solution: Check Dockerfile syntax and paths
```

**Issue**: Permission denied pushing to GHCR
```
Solution: Ensure workflow has 'packages: write' permission
```

**Issue**: Tests fail
```
Solution: Check test output in 'Test' job logs
```

---

## 🎯 Best Practices

### 1. Tag Strategy

- `latest` - Always points to main branch
- `main-<sha>` - Specific commit (for rollbacks)
- `v1.0.0` - Release tags (add manually)

### 2. Caching

Workflows use GitHub Actions cache to speed up builds:
```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```

### 3. Security

- Never commit secrets to workflows
- Use GitHub Secrets for sensitive data
- GITHUB_TOKEN is automatically provided

---

## 📈 Advanced Configuration

### Add Secrets

1. Go to Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add secrets like:
   - `DOCKER_USERNAME`
   - `DOCKER_PASSWORD`
   - `PRODUCTION_SECRET_KEY`

### Use in Workflow

```yaml
- name: Use secret
  env:
    SECRET_KEY: ${{ secrets.PRODUCTION_SECRET_KEY }}
  run: echo "Secret is set"
```

---

## 🔄 Deployment Strategies

### Rolling Update

```bash
# Pull latest images
docker compose pull

# Restart services with zero downtime
docker compose up -d --no-deps --build backend
```

### Blue-Green Deployment

```bash
# Start new version alongside old
docker compose -f docker-compose.blue.yml up -d

# Switch traffic (update load balancer)
# ...

# Stop old version
docker compose -f docker-compose.green.yml down
```

---

## 📚 Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

---

## ✅ Checklist

After setting up workflows:

- [ ] Workflows created in `.github/workflows/`
- [ ] Pushed to GitHub
- [ ] First workflow run successful
- [ ] Images visible in Packages tab
- [ ] Images are public (or team has access)
- [ ] docker-compose.yml updated to use images
- [ ] Documentation updated

---

**Happy CI/CD! 🚀**

