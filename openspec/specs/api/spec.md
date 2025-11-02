# API Specification

**Version**: 2.0.0
**Last Updated**: 2025-11-02
**Status**: Active

## Purpose

Define internal and external service interfaces for Project Starter Pro 2, including REST endpoints, request/response formats, authentication, and error handling.

---

## API Architecture

### API Layers

1. **Internal Python APIs**: Module-to-module communication
2. **CLI Interface**: Command-line tool for user interaction
3. **REST API**: HTTP endpoints for local/remote access (optional)
4. **Integration APIs**: External service connectors

### Design Principles

- **RESTful**: Follow REST conventions for HTTP APIs
- **Consistent**: Uniform naming, structure, and patterns
- **Versioned**: Explicit versioning in all APIs
- **Documented**: Self-documenting with OpenAPI/Swagger
- **Secure**: Authentication and authorization on all endpoints
- **Validated**: Input validation at API boundaries

---

## Internal Endpoints

### Base URL (Local Mode)
```
http://localhost:8080/api/v1
```

### Authentication

**Local Mode**: No authentication required (OS-level security)

**Team Mode**: Token-based authentication
```http
Authorization: Bearer <jwt_token>
```

---

## Project Management API

### List Projects

**Endpoint**: `GET /projects`

**Query Parameters**:
- `status` (optional): Filter by status (PLANNING|ACTIVE|PAUSED|COMPLETED|ARCHIVED)
- `type` (optional): Filter by type (software|business|research|personal)
- `tag` (optional): Filter by tag
- `sort` (optional): Sort field (name|created_at|updated_at), default: updated_at
- `order` (optional): Sort order (asc|desc), default: desc
- `limit` (optional): Max results, default: 100
- `offset` (optional): Pagination offset, default: 0

**Response**: `200 OK`
```json
{
  "status": "success",
  "data": {
    "projects": [
      {
        "id": "proj_abc123",
        "name": "My Project",
        "description": "Project description",
        "type": "software",
        "status": "ACTIVE",
        "created_at": "2025-10-30T10:00:00Z",
        "updated_at": "2025-10-30T12:00:00Z",
        "owner": "user_123",
        "tags": ["web", "frontend"],
        "stats": {
          "total_tasks": 25,
          "completed_tasks": 12
        }
      }
    ],
    "total": 1,
    "limit": 100,
    "offset": 0
  }
}
```

### Create Project

**Endpoint**: `POST /projects`

**Request Body**:
```json
{
  "name": "New Project",
  "description": "Project description",
  "type": "software",
  "template_id": "template_123",
  "tags": ["web", "api"],
  "settings": {
    "auto_sync": true,
    "notifications": true
  }
}
```

**Response**: `201 Created`
```json
{
  "status": "success",
  "data": {
    "project": {
      "id": "proj_xyz789",
      "name": "New Project",
      "description": "Project description",
      "type": "software",
      "status": "PLANNING",
      "created_at": "2025-10-30T13:00:00Z",
      "updated_at": "2025-10-30T13:00:00Z",
      "owner": "user_123",
      "tags": ["web", "api"]
    }
  },
  "message": "Project created successfully"
}
```

### Get Project

**Endpoint**: `GET /projects/{id}`

**Response**: `200 OK`
```json
{
  "status": "success",
  "data": {
    "project": {
      "id": "proj_abc123",
      "name": "My Project",
      "description": "Detailed project information",
      "type": "software",
      "status": "ACTIVE",
      "created_at": "2025-10-30T10:00:00Z",
      "updated_at": "2025-10-30T12:00:00Z",
      "owner": "user_123",
      "tags": ["web", "frontend"],
      "milestones": [
        {
          "id": "milestone_1",
          "name": "MVP Release",
          "target_date": "2025-12-31T00:00:00Z",
          "status": "PENDING"
        }
      ],
      "stats": {
        "total_tasks": 25,
        "completed_tasks": 12,
        "total_notes": 15,
        "total_research_items": 8
      }
    }
  }
}
```

### Update Project

**Endpoint**: `PUT /projects/{id}`

**Request Body**:
```json
{
  "name": "Updated Project Name",
  "description": "Updated description",
  "status": "ACTIVE",
  "tags": ["web", "frontend", "react"]
}
```

**Response**: `200 OK`
```json
{
  "status": "success",
  "data": {
    "project": {
      "id": "proj_abc123",
      "name": "Updated Project Name",
      "updated_at": "2025-10-30T14:00:00Z"
    }
  },
  "message": "Project updated successfully"
}
```

### Delete Project

**Endpoint**: `DELETE /projects/{id}`

**Query Parameters**:
- `force` (optional): Permanent delete if true, default: false (soft delete)

**Response**: `204 No Content`

### Archive Project

**Endpoint**: `POST /projects/{id}/archive`

**Response**: `200 OK`
```json
{
  "status": "success",
  "data": {
    "project": {
      "id": "proj_abc123",
      "status": "ARCHIVED",
      "archived_at": "2025-10-30T15:00:00Z"
    }
  },
  "message": "Project archived successfully"
}
```

---

## Notes Management API

### List Notes

**Endpoint**: `GET /projects/{project_id}/notes`

**Query Parameters**:
- `tag` (optional): Filter by tag
- `folder` (optional): Filter by folder path
- `favorite` (optional): Filter favorites (true|false)
- `archived` (optional): Include archived (true|false), default: false
- `sort` (optional): Sort field (title|created_at|updated_at)
- `limit` (optional): Max results, default: 100
- `offset` (optional): Pagination offset

**Response**: `200 OK`
```json
{
  "status": "success",
  "data": {
    "notes": [
      {
        "id": "note_xyz789",
        "project_id": "proj_abc123",
        "title": "Implementation Notes",
        "folder_path": "/docs",
        "tags": ["architecture", "backend"],
        "created_at": "2025-10-30T10:00:00Z",
        "updated_at": "2025-10-30T11:30:00Z",
        "is_favorite": true,
        "ai_summary": "Notes on API architecture..."
      }
    ],
    "total": 1
  }
}
```

### Create Note

**Endpoint**: `POST /projects/{project_id}/notes`

**Request Body**:
```json
{
  "title": "New Note",
  "content": "# Note Content\n\nMarkdown content here...",
  "tags": ["important", "todo"],
  "folder_path": "/docs"
}
```

**Response**: `201 Created`

### Get Note

**Endpoint**: `GET /notes/{id}`

**Response**: `200 OK`
```json
{
  "status": "success",
  "data": {
    "note": {
      "id": "note_xyz789",
      "project_id": "proj_abc123",
      "title": "Implementation Notes",
      "content": "# Implementation Notes\n\n...",
      "tags": ["architecture", "backend"],
      "folder_path": "/docs",
      "attachments": [
        {
          "id": "att_1",
          "name": "diagram.png",
          "path": "attachments/diagram.png",
          "type": "image/png",
          "size": 45678
        }
      ],
      "links": ["note_abc456"],
      "created_at": "2025-10-30T10:00:00Z",
      "updated_at": "2025-10-30T11:30:00Z",
      "ai_summary": "Notes on API architecture design decisions..."
    }
  }
}
```

### Update Note

**Endpoint**: `PUT /notes/{id}`

**Request Body**:
```json
{
  "title": "Updated Title",
  "content": "Updated content...",
  "tags": ["architecture", "backend", "api"]
}
```

**Response**: `200 OK`

### Delete Note

**Endpoint**: `DELETE /notes/{id}`

**Response**: `204 No Content`

### Generate Note Summary

**Endpoint**: `POST /notes/{id}/summary`

**Response**: `200 OK`
```json
{
  "status": "success",
  "data": {
    "summary": "AI-generated summary of the note content...",
    "key_points": [
      "Point 1",
      "Point 2",
      "Point 3"
    ]
  }
}
```

### Search Notes

**Endpoint**: `GET /notes/search`

**Query Parameters**:
- `q` (required): Search query
- `project_id` (optional): Limit to specific project
- `semantic` (optional): Use semantic search (true|false), default: false
- `limit` (optional): Max results, default: 20

**Response**: `200 OK`
```json
{
  "status": "success",
  "data": {
    "results": [
      {
        "note_id": "note_xyz789",
        "title": "Implementation Notes",
        "relevance_score": 0.95,
        "snippet": "...matching content snippet..."
      }
    ],
    "total": 1
  }
}
```

---

## Research Management API

### Import Research Source

**Endpoint**: `POST /projects/{project_id}/research`

**Request Body**:
```json
{
  "url": "https://example.com/article",
  "source_type": "WEB",
  "auto_process": true
}
```

**Response**: `201 Created`
```json
{
  "status": "success",
  "data": {
    "research_item": {
      "id": "research_123",
      "project_id": "proj_abc123",
      "title": "Article Title",
      "source_type": "WEB",
      "url": "https://example.com/article",
      "relevance_score": 0.85,
      "created_at": "2025-10-30T12:00:00Z"
    }
  },
  "message": "Research source imported successfully"
}
```

### List Research Items

**Endpoint**: `GET /projects/{project_id}/research`

**Query Parameters**:
- `source_type` (optional): Filter by type (WEB|PDF|SNIPPET|IMAGE|VIDEO|MANUAL)
- `tag` (optional): Filter by tag
- `min_relevance` (optional): Minimum relevance score (0.0-1.0)
- `sort` (optional): Sort field
- `limit` (optional): Max results

**Response**: `200 OK`

### Get Research Item

**Endpoint**: `GET /research/{id}`

**Response**: `200 OK`
```json
{
  "status": "success",
  "data": {
    "research_item": {
      "id": "research_123",
      "project_id": "proj_abc123",
      "title": "React Best Practices 2025",
      "source_type": "WEB",
      "url": "https://example.com/react-best-practices",
      "summary": "AI-generated summary...",
      "tags": ["react", "javascript"],
      "topics": ["hooks", "performance"],
      "relevance_score": 0.92,
      "facts": [
        {
          "id": "fact_1",
          "text": "React 18 introduces automatic batching",
          "confidence": 0.95
        }
      ],
      "quotes": [
        {
          "id": "quote_1",
          "text": "Always use functional components",
          "author": "Dan Abramov"
        }
      ]
    }
  }
}
```

### Synthesize Research

**Endpoint**: `POST /projects/{project_id}/research/synthesize`

**Request Body**:
```json
{
  "topic": "React Performance Optimization",
  "source_ids": ["research_123", "research_456"]
}
```

**Response**: `200 OK`
```json
{
  "status": "success",
  "data": {
    "synthesis": {
      "topic": "React Performance Optimization",
      "summary": "Combined insights from multiple sources...",
      "key_points": [
        "Use React.memo for expensive components",
        "Implement code splitting",
        "Optimize re-renders"
      ],
      "recommendations": [
        "Start with profiling",
        "Focus on bottlenecks"
      ],
      "sources_used": ["research_123", "research_456"]
    }
  }
}
```

---

## Analytics API

### Get Metrics

**Endpoint**: `GET /projects/{project_id}/metrics`

**Response**: `200 OK`
```json
{
  "status": "success",
  "data": {
    "metrics": {
      "task_completion_rate": 0.48,
      "velocity": 12.5,
      "cycle_time_avg": 3.2,
      "lead_time_avg": 5.8,
      "throughput": 8,
      "work_in_progress": 5,
      "blocked_tasks": 1
    },
    "timestamp": "2025-10-30T12:00:00Z"
  }
}
```

### Generate Report

**Endpoint**: `POST /projects/{project_id}/analytics/reports`

**Request Body**:
```json
{
  "report_type": "VELOCITY",
  "period": {
    "start_date": "2025-10-01T00:00:00Z",
    "end_date": "2025-10-30T23:59:59Z"
  }
}
```

**Response**: `201 Created`
```json
{
  "status": "success",
  "data": {
    "report": {
      "id": "report_123",
      "project_id": "proj_abc123",
      "report_type": "VELOCITY",
      "generated_at": "2025-10-30T12:00:00Z",
      "metrics": {
        "average_velocity": 12.3,
        "velocity_trend": "UP"
      },
      "insights": [
        {
          "type": "OBSERVATION",
          "text": "Velocity increased 15% this month"
        }
      ]
    }
  }
}
```

### Get Predictions

**Endpoint**: `GET /projects/{project_id}/predictions`

**Response**: `200 OK`
```json
{
  "status": "success",
  "data": {
    "predictions": {
      "estimated_completion_date": "2025-12-15T00:00:00Z",
      "confidence": 0.82,
      "assumptions": [
        "Current velocity maintained",
        "No major blockers"
      ]
    }
  }
}
```

### Get Bottlenecks

**Endpoint**: `GET /projects/{project_id}/bottlenecks`

**Response**: `200 OK`
```json
{
  "status": "success",
  "data": {
    "bottlenecks": [
      {
        "type": "BLOCKED_TASKS",
        "severity": "HIGH",
        "description": "3 tasks blocked by external dependency",
        "affected_tasks": ["task_1", "task_2", "task_3"],
        "recommendation": "Follow up with external team"
      }
    ]
  }
}
```

---

## Configuration API

### Get Settings

**Endpoint**: `GET /config`

**Response**: `200 OK`
```json
{
  "status": "success",
  "data": {
    "settings": {
      "system": {
        "version": "1.0.0",
        "log_level": "INFO"
      },
      "features": {
        "analytics": true,
        "research": true
      },
      "user_preferences": {
        "theme_mode": "dark",
        "language": "en"
      }
    }
  }
}
```

### Update Settings

**Endpoint**: `PUT /config`

**Request Body**:
```json
{
  "user_preferences": {
    "theme_mode": "light",
    "notifications_enabled": true
  }
}
```

**Response**: `200 OK`

---

## External Sync API

### Upload Project Data

**Endpoint**: `POST /sync/upload`

**Request Body**:
```json
{
  "project_id": "proj_abc123",
  "target": "cloud",
  "force": false
}
```

**Response**: `200 OK`
```json
{
  "status": "success",
  "data": {
    "sync_result": {
      "project_id": "proj_abc123",
      "files_uploaded": 25,
      "bytes_uploaded": 1048576,
      "duration_ms": 1234,
      "conflicts": []
    }
  },
  "message": "Project data uploaded successfully"
}
```

### Download Project Data

**Endpoint**: `POST /sync/download`

**Request Body**:
```json
{
  "project_id": "proj_abc123",
  "source": "cloud"
}
```

**Response**: `200 OK`

---

## System Status API

### Health Check

**Endpoint**: `GET /status`

**Response**: `200 OK`
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime_seconds": 86400,
  "services": {
    "database": "healthy",
    "cache": "healthy",
    "sync": "healthy"
  }
}
```

### Version Info

**Endpoint**: `GET /version`

**Response**: `200 OK`
```json
{
  "version": "1.0.0",
  "build": "20251030",
  "python_version": "3.13.5",
  "node_version": "20.10.0"
}
```

---

## Error Responses

### Error Format

All errors follow this structure:

```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "field_name",
      "constraint": "validation_rule",
      "value": "invalid_value"
    }
  }
}
```

### HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET/PUT |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid input |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource conflict |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Error Codes

- `VALIDATION_ERROR`: Input validation failed
- `NOT_FOUND`: Resource not found
- `DUPLICATE`: Resource already exists
- `PERMISSION_DENIED`: Insufficient permissions
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Server error

---

---

## AI & Multi-Agent System API

### AI Status & Health

#### Get AI Status
**Endpoint**: `GET /ai/status`

**Response**: `200 OK`
```json
{
  "status": "healthy",
  "frameworks_loaded": 100,
  "orchestrator_active": true,
  "memory_system_active": true
}
```

#### Get AI Health
**Endpoint**: `GET /ai/health`

**Response**: `200 OK`
```json
{
  "status": "healthy",
  "components": {
    "orchestrator": "active",
    "memory": "active",
    "skills": "active"
  }
}
```

### AI Frameworks

#### List All Frameworks
**Endpoint**: `GET /ai/frameworks`

**Response**: `200 OK`
```json
{
  "core": ["langchain", "llamaindex", "haystack", "litellm"],
  "multi_agents": ["autogen", "crewai", "langgraph", "metagpt", "semantic-kernel"],
  "enterprise": ["semantic-kernel", "rasa"],
  "transformers": ["transformers", "sentence-transformers", "datasets"]
}
```

#### Get Frameworks by Category
**Endpoint**: `GET /ai/frameworks/{category}`

**Path Parameters**:
- `category`: core | multi_agents | enterprise | transformers

**Response**: `200 OK`
```json
{
  "category": "multi_agents",
  "frameworks": ["autogen", "crewai", "langgraph", "metagpt"]
}
```

### LLM Chat

#### Single Message Chat
**Endpoint**: `POST /ai/chat`

**Request Body**:
```json
{
  "message": "What is FastAPI?",
  "provider": "openai",
  "model": "gpt-4",
  "temperature": 0.7,
  "max_tokens": 500
}
```

**Response**: `200 OK`
```json
{
  "response": "FastAPI is a modern, fast web framework...",
  "provider": "openai",
  "model": "gpt-4",
  "tokens_used": 150
}
```

#### Chat with History
**Endpoint**: `POST /ai/chat/history`

**Request Body**:
```json
{
  "messages": [
    {"role": "user", "content": "What is FastAPI?"},
    {"role": "assistant", "content": "FastAPI is..."},
    {"role": "user", "content": "How do I install it?"}
  ],
  "provider": "openai",
  "model": "gpt-4"
}
```

**Response**: `200 OK`
```json
{
  "response": "You can install FastAPI using pip...",
  "conversation_id": "conv_123"
}
```

### LLM Providers & Models

#### List LLM Providers
**Endpoint**: `GET /ai/llm/providers`

**Response**: `200 OK`
```json
{
  "providers": [
    {
      "name": "openai",
      "status": "active",
      "models_count": 10
    },
    {
      "name": "anthropic",
      "status": "active",
      "models_count": 5
    }
  ]
}
```

#### Get Models by Provider
**Endpoint**: `GET /ai/llm/models/{provider}`

**Path Parameters**:
- `provider`: openai | anthropic | cohere | google

**Response**: `200 OK`
```json
{
  "provider": "openai",
  "models": [
    {
      "id": "gpt-4",
      "name": "GPT-4",
      "context_window": 8192,
      "pricing": {"input": 0.03, "output": 0.06}
    },
    {
      "id": "gpt-3.5-turbo",
      "name": "GPT-3.5 Turbo",
      "context_window": 4096,
      "pricing": {"input": 0.001, "output": 0.002}
    }
  ]
}
```

### Memory System

#### Insert Memory
**Endpoint**: `POST /ai/memory/insert`

**Request Body**:
```json
{
  "text": "FastAPI uses Pydantic for data validation",
  "metadata": {
    "source": "documentation",
    "topic": "fastapi",
    "importance": 0.8
  }
}
```

**Response**: `200 OK`
```json
{
  "id": "mem_abc123",
  "tier": "LT_HOT",
  "inserted_at": "2025-11-02T10:00:00Z"
}
```

#### Search Memory
**Endpoint**: `POST /ai/memory/search`

**Request Body**:
```json
{
  "query": "How does FastAPI handle validation?",
  "top_k": 5,
  "tier": "all"
}
```

**Response**: `200 OK`
```json
{
  "results": [
    {
      "id": "mem_abc123",
      "text": "FastAPI uses Pydantic for data validation",
      "score": 0.95,
      "tier": "LT_HOT",
      "metadata": {"topic": "fastapi"}
    }
  ],
  "total": 1
}
```

#### Teach to Forever Tier
**Endpoint**: `POST /ai/memory/teach`

**Request Body**:
```json
{
  "text": "Always use async/await for database operations",
  "metadata": {
    "category": "best_practices",
    "importance": 1.0
  }
}
```

**Response**: `200 OK`
```json
{
  "id": "mem_xyz789",
  "tier": "FV",
  "message": "Memory stored in Forever tier"
}
```

#### Semantic Recall
**Endpoint**: `POST /ai/memory/recall`

**Request Body**:
```json
{
  "query": "database best practices",
  "top_k": 10
}
```

**Response**: `200 OK`
```json
{
  "memories": [
    {
      "text": "Always use async/await for database operations",
      "relevance": 0.92,
      "tier": "FV"
    }
  ]
}
```

#### Get Memory Statistics
**Endpoint**: `GET /ai/memory/stats`

**Response**: `200 OK`
```json
{
  "total_memories": 1500,
  "by_tier": {
    "ST": 50,
    "MT": 200,
    "LT_HOT": 800,
    "FV": 450
  },
  "total_size_mb": 25.6
}
```

#### Validate Memory
**Endpoint**: `GET /ai/memory/validate/{id}`

**Path Parameters**:
- `id`: Memory ID

**Response**: `200 OK`
```json
{
  "id": "mem_abc123",
  "valid": true,
  "tier": "LT_HOT",
  "last_accessed": "2025-11-02T09:00:00Z"
}
```

### Orchestrator

#### Get Orchestrator Status
**Endpoint**: `GET /ai/orchestrator/status`

**Response**: `200 OK`
```json
{
  "status": "active",
  "agents_count": 5,
  "skills_count": 12,
  "pending_approvals": 2,
  "uptime_seconds": 86400
}
```

#### List Agents
**Endpoint**: `GET /ai/orchestrator/agents`

**Response**: `200 OK`
```json
{
  "agents": [
    "research_agent",
    "code_analysis_agent",
    "documentation_agent"
  ],
  "total": 3
}
```

#### Create Agent
**Endpoint**: `POST /ai/orchestrator/agents`

**Request Body**:
```json
{
  "name": "research_agent",
  "config": {
    "role": "researcher",
    "skills": ["web_search", "data_analysis"],
    "max_iterations": 10
  },
  "approve": true
}
```

**Response**: `201 Created`
```json
{
  "name": "research_agent",
  "status": "created",
  "approved": true
}
```

#### Destroy Agent
**Endpoint**: `DELETE /ai/orchestrator/agents/{name}`

**Path Parameters**:
- `name`: Agent name

**Response**: `200 OK`
```json
{
  "name": "research_agent",
  "status": "destroyed"
}
```

#### Get Audit Log
**Endpoint**: `GET /ai/orchestrator/audit-log`

**Query Parameters**:
- `limit` (optional): Max entries, default: 100

**Response**: `200 OK`
```json
{
  "entries": [
    {
      "timestamp": "2025-11-02T10:00:00Z",
      "action": "agent_created",
      "agent": "research_agent",
      "user": "admin"
    }
  ],
  "total": 1
}
```

#### List Skills (Orchestrator)
**Endpoint**: `GET /ai/orchestrator/skills`

**Response**: `200 OK`
```json
{
  "skills": [
    {
      "name": "web_search",
      "enabled": true,
      "approved": true
    }
  ]
}
```

#### Get Skill Info
**Endpoint**: `GET /ai/orchestrator/skills/{name}`

**Path Parameters**:
- `name`: Skill name

**Response**: `200 OK`
```json
{
  "name": "web_search",
  "description": "Search the web using DuckDuckGo",
  "parameters": ["query", "num_results"],
  "enabled": true,
  "approved": true
}
```

#### Execute Skill (Orchestrator)
**Endpoint**: `POST /ai/orchestrator/skills/execute`

**Request Body**:
```json
{
  "skill_name": "web_search",
  "params": {
    "query": "FastAPI tutorial",
    "num_results": 5
  }
}
```

**Response**: `200 OK`
```json
{
  "result": {
    "results": ["Result 1", "Result 2", "Result 3"]
  },
  "execution_time_ms": 1250
}
```

#### Reload Skills
**Endpoint**: `POST /ai/orchestrator/skills/reload`

**Response**: `200 OK`
```json
{
  "status": "reloaded",
  "skills_count": 12
}
```

### Skills Management

#### List Skills
**Endpoint**: `GET /ai/skills`

**Response**: `200 OK`
```json
{
  "skills": [
    {
      "name": "web_search",
      "enabled": true,
      "approved": true,
      "description": "Search the web"
    }
  ],
  "total": 12
}
```

#### Get Skill
**Endpoint**: `GET /ai/skills/{name}`

**Path Parameters**:
- `name`: Skill name

**Response**: `200 OK`
```json
{
  "name": "web_search",
  "description": "Search the web using DuckDuckGo",
  "parameters": {
    "query": {"type": "string", "required": true},
    "num_results": {"type": "integer", "default": 5}
  },
  "code": "def execute(query, num_results=5): ...",
  "enabled": true,
  "approved": true
}
```

#### Add Skill
**Endpoint**: `POST /ai/skills`

**Request Body**:
```json
{
  "name": "custom_skill",
  "config": {
    "description": "Custom skill",
    "parameters": ["param1", "param2"]
  },
  "code": "def execute(param1, param2): return {'result': param1 + param2}",
  "enabled": true
}
```

**Response**: `201 Created`
```json
{
  "name": "custom_skill",
  "status": "created",
  "enabled": true
}
```

#### Approve Skill
**Endpoint**: `POST /ai/skills/{name}/approve`

**Path Parameters**:
- `name`: Skill name

**Request Body**:
```json
{
  "enabled": true,
  "approver": "admin"
}
```

**Response**: `200 OK`
```json
{
  "name": "custom_skill",
  "approved": true,
  "enabled": true
}
```

#### Execute Skill
**Endpoint**: `POST /ai/skills/{name}/execute`

**Path Parameters**:
- `name`: Skill name

**Request Body**:
```json
{
  "params": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

**Response**: `200 OK`
```json
{
  "result": {"output": "execution result"},
  "execution_time_ms": 500
}
```

#### Generate Skill
**Endpoint**: `POST /ai/skills/generate`

**Request Body**:
```json
{
  "name": "new_skill",
  "prompt": "Create a skill that fetches weather data for a given city"
}
```

**Response**: `200 OK`
```json
{
  "name": "new_skill",
  "code": "def execute(city): ...",
  "status": "generated",
  "requires_approval": true
}
```

### Research

#### Retrieve Research Data
**Endpoint**: `POST /ai/research/retrieve`

**Request Body**:
```json
{
  "urls": [
    "https://fastapi.tiangolo.com/",
    "https://docs.python.org/3/"
  ],
  "topic": "FastAPI best practices",
  "max_depth": 2
}
```

**Response**: `200 OK`
```json
{
  "results": [
    {
      "url": "https://fastapi.tiangolo.com/",
      "title": "FastAPI Documentation",
      "content": "Scraped content...",
      "metadata": {"crawl_depth": 1}
    }
  ],
  "total": 2,
  "cached": true
}
```

### Approvals Workflow

#### Get Pending Approvals
**Endpoint**: `GET /ai/approvals/pending`

**Response**: `200 OK`
```json
{
  "pending": [
    {
      "id": "approval_123",
      "type": "skill",
      "name": "custom_skill",
      "reason": "User-generated skill",
      "timestamp": "2025-11-02T10:00:00Z",
      "requester": "user_123"
    }
  ],
  "total": 1
}
```

#### Get Approval Details
**Endpoint**: `GET /ai/approvals/{id}`

**Path Parameters**:
- `id`: Approval ID

**Response**: `200 OK`
```json
{
  "id": "approval_123",
  "type": "skill",
  "name": "custom_skill",
  "config": {"description": "Custom skill"},
  "code": "def execute(): ...",
  "status": "pending",
  "timestamp": "2025-11-02T10:00:00Z",
  "requester": "user_123"
}
```

#### Request Approval
**Endpoint**: `POST /ai/approvals/request`

**Request Body**:
```json
{
  "type": "skill",
  "name": "custom_skill",
  "reason": "Need this skill for project",
  "config": {"description": "Custom skill"}
}
```

**Response**: `201 Created`
```json
{
  "id": "approval_124",
  "status": "pending",
  "message": "Approval request submitted"
}
```

#### Approve Request
**Endpoint**: `POST /ai/approvals/{id}/approve`

**Path Parameters**:
- `id`: Approval ID

**Request Body**:
```json
{
  "approver": "admin",
  "notes": "Approved for production use"
}
```

**Response**: `200 OK`
```json
{
  "id": "approval_123",
  "status": "approved",
  "approved_at": "2025-11-02T11:00:00Z",
  "approver": "admin"
}
```

#### Reject Request
**Endpoint**: `POST /ai/approvals/{id}/reject`

**Path Parameters**:
- `id`: Approval ID

**Request Body**:
```json
{
  "rejector": "admin",
  "reason": "Security concerns"
}
```

**Response**: `200 OK`
```json
{
  "id": "approval_123",
  "status": "rejected",
  "rejected_at": "2025-11-02T11:00:00Z",
  "rejector": "admin",
  "reason": "Security concerns"
}
```

### Project Workflows

#### Run Project Workflow
**Endpoint**: `POST /ai/projects/run`

**Request Body**:
```json
{
  "project_name": "my_project",
  "workflow": "planning",
  "agents": ["research_agent", "planning_agent"]
}
```

**Response**: `200 OK`
```json
{
  "project": "my_project",
  "workflow": "planning",
  "status": "running",
  "task_id": "task_abc123"
}
```

#### Get Project Status
**Endpoint**: `GET /ai/projects/{name}/status`

**Path Parameters**:
- `name`: Project name

**Response**: `200 OK`
```json
{
  "project": "my_project",
  "status": "active",
  "phase": "execution",
  "progress": 65,
  "agents_assigned": 3,
  "tasks_completed": 12,
  "tasks_total": 18
}
```

---

## Authentication & Authorization

### Token-Based Auth (Team Mode)

**Login**:
```http
POST /auth/login
Content-Type: application/json

{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "status": "success",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_at": "2025-10-31T12:00:00Z",
    "user": {
      "id": "user_123",
      "name": "John Doe"
    }
  }
}
```

**Register**:
```http
POST /auth/register
Content-Type: application/json

{
  "username": "newuser",
  "password": "securepassword123"
}
```

**Response**:
```json
{
  "msg": "User registered",
  "user_id": "user_456"
}
```

**Using Token**:
```http
GET /projects
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## Rate Limiting

### Limits

- **Anonymous**: 100 requests/hour
- **Authenticated**: 1000 requests/hour
- **Premium**: 10000 requests/hour

### Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1635724800
```

---

## References

- OpenAPI Spec: https://swagger.io/specification/
- REST API Design: https://restfulapi.net/
- JWT: https://jwt.io/

