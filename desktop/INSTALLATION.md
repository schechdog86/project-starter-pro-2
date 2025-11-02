# Desktop App Installation Guide

## Prerequisites

### Required
- **Node.js 20 LTS** or higher
  - Download: https://nodejs.org/
  - Verify: `node -v` (should show v20.x.x or higher)
- **npm** (comes with Node.js)
  - Verify: `npm -v`
- **Docker Desktop** (for backend)
  - Download: https://www.docker.com/products/docker-desktop
  - Verify: `docker --version`

### Optional (for GPU acceleration)
- **NVIDIA GPU** (RTX series recommended)
- **NVIDIA Docker Runtime**
  - See: `../GPU_SETUP.md`

---

## Installation Steps

### Step 1: Install Electron Dependencies

```bash
cd desktop
npm install
```

**Expected output:**
```
added 150 packages in 30s
```

**Dependencies installed:**
- electron (32.2.0)
- dockerode (4.0.2)
- systeminformation (5.25.11)
- electron-is-dev (3.0.1)
- concurrently (9.0.1)
- wait-on (8.0.2)
- electron-builder (25.1.8)

### Step 2: Install React UI Dependencies

```bash
cd react-ui
npm install
```

**Expected output:**
```
added 200 packages in 45s
```

**Dependencies installed:**
- react (18.3.1)
- react-dom (18.3.1)
- react-router-dom (6.28.0)
- axios (1.7.7)
- vite (5.4.10)
- lucide-react (0.294.0)
- recharts (2.12.7)

### Step 3: Start Backend (Optional but Recommended)

```bash
cd ../..  # Back to project root
docker compose up -d
```

**Expected output:**
```
[+] Running 4/4
 ✔ Container backend    Started
 ✔ Container postgres   Started
 ✔ Container redis      Started
 ✔ Container celery     Started
```

**Verify backend:**
```bash
curl http://localhost:8000/api/health
# Should return: {"status":"healthy"}
```

### Step 4: Launch Desktop App

**Option A: Quick Start Script (Recommended)**
```bash
cd desktop
./start-desktop.sh
```

**Option B: Manual Start**
```bash
# Terminal 1: React dev server
cd desktop/react-ui
npm run dev

# Terminal 2: Electron
cd desktop
npm run dev:electron
```

**Expected result:**
- React dev server starts on http://localhost:5173
- Electron window opens
- DevTools open automatically
- App loads with dashboard

---

## Verification

### 1. Check App Launch
- [ ] Electron window opens
- [ ] No errors in DevTools console
- [ ] Dashboard loads with cards

### 2. Check Backend Connection
- [ ] Backend status shows "Online" (green dot)
- [ ] Health check passes
- [ ] No connection errors

### 3. Check Navigation
- [ ] All 4 tabs clickable (Workspace, AI, Research, Settings)
- [ ] Tab content changes when clicked
- [ ] No console errors

### 4. Check File Trees
- [ ] 5 file trees visible (Docs, Code, Graphics, Marketing, Research)
- [ ] Trees expand/collapse when clicked
- [ ] File icons display correctly

### 5. Check Insights Panel
- [ ] Quick stats display
- [ ] Insights list shows items
- [ ] Quick actions buttons visible

### 6. Check Docker Control (if backend running)
- [ ] Navigate to System tab
- [ ] Container status shows "running"
- [ ] Start/Stop buttons work
- [ ] Logs stream when "Start Logs" clicked

### 7. Check System Stats
- [ ] GPU stats display (if GPU available)
- [ ] CPU load shows percentage
- [ ] Memory usage shows
- [ ] Disk space shows

---

## Troubleshooting

### Issue: `npm install` fails

**Solution 1: Clear cache**
```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**Solution 2: Use different registry**
```bash
npm install --registry=https://registry.npmjs.org/
```

### Issue: Electron won't start

**Error:** `Cannot find module 'electron'`

**Solution:**
```bash
cd desktop
rm -rf node_modules
npm install
```

### Issue: React dev server won't start

**Error:** `Port 5173 already in use`

**Solution:**
```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9

# Or change port in react-ui/vite.config.js
```

### Issue: Backend not connecting

**Error:** `Network Error` or `ERR_CONNECTION_REFUSED`

**Solution 1: Start backend**
```bash
cd ../..  # Project root
docker compose up -d
```

**Solution 2: Check backend URL**
- Open Settings tab
- Verify API URL is `http://localhost:8000`
- Click "Save Settings"

**Solution 3: Check Docker**
```bash
docker ps
# Should show backend, postgres, redis, celery containers
```

### Issue: Logs not streaming

**Error:** Logs panel empty or stuck

**Solution:**
1. Click "Stop Logs" button
2. Wait 2 seconds
3. Click "Start Logs" button
4. Check Docker container is running: `docker ps`

### Issue: GPU not detected

**Error:** GPU stats show "No GPU detected"

**Solution:**
1. Install NVIDIA Docker (see `../GPU_SETUP.md`)
2. Restart Docker Desktop
3. Restart desktop app
4. Click "Verify GPU" in System tab

### Issue: White screen on launch

**Error:** Blank white window

**Solution 1: Check React dev server**
```bash
# Make sure React is running
cd desktop/react-ui
npm run dev
```

**Solution 2: Clear Electron cache**
```bash
rm -rf ~/Library/Application\ Support/project-starter-pro-2-desktop  # macOS
rm -rf ~/.config/project-starter-pro-2-desktop  # Linux
rm -rf %APPDATA%\project-starter-pro-2-desktop  # Windows
```

**Solution 3: Check DevTools console**
- Press F12 in Electron window
- Look for errors in Console tab
- Fix any import or syntax errors

### Issue: Hot reload not working

**Error:** Changes not reflected in app

**Solution:**
- React changes: Should auto-reload (Vite HMR)
- Electron main.js changes: Restart Electron (Ctrl+C, then `npm run dev:electron`)
- Preload.js changes: Restart Electron

---

## Development Tips

### Enable Verbose Logging

**In main.js:**
```javascript
// Add at top
process.env.ELECTRON_ENABLE_LOGGING = true
```

**In React:**
```javascript
// Add in App.jsx
console.log('App mounted')
```

### Debug IPC Communication

**In preload.js:**
```javascript
contextBridge.exposeInMainWorld('electronAPI', {
  composeUp: () => {
    console.log('IPC: composeUp called')
    return ipcRenderer.invoke('backend:composeUp')
  }
})
```

**In main.js:**
```javascript
ipcMain.handle('backend:composeUp', async () => {
  console.log('IPC: backend:composeUp received')
  // ...
})
```

### Monitor Performance

**React DevTools:**
1. Install React DevTools extension
2. Open DevTools (F12)
3. Go to "Components" or "Profiler" tab

**Electron DevTools:**
- Already open in development mode
- Use "Performance" tab for profiling

---

## Production Build

### Build for Current Platform

```bash
cd desktop
npm run build
```

**Output locations:**
- **Windows**: `dist/Project Starter Pro 2 Setup.exe`
- **Linux**: `dist/project-starter-pro-2.AppImage`
- **macOS**: `dist/Project Starter Pro 2.dmg`

### Build for Specific Platform

```bash
# Windows
npm run build -- --win

# macOS
npm run build -- --mac

# Linux
npm run build -- --linux
```

### Build Options

**Directory only (no installer):**
```bash
npm run pack
# Output: dist/win-unpacked/ or dist/linux-unpacked/
```

**All platforms:**
```bash
npm run build -- --win --mac --linux
```

---

## Environment Variables

### Development

Create `desktop/.env`:
```bash
VITE_API_BASE=http://localhost:8000
ELECTRON_DEV=true
```

### Production

Set in `electron-builder.yml`:
```yaml
extraMetadata:
  env:
    VITE_API_BASE: "http://localhost:8000"
```

---

## Uninstallation

### Remove Desktop App

**Windows:**
- Control Panel → Programs → Uninstall

**macOS:**
- Drag app to Trash

**Linux:**
```bash
rm -rf /opt/project-starter-pro-2
rm ~/.local/share/applications/project-starter-pro-2.desktop
```

### Remove Development Files

```bash
cd desktop
rm -rf node_modules react-ui/node_modules
rm -rf dist
```

---

## Next Steps

After successful installation:

1. **Read the docs:**
   - `README.md` - User guide
   - `ARCHITECTURE.md` - Technical details
   - `QUICK_REFERENCE.md` - Quick reference

2. **Test features:**
   - Create a project
   - Chat with AI
   - Run research scraping
   - Monitor system stats

3. **Customize:**
   - Change theme colors in `styles.css`
   - Add new pages
   - Extend IPC handlers

4. **Deploy:**
   - Build production version
   - Distribute to users
   - Set up auto-update

---

## Support

For issues:
1. Check this guide
2. Check `README.md`
3. Check DevTools console
4. Check Docker logs: `docker compose logs -f`

---

**Installation complete! 🎉**

Run `./start-desktop.sh` to launch the app.

