# Desktop App - Quick Reference Card

## 🚀 Quick Start Commands

```bash
# Development
cd desktop
./start-desktop.sh

# Or manually:
cd desktop/react-ui && npm run dev &
cd desktop && npm run dev:electron

# Production Build
cd desktop && npm run build
```

## 📁 Key Files

| File | Purpose |
|------|---------|
| `main.js` | Electron main process, IPC handlers |
| `preload.js` | Secure IPC bridge |
| `react-ui/src/App.jsx` | React router & routes |
| `react-ui/src/components/Layout.jsx` | Three-panel layout |
| `react-ui/src/styles.css` | All styling (1395 lines) |
| `react-ui/src/api/client.js` | Backend API client |

## 🎨 Layout Structure

```
┌─────────────────────────────────────────────┐
│ [Workspace] [AI] [Research] [Settings]     │
├──────────────────────┬──────────────────────┤
│                      │ 📁 File Trees        │
│   Main View          │ ▼ Docs               │
│   (70% width)        │ ▼ Code               │
│                      │ ▶ Graphics           │
│   • Dashboard        │ ▶ Marketing          │
│   • Projects         │ ▼ Research           │
│   • Agents           ├──────────────────────┤
│   • Skills           │ 💡 Insights          │
│   • Memory           │ • Stats              │
│   • Research         │ • Notifications      │
│   • Chat             │ • Quick Actions      │
│   • System           │ • Activity           │
│   • Settings         │                      │
└──────────────────────┴──────────────────────┘
```

## 🔧 IPC API Reference

### Docker Control
```javascript
window.electronAPI.composeUp()
window.electronAPI.composeDown()
window.electronAPI.composeRestart()
window.electronAPI.composeRebuild()
window.electronAPI.status()
```

### Logs
```javascript
window.electronAPI.startLogs('backend')
window.electronAPI.stopLogs()
window.electronAPI.onLogLine((line) => console.log(line))
```

### System
```javascript
window.electronAPI.systemStats()
window.electronAPI.gpuVerify()
```

### Utilities
```javascript
window.electronAPI.openExternal(url)
window.electronAPI.openPath(path)
window.electronAPI.migrate()
```

## 🌐 API Client Reference

### Projects
```javascript
apiClient.projects.list()
apiClient.projects.get(id)
apiClient.projects.create(data)
apiClient.projects.update(id, data)
apiClient.projects.delete(id)
apiClient.projects.run(name)
```

### AI
```javascript
apiClient.ai.status()
apiClient.llm.chat({ messages, model })
apiClient.orchestrator.agents()
apiClient.skills.list()
apiClient.skills.execute(name, params)
```

### Memory
```javascript
apiClient.memory.search({ query, limit })
apiClient.memory.insert(data)
apiClient.memory.stats()
```

### Research
```javascript
apiClient.research.run({ url, query })
```

## 🎯 Component Hierarchy

```
App
└── Layout (Three-panel)
    ├── Top Tabs
    ├── Main Panel
    │   └── <Outlet> (React Router)
    │       ├── Dashboard
    │       ├── Projects
    │       ├── Agents
    │       ├── Skills
    │       ├── Memory
    │       ├── Research
    │       ├── Chat
    │       ├── System
    │       └── Settings
    ├── Top Right Panel
    │   └── FileTree × 5
    └── Bottom Right Panel
        └── InsightsPanel
```

## 🎨 CSS Classes Reference

### Layout
- `.workspace-layout` - Main container
- `.top-tabs` - Tab bar
- `.main-view` - Left panel
- `.right-sidebar` - Right panels container
- `.right-panel.top-panel` - File trees
- `.right-panel.bottom-panel` - Insights

### Components
- `.card` - Card container
- `.btn` - Button
- `.btn-primary` - Primary button
- `.form-group` - Form field
- `.list-item` - List item
- `.status-badge` - Status indicator
- `.progress-bar` - Progress bar

### Utilities
- `.grid-2` - 2-column grid
- `.grid-3` - 3-column grid
- `.grid-4` - 4-column grid
- `.spacer` - Flex spacer
- `.text-muted` - Muted text

## 🔐 Security Checklist

- [x] Context isolation enabled
- [x] No nodeIntegration
- [x] contextBridge for IPC
- [x] JWT token management
- [x] 401 auto-redirect
- [x] No secrets in code

## 📦 Build Outputs

| Platform | Output |
|----------|--------|
| Windows | `dist/Project Starter Pro 2 Setup.exe` |
| Linux | `dist/project-starter-pro-2.AppImage` |
| macOS | `dist/Project Starter Pro 2.dmg` |

## 🐛 Common Issues

### App won't start
```bash
rm -rf node_modules react-ui/node_modules
npm install
cd react-ui && npm install
```

### Backend not connecting
```bash
docker compose up -d
# Check: http://localhost:8000/api/health
```

### Logs not streaming
1. Click "Stop" in System tab
2. Click "Start" again

### GPU not detected
```bash
# Install NVIDIA Docker
# See: ../GPU_SETUP.md
```

## 📝 Development Workflow

### Adding a New Page
1. Create `react-ui/src/pages/NewPage.jsx`
2. Add route in `App.jsx`:
   ```jsx
   <Route path="/new" element={<NewPage />} />
   ```
3. Add tab in `Layout.jsx` (optional)

### Adding IPC Handler
1. Add handler in `main.js`:
   ```javascript
   ipcMain.handle('my:action', async () => {
     // Do something
     return { ok: true }
   })
   ```
2. Expose in `preload.js`:
   ```javascript
   myAction: () => ipcRenderer.invoke('my:action')
   ```
3. Use in React:
   ```javascript
   const result = await window.electronAPI.myAction()
   ```

### Styling
- All styles in `react-ui/src/styles.css`
- Use CSS variables for colors
- Follow existing patterns

## 🎯 Testing Checklist

- [ ] App launches
- [ ] All tabs work
- [ ] File trees expand/collapse
- [ ] Docker controls work
- [ ] Logs stream
- [ ] System stats update
- [ ] Projects CRUD works
- [ ] Chat works
- [ ] Settings persist

## 📚 Documentation

- `README.md` - User guide
- `ARCHITECTURE.md` - Technical details
- `DESKTOP_APP_COMPLETE.md` - Implementation summary
- `QUICK_REFERENCE.md` - This file

## 🔗 Useful Links

- Electron Docs: https://www.electronjs.org/docs
- React Router: https://reactrouter.com/
- Vite: https://vitejs.dev/
- Lucide Icons: https://lucide.dev/

## 💡 Tips

- Use DevTools (F12) for debugging
- Check Electron console for IPC errors
- Check browser console for React errors
- Use React DevTools extension
- Monitor Docker logs: `docker compose logs -f`

---

**Quick Help**: If stuck, check `desktop/README.md` for detailed instructions.

