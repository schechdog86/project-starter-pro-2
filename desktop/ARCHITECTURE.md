# Desktop App Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     ELECTRON DESKTOP APP                        │
│                   (Cross-platform: Win/Mac/Linux)               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Main Process │    │   Preload    │    │   Renderer   │
│  (Node.js)   │◄──►│  (Bridge)    │◄──►│   (React)    │
│              │    │              │    │              │
│ • IPC        │    │ • Context    │    │ • UI         │
│ • Docker     │    │   Bridge     │    │ • Components │
│ • System     │    │ • Secure API │    │ • Pages      │
│ • Files      │    │              │    │ • Hooks      │
└──────┬───────┘    └──────────────┘    └──────┬───────┘
       │                                        │
       │                                        │
       ▼                                        ▼
┌──────────────┐                      ┌──────────────┐
│   Docker     │                      │  Backend API │
│   Engine     │                      │ (FastAPI)    │
│              │                      │              │
│ • Compose    │                      │ • REST API   │
│ • Containers │                      │ • WebSocket  │
│ • Logs       │                      │ • AI/ML      │
└──────────────┘                      └──────────────┘
```

## Component Architecture

### 1. Electron Main Process (`main.js`)

**Responsibilities:**
- Window management
- IPC handler registration
- Docker API integration
- System monitoring
- File system operations

**IPC Handlers:**
```javascript
// Docker Control
backend:composeUp
backend:composeDown
backend:composeRestart
backend:composeRebuild
backend:status

// Logs
backend:startLogs
backend:stopLogs
backend:logLine (event)

// System
system:stats
gpu:verify

// Utilities
shell:open
fs:openPath
backend:migrate
```

**Dependencies:**
- `dockerode` - Docker API client
- `systeminformation` - System stats
- `child_process` - Process spawning

### 2. Preload Script (`preload.js`)

**Responsibilities:**
- Secure IPC bridge
- API exposure to renderer
- Context isolation

**Exposed API:**
```javascript
window.electronAPI = {
  // Docker
  composeUp()
  composeDown()
  composeRestart()
  composeRebuild()
  status()
  
  // Logs
  startLogs(service)
  stopLogs()
  onLogLine(callback)
  
  // System
  systemStats()
  gpuVerify()
  
  // Utilities
  openExternal(url)
  openPath(path)
  migrate()
}
```

### 3. React Renderer Process

**Architecture:**
```
App.jsx (Router)
    │
    ├─ Layout.jsx (Three-panel workspace)
    │   │
    │   ├─ Top Tabs (Workspace, AI, Research, Settings)
    │   │
    │   ├─ Main Panel (Left)
    │   │   └─ <Outlet /> (React Router)
    │   │       ├─ Dashboard
    │   │       ├─ Projects
    │   │       ├─ Agents
    │   │       ├─ Skills
    │   │       ├─ Memory
    │   │       ├─ Research
    │   │       ├─ Chat
    │   │       ├─ System
    │   │       └─ Settings
    │   │
    │   ├─ Right Panel Top (File Trees)
    │   │   ├─ FileTree (Documentation)
    │   │   ├─ FileTree (Code)
    │   │   ├─ FileTree (Graphics)
    │   │   ├─ FileTree (Marketing)
    │   │   └─ FileTree (Research)
    │   │
    │   └─ Right Panel Bottom (Insights)
    │       └─ InsightsPanel
    │           ├─ Quick Stats
    │           ├─ Insights List
    │           ├─ Quick Actions
    │           └─ Recent Activity
```

## Data Flow

### 1. Docker Control Flow

```
User clicks "Start Stack"
    │
    ▼
React Component (System.jsx)
    │
    ▼
useBackend hook
    │
    ▼
window.electronAPI.composeUp()
    │
    ▼
IPC: 'backend:composeUp'
    │
    ▼
Main Process Handler
    │
    ▼
spawn('docker', ['compose', 'up', '-d'])
    │
    ▼
Docker Engine
    │
    ▼
Containers start
    │
    ▼
Response { ok: true }
    │
    ▼
React updates UI
```

### 2. Log Streaming Flow

```
User clicks "Start Logs"
    │
    ▼
System.jsx
    │
    ▼
backend.startLogs('backend')
    │
    ▼
IPC: 'backend:startLogs'
    │
    ▼
Main Process spawns:
docker compose logs -f backend
    │
    ▼
stdout.on('data') ──► IPC: 'backend:logLine'
    │                         │
    ▼                         ▼
Logs stream          React receives event
    │                         │
    │                         ▼
    │                  useBackend.onLogLine()
    │                         │
    │                         ▼
    └──────────────────► UI updates with logs
```

### 3. API Communication Flow

```
User action (e.g., create project)
    │
    ▼
React Component
    │
    ▼
apiClient.projects.create(data)
    │
    ▼
axios POST http://localhost:8000/api/projects
    │
    ▼
Backend API (FastAPI)
    │
    ▼
Database (PostgreSQL)
    │
    ▼
Response
    │
    ▼
React updates state
    │
    ▼
UI re-renders
```

### 4. System Stats Flow

```
useSystemStats hook mounts
    │
    ▼
setInterval(5000)
    │
    ▼
window.electronAPI.systemStats()
    │
    ▼
IPC: 'system:stats'
    │
    ▼
Main Process
    │
    ▼
systeminformation.graphics()
systeminformation.mem()
systeminformation.cpu()
systeminformation.disk()
    │
    ▼
Response { gpu, mem, cpu, disk }
    │
    ▼
React state updates
    │
    ▼
UI displays stats
```

## File Structure

```
desktop/
├── main.js                    # Electron main process
├── preload.js                 # IPC bridge
├── package.json               # Electron config
├── electron-builder.yml       # Packaging
├── start-desktop.sh           # Quick start
│
└── react-ui/
    ├── src/
    │   ├── main.jsx           # React entry
    │   ├── App.jsx            # Router
    │   ├── styles.css         # All styles
    │   │
    │   ├── api/
    │   │   └── client.js      # Backend API
    │   │
    │   ├── components/
    │   │   ├── Layout.jsx     # Three-panel layout
    │   │   ├── FileTree.jsx   # File tree component
    │   │   └── InsightsPanel.jsx
    │   │
    │   ├── hooks/
    │   │   ├── useBackend.js  # Docker control
    │   │   └── useSystemStats.js
    │   │
    │   └── pages/
    │       ├── Dashboard.jsx
    │       ├── Projects.jsx
    │       ├── ProjectDetail.jsx
    │       ├── Agents.jsx
    │       ├── Skills.jsx
    │       ├── Memory.jsx
    │       ├── Research.jsx
    │       ├── Chat.jsx
    │       ├── System.jsx
    │       └── Settings.jsx
    │
    ├── index.html
    ├── vite.config.js
    └── package.json
```

## Security Model

### Context Isolation

```
┌─────────────────────────────────────────┐
│         Renderer Process (React)        │
│                                         │
│  ✗ No direct Node.js access             │
│  ✗ No require()                         │
│  ✗ No fs, child_process, etc.          │
│                                         │
│  ✓ window.electronAPI only              │
└─────────────────┬───────────────────────┘
                  │
                  │ contextBridge
                  │
┌─────────────────▼───────────────────────┐
│          Preload Script                 │
│                                         │
│  • Whitelisted APIs only                │
│  • No arbitrary code execution          │
│  • Validated parameters                 │
└─────────────────┬───────────────────────┘
                  │
                  │ IPC
                  │
┌─────────────────▼───────────────────────┐
│         Main Process (Node.js)          │
│                                         │
│  • Full Node.js access                  │
│  • Docker API                           │
│  • File system                          │
│  • System calls                         │
└─────────────────────────────────────────┘
```

### API Authentication

```
React Component
    │
    ▼
axios request
    │
    ▼
Request Interceptor
    │
    ├─ Get token from localStorage
    │
    └─ Add Authorization: Bearer <token>
    │
    ▼
Backend API
    │
    ├─ Validate JWT
    │
    └─ Return response
    │
    ▼
Response Interceptor
    │
    ├─ If 401: Clear token, redirect to login
    │
    └─ Return data
```

## Build Process

### Development

```
npm run dev
    │
    ├─ Start React dev server (Vite)
    │   └─ http://localhost:5173
    │
    └─ Start Electron
        └─ Load http://localhost:5173
```

### Production

```
npm run build
    │
    ├─ Build React app
    │   └─ vite build → react-ui/dist/
    │
    └─ Package Electron
        └─ electron-builder
            │
            ├─ Windows: .exe installer
            ├─ Linux: .AppImage, .deb
            └─ macOS: .dmg, .app
```

## Performance Optimizations

### React
- Component memoization
- useCallback for event handlers
- Lazy loading for routes
- Virtual scrolling (future)

### Electron
- Preload script for fast startup
- Background processes for heavy tasks
- Efficient IPC communication
- Resource cleanup on exit

### API
- Request caching
- Debounced search
- Pagination
- Lazy data loading

## Error Handling

### IPC Errors
```javascript
try {
  const result = await window.electronAPI.composeUp()
  if (!result.ok) {
    console.error(result.error)
    alert('Failed to start backend')
  }
} catch (error) {
  console.error('IPC error:', error)
}
```

### API Errors
```javascript
try {
  const res = await apiClient.projects.create(data)
  // Success
} catch (error) {
  if (error.response?.status === 401) {
    // Handled by interceptor
  } else {
    console.error('API error:', error)
    alert('Failed to create project')
  }
}
```

### Process Errors
```javascript
// In main.js
process.on('uncaughtException', (error) => {
  console.error('Uncaught exception:', error)
  // Log to file, show dialog, etc.
})
```

## State Management

### Local State (useState)
- Component-specific UI state
- Form inputs
- Modal visibility

### Custom Hooks
- `useBackend` - Docker state
- `useSystemStats` - System monitoring
- Shared logic across components

### localStorage
- Settings persistence
- Auth tokens
- User preferences

### React Router
- Navigation state
- URL parameters
- Route context

## Future Enhancements

### Planned Features
- [ ] File editing with Monaco Editor
- [ ] Real-time collaboration
- [ ] Plugin system
- [ ] Custom themes
- [ ] Keyboard shortcuts
- [ ] Command palette
- [ ] Auto-update system

### Performance
- [ ] Web Workers for heavy tasks
- [ ] IndexedDB for offline data
- [ ] Service Worker for caching
- [ ] Virtual scrolling for large lists

### Developer Experience
- [ ] Hot reload for main process
- [ ] Better error messages
- [ ] Debug panel
- [ ] Performance profiler

---

**Architecture designed for:**
- Scalability
- Maintainability
- Security
- Performance
- User experience

