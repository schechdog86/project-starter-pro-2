# 🚀 API Usage Guide - Orchestrator System

## Quick Start

### 1. Start the Backend

```bash
cd backend
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

---

## 📋 Skill Management

### List All Skills

```bash
GET /api/skills
```

**Response:**
```json
{
  "skills": ["web_search", "memory_search", "code_analysis"],
  "count": 3
}
```

---

### Get Skill Information

```bash
GET /api/skills/{skill_name}
```

**Example:**
```bash
curl http://localhost:8000/api/skills/web_search
```

**Response:**
```json
{
  "name": "web_search",
  "version": "1.0.0",
  "description": "Search the web and return titles (demo).",
  "category": "research",
  "enabled": false,
  "parameters": {
    "query": {
      "type": "string",
      "required": true,
      "description": "Search query"
    },
    "num_results": {
      "type": "integer",
      "required": false,
      "description": "How many",
      "default": 5
    }
  },
  "permissions": ["network"],
  "timeout": 30
}
```

---

### Approve and Enable a Skill

```bash
POST /api/skills/{skill_name}/approve
```

**Request:**
```json
{
  "enabled": true
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/skills/web_search/approve \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

**Response:**
```json
{
  "ok": true,
  "name": "web_search",
  "enabled": true
}
```

---

### Execute a Skill

```bash
POST /api/skills/{skill_name}/execute
```

**Request:**
```json
{
  "params": {
    "query": "RTX 4090 benchmark",
    "num_results": 3
  }
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/skills/web_search/execute \
  -H "Content-Type: application/json" \
  -d '{
    "params": {
      "query": "RTX 4090 benchmark",
      "num_results": 3
    }
  }'
```

**Response:**
```json
{
  "ok": true,
  "result": {
    "results": [
      "RTX 4090 Gaming Benchmarks",
      "NVIDIA GeForce RTX 4090 Review",
      "RTX 4090 vs RTX 3090 Performance"
    ]
  }
}
```

---

### Generate a New Skill

```bash
POST /api/skills/generate
```

**Request:**
```json
{
  "name": "csv_parser",
  "prompt": "skill that parses CSV and returns stats"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/skills/generate \
  -H "Content-Type: application/json" \
  -d '{
    "name": "csv_parser",
    "prompt": "skill that parses CSV files and returns statistical analysis"
  }'
```

**Response:**
```json
{
  "ok": true,
  "draft": {
    "name": "csv_parser",
    "draft": "... generated code and config ...",
    "status": "pending_review"
  }
}
```

---

### Add a Custom Skill

```bash
POST /api/skills
```

**Request:**
```json
{
  "name": "my_skill",
  "config": {
    "name": "my_skill",
    "version": "1.0.0",
    "description": "My custom skill",
    "category": "custom",
    "enabled": false,
    "parameters": {
      "input": {
        "type": "string",
        "required": true
      }
    },
    "permissions": [],
    "timeout": 30
  },
  "code": "from backend.app.skills.base import BaseSkill\n\nclass MySkill(BaseSkill):\n    def execute(self, input: str):\n        return {'result': input.upper()}",
  "enabled": false
}
```

**Response:**
```json
{
  "ok": true,
  "name": "my_skill",
  "enabled": false
}
```

---

## 🤖 Agent Management

### Create an Agent

```bash
POST /api/agents
```

**Request:**
```json
{
  "name": "ProjectWizard",
  "config": {
    "role": "Project Planner",
    "policy": "auto"
  },
  "approved": true
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ProjectWizard",
    "config": {"role": "Project Planner", "policy": "auto"},
    "approved": true
  }'
```

**Response:**
```json
{
  "ok": true
}
```

---

## 📁 Project Management

### Run a Project

```bash
POST /api/projects/run
```

**Request:**
```json
{
  "name": "my_app"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/projects/run \
  -H "Content-Type: application/json" \
  -d '{"name": "my_app"}'
```

**Response:**
```json
{
  "ok": true,
  "project": {
    "name": "my_app",
    "phase": "planning",
    "next_required_doc": "01_project_scope.md",
    "docs_status": {}
  }
}
```

---

### Get Project Status

```bash
GET /api/projects/{name}/status
```

**Example:**
```bash
curl http://localhost:8000/api/projects/my_app/status
```

**Response:**
```json
{
  "project": {
    "name": "my_app",
    "phase": "planning",
    "status": "active"
  }
}
```

---

## 🔍 Research & Data Retrieval

### Retrieve Research Data

```bash
POST /api/research/retrieve
```

**Request:**
```json
{
  "topic": "AI frameworks 2025",
  "urls": [
    "https://example.com/ai-frameworks",
    "https://example.com/ai-trends"
  ]
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/research/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "AI frameworks 2025",
    "urls": [
      "https://example.com/ai-frameworks",
      "https://example.com/ai-trends"
    ]
  }'
```

**Response:**
```json
{
  "ok": true,
  "data": {
    "topic": "AI frameworks 2025",
    "scrapes": [...],
    "crawl": {...},
    "url_count": 2
  }
}
```

---

## 🔄 Complete Workflow Example

### 1. List Available Skills

```bash
curl http://localhost:8000/api/skills
```

### 2. Check Web Search Skill (Disabled by Default)

```bash
curl http://localhost:8000/api/skills/web_search
```

### 3. Approve Web Search Skill

```bash
curl -X POST http://localhost:8000/api/skills/web_search/approve \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

### 4. Execute Web Search

```bash
curl -X POST http://localhost:8000/api/skills/web_search/execute \
  -H "Content-Type: application/json" \
  -d '{
    "params": {
      "query": "Python async programming",
      "num_results": 5
    }
  }'
```

### 5. Use Results for Research

```bash
# Get URLs from web search results, then:
curl -X POST http://localhost:8000/api/research/retrieve \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Python async programming",
    "urls": ["https://url1.com", "https://url2.com"]
  }'
```

### 6. Create Project

```bash
curl -X POST http://localhost:8000/api/projects/run \
  -H "Content-Type: application/json" \
  -d '{"name": "async_python_guide"}'
```

---

## 📊 Orchestrator Status

### Get Orchestrator Status

```bash
GET /ai/orchestrator/status
```

**Example:**
```bash
curl http://localhost:8000/ai/orchestrator/status
```

**Response:**
```json
{
  "agents": 1,
  "skills": 3,
  "audit_log_size": 15,
  "loaded_agents": ["ProjectWizard"],
  "available_skills": ["web_search", "memory_search", "code_analysis"]
}
```

---

## 🎯 Common Use Cases

### Use Case 1: Research Assistant

```bash
# 1. Enable web search
curl -X POST http://localhost:8000/api/skills/web_search/approve \
  -d '{"enabled": true}'

# 2. Search for information
curl -X POST http://localhost:8000/api/skills/web_search/execute \
  -d '{"params": {"query": "machine learning trends", "num_results": 5}}'

# 3. Deep dive with research retrieval
curl -X POST http://localhost:8000/api/research/retrieve \
  -d '{"topic": "ML trends", "urls": ["..."]}'
```

### Use Case 2: Code Analysis

```bash
# Execute code analysis skill
curl -X POST http://localhost:8000/api/skills/code_analysis/execute \
  -H "Content-Type: application/json" \
  -d '{
    "params": {
      "code": "def hello():\n    print(\"world\")",
      "language": "python"
    }
  }'
```

### Use Case 3: Memory Search

```bash
# Search memory for relevant information
curl -X POST http://localhost:8000/api/skills/memory_search/execute \
  -H "Content-Type: application/json" \
  -d '{
    "params": {
      "query": "user preferences",
      "k": 10
    }
  }'
```

---

## 🔧 Tips

1. **Skills are disabled by default** - Always approve before use
2. **Check skill info** - Review parameters and permissions
3. **Use audit log** - Track all operations via `/ai/orchestrator/audit-log`
4. **Generate skills** - Use LLM to create new skills from prompts
5. **Research workflow** - Combine web search → research retrieval → memory storage

---

## 📚 Related Documentation

- **Full Guide:** `ORCHESTRATOR.md`
- **Summary:** `ORCHESTRATOR_SUMMARY.md`
- **Memory System:** `MEMORY_SYSTEM.md`
- **AI Stack:** `AI_STACK.md`

---

**Happy building!** 🚀

