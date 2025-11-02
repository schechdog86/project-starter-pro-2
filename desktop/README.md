# Project Starter Pro 2 - Desktop App

Production-ready Electron desktop application with embedded React GUI for managing AI-powered projects.

## 🎯 Features

### Three-Panel Workspace Layout
- **Left Panel (Main View)**: Full-size content area for viewing files, dashboards, notes, and code
- **Top Right Panel**: Organized file trees for all project files (Docs, Code, Graphics, Marketing, Research)
- **Bottom Right Panel**: Real-time insights, information, and quick actions

### Tab-Based Navigation
- **Workspace**: Project management, file viewing, note-taking
- **AI Agents**: Manage and interact with AI agents
- **Research**: Web scraping and data analysis
- **Settings**: Application configuration

### Backend Control
- Start/stop/restart Docker containers
- Real-time logs streaming
- GPU/CPU/RAM monitoring
- Database migrations
- Health checks

### AI Integration
- Chat with AI agents
- Execute skills
- Memory system (ST, MT, LT_HOT, FV)
- Research scraping (ScrapeGraphAI, Firecrawl)
- 100+ AI frameworks

### Project Management
- Create projects with wizard
- View project details
- Run project workflows
- File organization

## 📁 Structure

```
desktop/
├── main.js                 # Electron main process
├── preload.js             # Secure IPC bridge
├── package.json           # Electron config
├── electron-builder.yml   # Packaging config
└── react-ui/
    ├── src/
    │   ├── main.jsx       # React entry
    │   ├── App.jsx        # Main app component
    │   ├── styles.css     # Complete styling
    │   ├── api/
    │   │   └── client.js  # Backend API client
    │   ├── components/
    │   │   ├── Layout.jsx        # Three-panel layout
    │   │   ├── FileTree.jsx      # File tree component
    │   │   └── InsightsPanel.jsx # Insights component
    │   ├── hooks/
    │   │   ├── useBackend.js     # Docker control
    │   │   └── useSystemStats.js # System monitoring
    │   └── pages/
    │       ├── Dashboard.jsx     # Main dashboard
    │       ├── Projects.jsx      # Project list + wizard
    │       ├── ProjectDetail.jsx # Project details
    │       ├── Agents.jsx        # AI agents
    │       ├── Skills.jsx        # Skills management
    │       ├── Memory.jsx        # Memory system
    │       ├── Research.jsx      # Research tools
    │       ├── Chat.jsx          # AI chat
    │       ├── System.jsx        # System control
    │       └── Settings.jsx      # App settings
    ├── index.html
    ├── vite.config.js
    └── package.json
```

## 🚀 Quick Start

### Prerequisites
- Node.js 20 LTS
- Docker & Docker Compose
- NVIDIA Docker (optional, for GPU)

### Installation

1. **Install Electron dependencies:**
```bash
cd desktop
npm install
```

2. **Install React UI dependencies:**
```bash
cd react-ui
npm install
```

### Development

1. **Start React dev server:**
```bash
cd desktop/react-ui
npm run dev
```

2. **In another terminal, start Electron:**
```bash
cd desktop
npm run dev
```

The app will launch with:
- React dev server on `http://localhost:5173`
- Electron window with hot reload
- DevTools open for debugging

### Production Build

```bash
cd desktop
npm run build
```

This will:
1. Build React app to `react-ui/dist/`
2. Package Electron app with electron-builder
3. Create installers in `desktop/dist/`

**Output:**
- Windows: `.exe` installer
- Linux: `.AppImage`, `.deb`
- macOS: `.dmg`, `.app`

## 🎨 UI Layout

### Top Tab Bar
```
┌─────────────────────────────────────────────────────────┐
│ 🚀 Project Starter Pro 2  [Workspace] [AI] [Research]  │
│                           [Settings]    ● Backend Online│
└─────────────────────────────────────────────────────────┘
```

### Main Workspace
```
┌──────────────────────────┬──────────────────┐
│                          │ 📁 Project Files │
│                          ├──────────────────┤
│                          │ ▼ Documentation  │
│   Main Content Area      │   01_scope.md    │
│   (Full Size)            │   02_research.md │
│                          │ ▼ Code           │
│   - View files           │   backend/       │
│   - Write notes          │   frontend/      │
│   - Code editor          │ ▶ Graphics       │
│   - Dashboards           │ ▶ Marketing      │
│                          │ ▼ Research       │
│                          ├──────────────────┤
│                          │ 💡 Insights      │
│                          ├──────────────────┤
│                          │ ✓ Backend Healthy│
│                          │ 📊 5 Projects    │
│                          │ ⚡ Quick Actions │
│                          │ 📝 Recent Activity│
└──────────────────────────┴──────────────────┘
```

## 🔧 Configuration

### API Endpoint
Default: `http://localhost:8000`

Change in Settings tab or set environment variable:
```bash
VITE_API_BASE=http://localhost:8000
```

### Docker Compose Path
- **Development**: `../docker-compose.yml`
- **Production**: Bundled in `resources/docker-compose.yml`

### Auto-start Backend
Enable in Settings to automatically start Docker containers on app launch.

## 🧪 Testing

### Manual Testing Checklist
- [ ] App launches successfully
- [ ] All tabs switch correctly
- [ ] File trees expand/collapse
- [ ] Insights panel updates
- [ ] Docker controls work (start/stop/restart)
- [ ] Logs stream in real-time
- [ ] System stats update
- [ ] Projects CRUD operations
- [ ] AI chat works
- [ ] Research scraping works
- [ ] Settings persist

### Test Commands
```bash
# Start backend first
cd ..
docker compose up -d

# Then test desktop app
cd desktop
npm run dev
```

## 📦 Dependencies

### Electron
- `electron` ^32.2.0 - Desktop framework
- `electron-is-dev` ^3.0.1 - Dev detection
- `electron-builder` ^25.1.8 - Packaging

### Backend Integration
- `dockerode` ^4.0.2 - Docker API
- `systeminformation` ^5.25.11 - System stats

### React UI
- `react` ^18.3.1
- `react-dom` ^18.3.1
- `react-router-dom` ^6.28.0
- `axios` ^1.7.7
- `recharts` ^2.12.7
- `lucide-react` ^0.294.0
- `vite` ^5.4.10

## 🔐 Security

### IPC Communication
- Context isolation enabled
- `contextBridge` for secure API exposure
- No `nodeIntegration` in renderer

### API Authentication
- JWT tokens stored in `localStorage`
- Automatic token refresh
- 401 handling with redirect

### Docker Socket
- Read-only access where possible
- No privileged operations without confirmation

## 🐛 Troubleshooting

### App won't start
```bash
# Clear node_modules and reinstall
rm -rf node_modules react-ui/node_modules
npm install
cd react-ui && npm install
```

### Backend not connecting
1. Check Docker is running: `docker ps`
2. Start backend: `docker compose up -d`
3. Check API URL in Settings

### Logs not streaming
1. Stop existing logs: Click "Stop" in System tab
2. Restart logs: Click "Start"
3. Check Docker container is running

### GPU not detected
1. Install NVIDIA Docker: See `../GPU_SETUP.md`
2. Verify GPU: `docker compose exec backend python -c "import torch; print(torch.cuda.is_available())"`

## 📝 Development Notes

### Hot Reload
- React: Vite HMR (instant)
- Electron: Manual restart required for `main.js` changes
- Preload: Requires Electron restart

### Adding New Pages
1. Create page in `react-ui/src/pages/`
2. Add route in `App.jsx`
3. Add tab in `Layout.jsx` (if needed)

### Adding New IPC Handlers
1. Add handler in `main.js`
2. Expose in `preload.js`
3. Use in React via `window.electronAPI`

### Styling
- All styles in `react-ui/src/styles.css`
- Dark theme by default
- CSS variables for theming

## 🚢 Deployment

### Windows
```bash
npm run build
# Output: dist/Project Starter Pro 2 Setup.exe
```

### Linux
```bash
npm run build
# Output: dist/project-starter-pro-2.AppImage
```

### macOS
```bash
npm run build
# Output: dist/Project Starter Pro 2.dmg
```

### Auto-Update
Wire `electron-updater` for automatic updates:
```javascript
// In main.js
const { autoUpdater } = require('electron-updater');
autoUpdater.checkForUpdatesAndNotify();
```

## 📄 License

Part of Project Starter Pro 2 - See root LICENSE

## 🤝 Contributing

1. Follow workspace rules in `.augment/rules/rules.md`
2. Test all changes manually
3. Update this README for new features
4. Keep dependencies up to date

---

**Built with ❤️ using Electron + React + Vite**

