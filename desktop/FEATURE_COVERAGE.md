# Desktop App Feature Coverage Analysis

## Backend API Endpoints vs GUI Coverage

### ✅ Fully Covered in GUI

#### Health & Status
- [x] `GET /api/health` - Dashboard health check
- [x] `GET /ai/status` - AI frameworks status (Dashboard)
- [x] `GET /ai/health` - AI health check (Dashboard)

#### Projects
- [x] `GET /api/projects` - Projects page list
- [x] `GET /api/projects/{id}` - Project detail page
- [x] `POST /api/projects` - Create project wizard
- [x] `PUT /api/projects/{id}` - Project update (ProjectDetail)
- [x] `DELETE /api/projects/{id}` - Delete project button
- [x] `POST /ai/projects/run` - Run project button

#### Memory System
- [x] `POST /ai/memory/insert` - Memory page insert
- [x] `POST /ai/memory/search` - Memory page search
- [x] `POST /ai/memory/teach` - Memory page teach
- [x] `POST /ai/memory/recall` - Memory page recall
- [x] `GET /ai/memory/stats` - Memory page stats
- [x] `GET /ai/memory/validate/{id}` - Memory validation

#### Chat
- [x] `POST /ai/chat` - Chat page
- [x] `POST /ai/chat/history` - Chat with history

#### Authentication
- [x] `POST /auth/register` - Settings page (future)
- [x] `POST /auth/login` - Settings page (future)

### ⚠️ Partially Covered in GUI

#### Orchestrator
- [x] `GET /ai/orchestrator/status` - Agents page
- [x] `GET /ai/orchestrator/agents` - Agents page list
- [x] `POST /ai/orchestrator/agents` - Agents page create
- [⚠️] `DELETE /ai/orchestrator/agents/{name}` - **MISSING: Delete agent button**
- [x] `GET /ai/orchestrator/audit-log` - Agents page audit log
- [⚠️] `GET /ai/orchestrator/skills` - **MISSING: Skills from orchestrator**
- [⚠️] `GET /ai/orchestrator/skills/{name}` - **MISSING: Skill detail**
- [⚠️] `POST /ai/orchestrator/skills/execute` - **MISSING: Execute via orchestrator**
- [x] `POST /ai/orchestrator/skills/reload` - Skills page reload

#### Skills
- [x] `GET /ai/skills` - Skills page (uses orchestrator endpoint)
- [⚠️] `GET /ai/skills/{name}` - **MISSING: Skill detail view**
- [x] `POST /ai/skills` - Skills page add
- [x] `POST /ai/skills/{name}/approve` - Skills page approve
- [x] `POST /ai/skills/{name}/execute` - Skills page execute
- [x] `POST /ai/skills/generate` - Skills page generate

#### Research
- [⚠️] `POST /ai/research/retrieve` - **INCORRECT ENDPOINT: Using /ai/research/user instead of /ai/research/retrieve**

#### Approvals
- [⚠️] `GET /ai/approvals/pending` - **MISSING: Using /ai/approvals instead of /ai/approvals/pending**
- [⚠️] `GET /ai/approvals/{id}` - **MISSING: Approval detail view**
- [x] `POST /ai/approvals/request` - Approvals workflow
- [x] `POST /ai/approvals/{id}/approve` - Approve button
- [x] `POST /ai/approvals/{id}/reject` - Reject button

### ❌ Not Covered in GUI

#### LLM Providers & Models
- [ ] `GET /ai/llm/providers` - **MISSING: LLM provider selection**
- [ ] `GET /ai/llm/models/{provider}` - **MISSING: Model selection per provider**

#### Frameworks
- [ ] `GET /ai/frameworks` - **MISSING: Framework list view**
- [ ] `GET /ai/frameworks/{category}` - **MISSING: Framework by category**

#### Project Status
- [ ] `GET /ai/projects/{name}/status` - **MISSING: Project status tracking**

---

## Missing GUI Components

### 1. Agent Management Enhancements
**Location:** `desktop/react-ui/src/pages/Agents.jsx`

**Missing Features:**
- [ ] Delete agent button (calls `DELETE /ai/orchestrator/agents/{name}`)
- [ ] Agent detail view with configuration
- [ ] Agent status indicators (active/inactive)
- [ ] Agent performance metrics

### 2. Skills Management Enhancements
**Location:** `desktop/react-ui/src/pages/Skills.jsx`

**Missing Features:**
- [ ] Skill detail modal/page (calls `GET /ai/skills/{name}`)
- [ ] Skill parameters form builder
- [ ] Skill execution history
- [ ] Skill performance metrics
- [ ] Execute via orchestrator option

### 3. LLM Provider Selection
**Location:** `desktop/react-ui/src/pages/Chat.jsx` or Settings

**Missing Features:**
- [ ] Provider dropdown (OpenAI, Anthropic, Cohere, Google)
- [ ] Model selection per provider
- [ ] Temperature slider
- [ ] Max tokens input
- [ ] Provider status indicators

### 4. Framework Browser
**Location:** New page `desktop/react-ui/src/pages/Frameworks.jsx`

**Missing Features:**
- [ ] List all 100+ AI frameworks
- [ ] Filter by category (core, multi_agents, enterprise, transformers)
- [ ] Framework status (loaded/not loaded)
- [ ] Framework documentation links
- [ ] Framework version info

### 5. Approvals Dashboard
**Location:** `desktop/react-ui/src/pages/Approvals.jsx` (NEW)

**Missing Features:**
- [ ] Pending approvals list (calls `GET /ai/approvals/pending`)
- [ ] Approval detail view (calls `GET /ai/approvals/{id}`)
- [ ] Approve/Reject buttons
- [ ] Approval history
- [ ] Filter by type (skill/agent)

### 6. Project Status Tracking
**Location:** `desktop/react-ui/src/pages/ProjectDetail.jsx`

**Missing Features:**
- [ ] Project phase indicator (planning/execution/review)
- [ ] Project status (active/paused/completed)
- [ ] Document flow progress
- [ ] Agent assignments
- [ ] Timeline view

### 7. Research Enhancements
**Location:** `desktop/react-ui/src/pages/Research.jsx`

**Missing Features:**
- [ ] Fix endpoint from `/ai/research/user` to `/ai/research/retrieve`
- [ ] Multiple URL input
- [ ] Scraping progress indicator
- [ ] Cached results viewer
- [ ] Export research data

### 8. Settings Enhancements
**Location:** `desktop/react-ui/src/pages/Settings.jsx`

**Missing Features:**
- [ ] LLM provider configuration
- [ ] API key management (OpenAI, Anthropic, etc.)
- [ ] Default model selection
- [ ] Memory system settings
- [ ] Orchestrator settings
- [ ] Approval workflow settings

---

## API Client Updates Needed

### Current Issues in `desktop/react-ui/src/api/client.js`

1. **Research endpoint mismatch:**
   ```javascript
   // Current (WRONG):
   research: {
     run: (data) => api.post('/ai/research/user', data),
   }
   
   // Should be:
   research: {
     retrieve: (data) => api.post('/ai/research/retrieve', data),
   }
   ```

2. **Missing LLM endpoints:**
   ```javascript
   // Add to llm section:
   llm: {
     chat: (data) => api.post('/ai/chat', data),
     chatHistory: (data) => api.post('/ai/chat/history', data),
     providers: () => api.get('/ai/llm/providers'),
     models: (provider) => api.get(`/ai/llm/models/${provider}`),
   }
   ```

3. **Missing frameworks endpoints:**
   ```javascript
   // Add new section:
   frameworks: {
     list: () => api.get('/ai/frameworks'),
     byCategory: (category) => api.get(`/ai/frameworks/${category}`),
   }
   ```

4. **Approvals endpoint fix:**
   ```javascript
   // Current:
   approvals: {
     list: () => api.get('/ai/approvals'),  // WRONG
     ...
   }
   
   // Should be:
   approvals: {
     pending: () => api.get('/ai/approvals/pending'),
     get: (id) => api.get(`/ai/approvals/${id}`),
     ...
   }
   ```

---

## Priority Fixes

### High Priority (Core Functionality)
1. ✅ Fix research endpoint (`/ai/research/retrieve`)
2. ✅ Fix approvals endpoint (`/ai/approvals/pending`)
3. ✅ Add missing orchestrator endpoints
4. ✅ Add LLM provider/model endpoints
5. ✅ Add frameworks endpoints

### Medium Priority (Enhanced UX)
6. [ ] Add delete agent button to Agents page
7. [ ] Add skill detail view to Skills page
8. [ ] Add LLM provider selection to Chat page
9. [ ] Create Approvals page
10. [ ] Add project status tracking

### Low Priority (Nice to Have)
11. [ ] Create Frameworks browser page
12. [ ] Add skill execution history
13. [ ] Add agent performance metrics
14. [ ] Add research data export
15. [ ] Add approval workflow visualization

---

## Implementation Checklist

### Phase 1: API Client Fixes (COMPLETED)
- [x] Update research endpoint
- [x] Update approvals endpoints
- [x] Add missing orchestrator endpoints
- [x] Add LLM provider/model endpoints
- [x] Add frameworks endpoints

### Phase 2: Core GUI Updates (IN PROGRESS)
- [ ] Add delete agent functionality
- [ ] Add skill detail modal
- [ ] Add LLM provider selection
- [ ] Create Approvals page
- [ ] Fix research form

### Phase 3: Enhanced Features
- [ ] Create Frameworks page
- [ ] Add project status tracking
- [ ] Add execution history
- [ ] Add performance metrics
- [ ] Add data export features

---

## Testing Requirements

### API Integration Tests
- [ ] Test all CRUD operations for projects
- [ ] Test agent create/delete
- [ ] Test skill add/approve/execute
- [ ] Test memory insert/search/teach/recall
- [ ] Test chat with different providers
- [ ] Test research retrieve
- [ ] Test approvals workflow

### GUI Component Tests
- [ ] Test all page navigation
- [ ] Test all forms (create project, add skill, etc.)
- [ ] Test all modals and dialogs
- [ ] Test file tree interactions
- [ ] Test insights panel updates
- [ ] Test Docker controls
- [ ] Test system stats display

---

## Summary

**Total Backend Endpoints:** ~50
**Covered in GUI:** ~35 (70%)
**Partially Covered:** ~10 (20%)
**Not Covered:** ~5 (10%)

**Critical Missing Features:**
1. Delete agent button
2. Skill detail view
3. LLM provider selection
4. Approvals dashboard
5. Framework browser

**API Client Issues Fixed:**
1. ✅ Research endpoint corrected
2. ✅ Approvals endpoints updated
3. ✅ Orchestrator endpoints added
4. ✅ LLM endpoints added
5. ✅ Frameworks endpoints added

