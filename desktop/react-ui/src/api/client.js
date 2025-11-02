import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export const api = axios.create({
  baseURL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// ============================================================
// API Methods
// ============================================================

export const apiClient = {
  // Health
  health: () => api.get('/api/health'),

  // Projects
  projects: {
    list: (params) => api.get('/api/projects', { params }),
    get: (id) => api.get(`/api/projects/${id}`),
    create: (data) => api.post('/api/projects', data),
    update: (id, data) => api.put(`/api/projects/${id}`, data),
    delete: (id) => api.delete(`/api/projects/${id}`),
    run: (name) => api.post('/ai/projects/run', { name }),
    status: (name) => api.get(`/ai/projects/${name}/status`),

  },

  // AI Status
  ai: {
    status: () => api.get('/ai/status'),
    health: () => api.get('/ai/health'),
  },

  // Frameworks
  frameworks: {
    list: () => api.get('/ai/frameworks'),
    byCategory: (category) => api.get(`/ai/frameworks/${category}`),
  },

  // LLM
  llm: {
    chat: (data) => api.post('/ai/chat', data),
    chatHistory: (data) => api.post('/ai/chat/history', data),
    providers: () => api.get('/ai/llm/providers'),
    models: (provider) => api.get(`/ai/llm/models/${provider}`),
  },

  // Project RAG
  rag: {
    add: (name, data) => api.post(`/ai/projects/${name}/rag/add`, data),
    ingest: (name, data) => api.post(`/ai/projects/${name}/rag/ingest`, data),
    search: (name, params) => api.get(`/ai/projects/${name}/rag/search`, { params }),
    upload: (name, formData) => api.post(`/ai/projects/${name}/rag/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  },

  docs: {
    list: (name, params) => api.get(`/ai/projects/${name}/docs/list`, { params }),
  },

  // Memory System
  memory: {
    insert: (data) => api.post('/ai/memory/insert', data),
    search: (data) => api.post('/ai/memory/search', data),
    teach: (data) => api.post('/ai/memory/teach', data),
    recall: (data) => api.post('/ai/memory/recall', data),
    stats: () => api.get('/ai/memory/stats'),
    validate: (id) => api.get(`/ai/memory/validate/${id}`),
  },

  // Orchestrator
  orchestrator: {
    status: () => api.get('/ai/orchestrator/status'),
    agents: () => api.get('/ai/orchestrator/agents'),
    createAgent: (data) => api.post('/ai/orchestrator/agents', data),
    destroyAgent: (name) => api.delete(`/ai/orchestrator/agents/${name}`),
    auditLog: (limit) => api.get('/ai/orchestrator/audit-log', { params: { limit } }),
    skills: () => api.get('/ai/orchestrator/skills'),
    getSkill: (name) => api.get(`/ai/orchestrator/skills/${name}`),
    executeSkill: (data) => api.post('/ai/orchestrator/skills/execute', data),
    reloadSkills: () => api.post('/ai/orchestrator/skills/reload'),
  },

  // Skills
  skills: {
    list: () => api.get('/ai/skills'),
    get: (name) => api.get(`/ai/skills/${name}`),
    add: (data) => api.post('/ai/skills', data),
    approve: (name, data) => api.post(`/ai/skills/${name}/approve`, data),
    execute: (name, data) => api.post(`/ai/skills/${name}/execute`, data),
    generate: (data) => api.post('/ai/skills/generate', data),
    reload: () => api.post('/ai/orchestrator/skills/reload'),
  },

  // Research
  research: {
    retrieve: (data) => api.post('/ai/research/retrieve', data),
  },

  // Approvals
  approvals: {
    pending: () => api.get('/ai/approvals/pending'),
    get: (id) => api.get(`/ai/approvals/${id}`),
    request: (data) => api.post('/ai/approvals/request', data),
    approve: (id, data) => api.post(`/ai/approvals/${id}/approve`, data),
    reject: (id, data) => api.post(`/ai/approvals/${id}/reject`, data),
  },

  // Auth
  auth: {
    register: (data) => api.post('/auth/register', data),
    login: (data) => api.post('/auth/login', data),
  },
}

export default api

