# 🎭 AI Orchestrator System

## Overview

The **Orchestrator** is the central controller for agent lifecycle, skill management, and project coordination in Project Starter Pro 2.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │    Agent     │  │    Skill     │  │   Memory     │ │
│  │  Management  │  │  Management  │  │   Routing    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
         │                  │                  │
         ▼                  ▼                  ▼
   ┌─────────┐       ┌──────────┐      ┌──────────┐
   │ Agents  │       │  Skills  │      │  Memory  │
   │ (CrewAI,│       │ Registry │      │  System  │
   │ AutoGen)│       │ Factory  │      │ (4-tier) │
   └─────────┘       └──────────┘      └──────────┘
```

---

## 📦 Components

### **1. Orchestrator** (`backend/app/ai/orchestrator.py`)

Main controller with:
- **Agent Management** - Create, load, destroy agents
- **Skill Management** - Load, ensure, add skills
- **Memory Routing** - Route data to appropriate memory tier
- **Audit Logging** - Track all operations

### **2. Skill Registry** (`backend/app/skills/registry.py`)

- Auto-discovers skills from folder structure
- Loads/saves `registry.json`
- Manages skill metadata

### **3. Skill Factory** (`backend/app/skills/skill_factory.py`)

- Dynamically loads skill Python modules
- Caches skill classes
- Supports hot reload

### **4. Base Skill** (`backend/app/skills/base.py`)

Abstract base class providing:
- Parameter validation
- Permission checking
- Default values
- Type checking

---

## 🛠️ Skill System

### **Skill Structure**

```
backend/app/skills/
├── registry.json              # Skill metadata registry
├── base.py                    # Base skill class
├── registry.py                # Skill registry
├── skill_factory.py           # Skill factory
├── web_search/
│   ├── __init__.py
│   ├── config.json            # Skill configuration
│   └── skill.py               # Skill implementation
├── memory_search/
│   ├── __init__.py
│   ├── config.json
│   └── skill.py
└── code_analysis/
    ├── __init__.py
    ├── config.json
    └── skill.py
```

### **Skill Configuration** (`config.json`)

```json
{
  "name": "web_search",
  "version": "1.0.0",
  "description": "Search the web for information",
  "category": "research",
  "enabled": true,
  "parameters": {
    "query": {
      "type": "string",
      "required": true,
      "description": "Search query"
    },
    "num_results": {
      "type": "integer",
      "default": 5,
      "description": "Number of results"
    }
  },
  "dependencies": ["requests", "beautifulsoup4"],
  "frameworks": ["crewai", "autogen", "langchain"],
  "permissions": ["network"],
  "timeout": 30
}
```

### **Skill Implementation** (`skill.py`)

```python
from backend.app.skills.base import BaseSkill

class WebSearchSkill(BaseSkill):
    """Search the web using DuckDuckGo."""
    
    def execute(self, query: str, num_results: int = 5):
        """Execute web search."""
        # Validate parameters
        self.validate_params({"query": query, "num_results": num_results})
        
        # Implementation
        results = self._search(query, num_results)
        return results
```

---

## 🚀 API Endpoints

### **Orchestrator Status**

```http
GET /ai/orchestrator/status
```

**Response:**
```json
{
  "agents": 2,
  "skills": 3,
  "audit_log_size": 45,
  "loaded_agents": ["researcher", "writer"],
  "available_skills": ["web_search", "memory_search", "code_analysis"]
}
```

---

### **Agent Management**

#### **List Agents**

```http
GET /ai/orchestrator/agents
```

**Response:**
```json
{
  "agents": ["researcher", "writer"],
  "count": 2
}
```

#### **Create Agent**

```http
POST /ai/orchestrator/agents
```

**Request:**
```json
{
  "name": "researcher",
  "config": {
    "role": "Research Specialist",
    "goal": "Find and analyze information",
    "policy": "auto"
  },
  "approve": true
}
```

**Response:**
```json
{
  "name": "researcher",
  "created": true,
  "status": "created"
}
```

#### **Destroy Agent**

```http
DELETE /ai/orchestrator/agents/{agent_name}
```

**Response:**
```json
{
  "name": "researcher",
  "status": "destroyed"
}
```

---

### **Skill Management**

#### **List Skills**

```http
GET /ai/orchestrator/skills
```

**Response:**
```json
{
  "skills": ["web_search", "memory_search", "code_analysis"],
  "count": 3
}
```

#### **Get Skill Info**

```http
GET /ai/orchestrator/skills/{skill_name}
```

**Response:**
```json
{
  "name": "web_search",
  "version": "1.0.0",
  "description": "Search the web for information",
  "category": "research",
  "enabled": true,
  "parameters": {...},
  "permissions": ["network"],
  "timeout": 30
}
```

#### **Execute Skill**

```http
POST /ai/orchestrator/skills/execute
```

**Request:**
```json
{
  "skill_name": "web_search",
  "parameters": {
    "query": "FastAPI best practices",
    "num_results": 5
  }
}
```

**Response:**
```json
{
  "skill": "web_search",
  "result": [
    {
      "title": "FastAPI Best Practices",
      "snippet": "...",
      "url": "https://..."
    }
  ],
  "status": "success"
}
```

#### **Reload Skills**

```http
POST /ai/orchestrator/skills/reload
```

**Response:**
```json
{
  "status": "reloaded",
  "skills": ["web_search", "memory_search", "code_analysis"],
  "count": 3
}
```

---

### **Audit Log**

```http
GET /ai/orchestrator/audit-log?limit=100
```

**Response:**
```json
{
  "entries": [
    {
      "timestamp": "2025-01-15T10:30:00",
      "event": "skill_loaded",
      "data": "web_search"
    },
    {
      "timestamp": "2025-01-15T10:31:00",
      "event": "agent_created",
      "data": "researcher"
    }
  ],
  "count": 2
}
```

---

## 💻 Python Usage

### **Basic Usage**

```python
from backend.app.ai.orchestrator import orchestrator

# Create an agent
orchestrator.create_agent(
    name="researcher",
    config={"role": "Researcher", "policy": "auto"},
    approve=True
)

# Load a skill
skill = orchestrator.load_skill("web_search")
results = skill.execute(query="AI trends 2025", num_results=5)

# Route memory
orchestrator.route_memory(
    data={"topic": "AI trends", "results": results},
    importance=2  # High importance
)

# Recall memory
memories = orchestrator.recall_memory("AI trends", k=10)
```

---

### **Creating Custom Skills**

```python
# 1. Create skill directory
mkdir -p backend/app/skills/my_skill

# 2. Create config.json
{
  "name": "my_skill",
  "version": "1.0.0",
  "description": "My custom skill",
  "category": "custom",
  "enabled": true,
  "parameters": {
    "input": {
      "type": "string",
      "required": true
    }
  },
  "permissions": [],
  "timeout": 30
}

# 3. Create skill.py
from backend.app.skills.base import BaseSkill

class MySkill(BaseSkill):
    def execute(self, input: str):
        self.validate_params({"input": input})
        # Your logic here
        return {"result": "success"}

# 4. Reload skills
orchestrator.skill_registry.reload()
```

---

## 🔐 Approval System

### **Skill Approval Workflow**

Skills can be disabled by default (`"enabled": false` in `config.json`) and require approval before use.

#### **1. Request Approval**

```http
POST /ai/approvals/request
```

**Request:**
```json
{
  "item_type": "skill",
  "item_name": "web_search",
  "config": {
    "name": "web_search",
    "version": "1.0.0",
    "enabled": true
  },
  "reason": "Need web search for research tasks"
}
```

**Response:**
```json
{
  "request_id": "skill_web_search_1234567890.123",
  "status": "pending",
  "message": "Approval requested"
}
```

#### **2. List Pending Approvals**

```http
GET /ai/approvals/pending
```

**Response:**
```json
{
  "pending": [
    {
      "id": "skill_web_search_1234567890.123",
      "type": "skill",
      "name": "web_search",
      "config": {...},
      "reason": "Need web search for research tasks",
      "requested_at": "2025-01-15T10:30:00",
      "status": "pending"
    }
  ],
  "count": 1
}
```

#### **3. Approve Request**

```http
POST /ai/approvals/{request_id}/approve
```

**Request:**
```json
{
  "approver": "user_name"
}
```

**Response:**
```json
{
  "request_id": "skill_web_search_1234567890.123",
  "status": "approved",
  "approved_by": "user_name",
  "message": "Request approved successfully"
}
```

#### **4. Reject Request**

```http
POST /ai/approvals/{request_id}/reject
```

**Request:**
```json
{
  "reason": "Security concerns",
  "rejector": "admin"
}
```

**Response:**
```json
{
  "request_id": "skill_web_search_1234567890.123",
  "status": "rejected",
  "rejected_by": "admin",
  "reason": "Security concerns",
  "message": "Request rejected"
}
```

### **Agent Approval Policy**

#### **Auto-Approve**

```json
{
  "policy": "auto"
}
```

Agents are automatically approved.

#### **User Approval** (Default)

```json
{
  "policy": "user_approval"
}
```

Requires explicit `approve=True` parameter or approval workflow.

---

## 🧪 Testing

### **Run the Demo Script**

The easiest way to test the orchestrator is to run the comprehensive demo:

```bash
# Start the backend
cd backend
uvicorn main:app --reload

# In another terminal, run the demo
python3 examples/orchestrator_demo.py
```

The demo script will:
1. ✅ Check orchestrator status
2. ✅ List all skills
3. ✅ Get skill information
4. ✅ Try to execute a disabled skill (will fail)
5. ✅ Request approval for the skill
6. ✅ List pending approvals
7. ✅ Approve the request
8. ✅ Execute the now-enabled skill
9. ✅ Test memory search skill
10. ✅ Test code analysis skill
11. ✅ View audit log

### **Manual Testing**

#### **Test Orchestrator Status**

```bash
curl http://localhost:8000/ai/orchestrator/status
```

#### **Test Skill Execution**

```bash
curl -X POST http://localhost:8000/ai/orchestrator/skills/execute \
  -H "Content-Type: application/json" \
  -d '{
    "skill_name": "web_search",
    "parameters": {
      "query": "Python async programming",
      "num_results": 3
    }
  }'
```

#### **Test Approval Workflow**

```bash
# Request approval
curl -X POST http://localhost:8000/ai/approvals/request \
  -H "Content-Type: application/json" \
  -d '{
    "item_type": "skill",
    "item_name": "web_search",
    "config": {"name": "web_search", "enabled": true},
    "reason": "Testing approval workflow"
  }'

# List pending approvals
curl http://localhost:8000/ai/approvals/pending

# Approve (replace REQUEST_ID with actual ID)
curl -X POST http://localhost:8000/ai/approvals/REQUEST_ID/approve \
  -H "Content-Type: application/json" \
  -d '{"approver": "test_user"}'
```

#### **Test Memory Search Skill**

```bash
curl -X POST http://localhost:8000/ai/orchestrator/skills/execute \
  -H "Content-Type: application/json" \
  -d '{
    "skill_name": "memory_search",
    "parameters": {
      "query": "user preferences",
      "k": 5
    }
  }'
```

---

## 📊 Built-in Skills

| Skill | Category | Description |
|-------|----------|-------------|
| **web_search** | research | Search web using DuckDuckGo |
| **memory_search** | memory | Search AI memory system |
| **code_analysis** | development | Analyze code with LLM |

---

## 🎯 Use Cases

### **1. Multi-Agent Research**

```python
# Create research team
orchestrator.create_agent("researcher", {...}, approve=True)
orchestrator.create_agent("writer", {...}, approve=True)

# Researcher uses web_search skill
search_skill = orchestrator.load_skill("web_search")
results = search_skill.execute(query="AI trends", num_results=10)

# Store in memory
orchestrator.route_memory({"research": results}, importance=2)

# Writer recalls memory
memory_skill = orchestrator.load_skill("memory_search")
context = memory_skill.execute(query="AI trends", k=5)
```

### **2. Code Review Agent**

```python
# Create code reviewer
orchestrator.create_agent("code_reviewer", {...}, approve=True)

# Use code_analysis skill
analysis_skill = orchestrator.load_skill("code_analysis")
result = analysis_skill.execute(
    code="def hello(): print('world')",
    language="python"
)
```

---

## ✅ Summary

**The Orchestrator provides:**

- ✅ **Centralized agent management**
- ✅ **Dynamic skill loading**
- ✅ **Auto-discovery from folder structure**
- ✅ **Hybrid JSON + Python configuration**
- ✅ **Permission-based execution**
- ✅ **Memory routing by importance**
- ✅ **Audit logging**
- ✅ **RESTful API**
- ✅ **Hot reload support**

**Ready to orchestrate intelligent multi-agent systems!** 🎭🚀

