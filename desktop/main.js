const { app, BrowserWindow, ipcMain, shell } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');
const { spawn } = require('child_process');
const Docker = require('dockerode');
const si = require('systeminformation');

const docker = new Docker({ socketPath: '/var/run/docker.sock' });
let mainWindow;
let logsProc = null;

// ============================================================
// Window Management
// ============================================================

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1800,
    height: 1200,
    minWidth: 1200,
    minHeight: 800,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    },
    backgroundColor: '#0b0f14',
    titleBarStyle: 'default',
    show: false, // Show after ready-to-show
  });

  // Load React app
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools({ mode: 'detach' });
  } else {
    const indexFile = path.join(__dirname, 'react-ui', 'dist', 'index.html');
    mainWindow.loadFile(indexFile);
  }

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Handle window close
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  createWindow();
  
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (logsProc) {
    logsProc.kill('SIGINT');
  }
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// ============================================================
// Helper Functions
// ============================================================

function run(cmd, args, opts = {}) {
  return new Promise((resolve, reject) => {
    const p = spawn(cmd, args, { stdio: 'pipe', shell: false, ...opts });
    let out = '', err = '';
    p.stdout.on('data', d => out += d.toString());
    p.stderr.on('data', d => err += d.toString());
    p.on('close', code => {
      if (code === 0) resolve({ out, err });
      else reject(new Error(err || `exit ${code}`));
    });
  });
}

function getComposePath() {
  if (isDev) {
    return path.join(__dirname, '..', 'docker-compose.yml');
  }
  return path.join(process.resourcesPath, 'docker-compose.yml');
}

// ============================================================
// IPC: Docker Compose Control
// ============================================================

ipcMain.handle('backend:composeUp', async () => {
  const composePath = getComposePath();
  try {
    await run('docker', ['compose', '-f', composePath, 'up', '-d']);
    return { ok: true };
  } catch (e) {
    return { ok: false, error: String(e.message || e) };
  }
});

ipcMain.handle('backend:composeDown', async () => {
  const composePath = getComposePath();
  try {
    await run('docker', ['compose', '-f', composePath, 'down']);
    return { ok: true };
  } catch (e) {
    return { ok: false, error: String(e.message || e) };
  }
});

ipcMain.handle('backend:composeRestart', async () => {
  const composePath = getComposePath();
  try {
    await run('docker', ['compose', '-f', composePath, 'restart']);
    return { ok: true };
  } catch (e) {
    return { ok: false, error: String(e.message || e) };
  }
});

ipcMain.handle('backend:composeRebuild', async () => {
  const composePath = getComposePath();
  try {
    await run('docker', ['compose', '-f', composePath, 'up', '--build', '-d']);
    return { ok: true };
  } catch (e) {
    return { ok: false, error: String(e.message || e) };
  }
});

ipcMain.handle('backend:status', async () => {
  try {
    const containers = await docker.listContainers({ all: true });
    const interesting = containers.filter(c => 
      (c.Names || []).some(n => /psp|backend|celery|db|redis|postgres/.test(n))
    );
    return { ok: true, containers: interesting };
  } catch (e) {
    return { ok: false, error: String(e.message || e) };
  }
});

// ============================================================
// IPC: Logs Streaming
// ============================================================

ipcMain.handle('backend:startLogs', async (evt, service = 'backend') => {
  const composePath = getComposePath();
  try {
    if (logsProc) {
      logsProc.kill('SIGINT');
      logsProc = null;
    }
    
    logsProc = spawn('docker', ['compose', '-f', composePath, 'logs', '-f', '--tail=100', service]);
    
    logsProc.stdout.on('data', (d) => {
      mainWindow?.webContents.send('backend:logLine', d.toString());
    });
    
    logsProc.stderr.on('data', (d) => {
      mainWindow?.webContents.send('backend:logLine', d.toString());
    });
    
    logsProc.on('close', () => {
      mainWindow?.webContents.send('backend:logLine', '\n[logs] stream ended\n');
      logsProc = null;
    });
    
    return { ok: true };
  } catch (e) {
    return { ok: false, error: String(e.message || e) };
  }
});

ipcMain.handle('backend:stopLogs', async () => {
  if (logsProc) {
    logsProc.kill('SIGINT');
    logsProc = null;
  }
  return { ok: true };
});

// ============================================================
// IPC: System Stats (GPU, CPU, RAM)
// ============================================================

ipcMain.handle('system:stats', async () => {
  try {
    const [gpu, mem, cpu, disk] = await Promise.all([
      si.graphics(),
      si.mem(),
      si.currentLoad(),
      si.fsSize(),
    ]);
    return { ok: true, gpu, mem, cpu, disk };
  } catch (e) {
    return { ok: false, error: String(e.message || e) };
  }
});

// ============================================================
// IPC: External Links
// ============================================================

ipcMain.handle('shell:open', async (evt, url) => {
  try {
    await shell.openExternal(url);
    return { ok: true };
  } catch (e) {
    return { ok: false, error: String(e.message || e) };
  }
});

// ============================================================
// IPC: File System Operations
// ============================================================

ipcMain.handle('fs:openPath', async (evt, filePath) => {
  try {
    await shell.openPath(filePath);
    return { ok: true };
  } catch (e) {
    return { ok: false, error: String(e.message || e) };
  }
});

// ============================================================
// IPC: Database Migrations
// ============================================================

ipcMain.handle('backend:migrate', async () => {
  const composePath = getComposePath();
  try {
    await run('docker', ['compose', '-f', composePath, 'exec', 'backend', 'alembic', 'upgrade', 'head']);
    return { ok: true };
  } catch (e) {
    return { ok: false, error: String(e.message || e) };
  }
});

// ============================================================
// IPC: GPU Verification
// ============================================================

ipcMain.handle('gpu:verify', async () => {
  const composePath = getComposePath();
  try {
    const result = await run('docker', [
      'compose', '-f', composePath, 'exec', 'backend',
      'python', '-c', 'import torch; print(torch.cuda.is_available())'
    ]);
    const available = result.out.trim() === 'True';
    return { ok: true, available };
  } catch (e) {
    return { ok: false, error: String(e.message || e), available: false };
  }
});

console.log('Electron main process initialized');

