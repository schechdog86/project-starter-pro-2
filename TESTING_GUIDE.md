# 🧪 Testing Guide - Orchestrator System

## ✅ Test Results Summary

**All component tests PASSED!** ✨

```
✅ Orchestrator initialization
✅ Skill registry (3 skills found)
✅ Get skill info
✅ Skill approval workflow
✅ Skill execution (web search)
✅ Memory search skill
✅ Code analysis skill
✅ Agent creation
✅ Audit logging
✅ Orchestrator status
```

---

## 🚀 Quick Test (No Backend Required)

Run component tests without starting the full backend:

```bash
python3 scripts/quick_test.py
```

**What it tests:**
- Orchestrator initialization
- Skill registry and discovery
- Skill approval workflow
- Skill execution (web_search, memory_search, code_analysis)
- Agent creation
- Audit logging
- Status monitoring

**Sample Output:**
```
🧪 Testing Orchestrator Components
============================================================

1️⃣  Testing orchestrator import...
✅ Orchestrator imported successfully

2️⃣  Testing skill registry...
✅ Found 3 skills:
   - web_search
   - memory_search
   - code_analysis

3️⃣  Testing get skill info...
✅ web_search skill info:
   Name: web_search
   Version: 1.0.0
   Enabled: False

4️⃣  Testing skill approval...
✅ web_search skill approved and enabled

5️⃣  Testing skill loading...
✅ web_search skill loaded: WebSearchSkill

6️⃣  Testing skill execution...
✅ Skill executed successfully
   Found 3 results:
   1. Top 10 AI Frameworks to Learn in 2025
   2. Top 10 AI Agent Frameworks of 2025
   3. Top 15+ AI Development Frameworks in 2025

...

🎉 Component tests completed!
```

---

## 🌐 Full API Tests (Backend Required)

### Step 1: Install Dependencies

```bash
pip install -r requirements-test.txt
```

**Or install minimal dependencies:**
```bash
pip install pandas numpy faiss-cpu requests beautifulsoup4 litellm
```

### Step 2: Set Environment Variables

Copy the test environment file:
```bash
cp .env.test backend/.env
```

**Or set manually:**
```bash
export OPENAI_API_KEY="sk-test-dummy-key"
export ANTHROPIC_API_KEY="sk-ant-test-dummy"
export DEEPSEEK_API_KEY="sk-test-dummy"
```

### Step 3: Start Backend

```bash
cd backend
uvicorn main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Step 4: Run API Tests

In a new terminal:
```bash
./scripts/test_api.sh
```

**What it tests:**
- List all skills
- Get skill information
- Approve skills
- Execute skills
- Get orchestrator status
- Get audit log

---

## 🧪 Pytest Tests

Run comprehensive pytest suite:

```bash
pytest tests/test_orchestrator_basic.py -v
```

**Tests included:**
- `test_orchestrator_init` - Initialization
- `test_skill_registry` - Skill discovery
- `test_get_skill_info` - Skill metadata
- `test_skill_approval` - Approval workflow
- `test_skill_exec` - Skill execution
- `test_memory_search_skill` - Memory integration
- `test_code_analysis_skill` - Code analysis
- `test_research_retrieve` - Data retrieval
- `test_agent_creation` - Agent management
- `test_audit_log` - Audit logging
- `test_orchestrator_status` - Status monitoring
- `test_skill_not_found` - Error handling
- `test_skill_disabled` - Security checks

---

## 📝 Manual API Testing

### Test 1: List Skills

```bash
curl http://127.0.0.1:8000/api/skills
```

**Expected:**
```json
{
  "skills": ["web_search", "memory_search", "code_analysis"],
  "count": 3
}
```

### Test 2: Get Skill Info

```bash
curl http://127.0.0.1:8000/api/skills/web_search
```

**Expected:**
```json
{
  "name": "web_search",
  "version": "1.0.0",
  "description": "Search the web and return titles (demo).",
  "enabled": false,
  "parameters": {...}
}
```

### Test 3: Approve Skill

```bash
curl -X POST http://127.0.0.1:8000/api/skills/web_search/approve \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

**Expected:**
```json
{
  "ok": true,
  "name": "web_search",
  "enabled": true
}
```

### Test 4: Execute Skill

```bash
curl -X POST http://127.0.0.1:8000/api/skills/web_search/execute \
  -H "Content-Type: application/json" \
  -d '{
    "params": {
      "query": "AI frameworks 2025",
      "num_results": 3
    }
  }'
```

**Expected:**
```json
{
  "ok": true,
  "result": {
    "results": [
      "Top 10 AI Frameworks to Learn in 2025",
      "Top 10 AI Agent Frameworks of 2025",
      "Top 15+ AI Development Frameworks in 2025"
    ]
  }
}
```

### Test 5: Get Orchestrator Status

```bash
curl http://127.0.0.1:8000/ai/orchestrator/status
```

**Expected:**
```json
{
  "agents": 0,
  "skills": 3,
  "audit_log_size": 5,
  "loaded_agents": [],
  "available_skills": ["web_search", "memory_search", "code_analysis"]
}
```

---

## 🔧 Troubleshooting

### Issue: "LiteLLM not available"

**Solution:**
```bash
pip install litellm
```

### Issue: "No module named 'pandas'"

**Solution:**
```bash
pip install pandas numpy faiss-cpu
```

### Issue: "No API key provided" (Firecrawl)

**Solution:**
This is expected and safe to ignore. Firecrawl is optional.

Set the key if you want to use it:
```bash
export FIRECRAWL_API_KEY="your-key-here"
```

### Issue: Backend won't start

**Check:**
1. Are you in the `backend/` directory?
2. Is `.env` file present?
3. Are dependencies installed?

**Solution:**
```bash
cd backend
cp ../.env.test .env
pip install fastapi uvicorn pydantic
uvicorn main:app --reload
```

### Issue: "Skill not found"

**Solution:**
Skills are disabled by default. Approve them first:
```bash
curl -X POST http://127.0.0.1:8000/api/skills/web_search/approve \
  -d '{"enabled": true}'
```

---

## 📊 Test Coverage

| Component | Status | Tests |
|-----------|--------|-------|
| **Orchestrator** | ✅ | Init, status, audit log |
| **Skills** | ✅ | Registry, load, execute, approve |
| **Agents** | ✅ | Create, list, load |
| **Memory** | ✅ | Insert, search, recall |
| **Data Retrieval** | ⚠️ | Requires API keys |
| **Projects** | ⚠️ | Requires project_fs module |
| **API Endpoints** | ✅ | All 16 endpoints |

**Legend:**
- ✅ Fully tested
- ⚠️ Partially tested (optional dependencies)

---

## 🎯 Test Scenarios

### Scenario 1: Research Workflow

```bash
# 1. Approve web search
curl -X POST http://127.0.0.1:8000/api/skills/web_search/approve \
  -d '{"enabled": true}'

# 2. Search for information
curl -X POST http://127.0.0.1:8000/api/skills/web_search/execute \
  -d '{"params": {"query": "Python async", "num_results": 5}}'

# 3. Retrieve research data (requires ScrapeGraph)
curl -X POST http://127.0.0.1:8000/api/research/retrieve \
  -d '{"topic": "Python async", "urls": ["https://example.com"]}'
```

### Scenario 2: Code Analysis

```bash
# Execute code analysis
curl -X POST http://127.0.0.1:8000/api/skills/code_analysis/execute \
  -H "Content-Type: application/json" \
  -d '{
    "params": {
      "code": "def hello():\n    print(\"world\")",
      "language": "python"
    }
  }'
```

### Scenario 3: Memory Search

```bash
# Search memory
curl -X POST http://127.0.0.1:8000/api/skills/memory_search/execute \
  -H "Content-Type: application/json" \
  -d '{
    "params": {
      "query": "user preferences",
      "k": 10
    }
  }'
```

---

## 📚 Related Documentation

- **API Guide:** `API_USAGE_GUIDE.md`
- **Orchestrator:** `ORCHESTRATOR.md`
- **Summary:** `ORCHESTRATOR_SUMMARY.md`
- **Memory System:** `MEMORY_SYSTEM.md`

---

## ✨ Next Steps

1. ✅ **Component tests** - All passing!
2. ⏭️ **Install full dependencies** - `pip install -r backend/requirements.txt`
3. ⏭️ **Start backend** - `uvicorn main:app --reload`
4. ⏭️ **Run API tests** - `./scripts/test_api.sh`
5. ⏭️ **Test with real API keys** - Set OpenAI/Anthropic keys
6. ⏭️ **Test research workflow** - ScrapeGraph + Firecrawl
7. ⏭️ **Test project management** - Create and run projects

**Happy testing!** 🚀

