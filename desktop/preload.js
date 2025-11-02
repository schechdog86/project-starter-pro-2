const { contextBridge, ipcRenderer } = require('electron');

/**
 * Secure IPC Bridge for Project Starter Pro 2
 * 
 * Exposes safe API to renderer process with context isolation.
 * All backend communication goes through these channels.
 */

contextBridge.exposeInMainWorld('electronAPI', {
  // ============================================================
  // Docker Compose Control
  // ============================================================
  
  composeUp: () => ipcRenderer.invoke('backend:composeUp'),
  composeDown: () => ipcRenderer.invoke('backend:composeDown'),
  composeRestart: () => ipcRenderer.invoke('backend:composeRestart'),
  composeRebuild: () => ipcRenderer.invoke('backend:composeRebuild'),
  status: () => ipcRenderer.invoke('backend:status'),
  
  // ============================================================
  // Logs Streaming
  // ============================================================
  
  startLogs: (service) => ipcRenderer.invoke('backend:startLogs', service),
  stopLogs: () => ipcRenderer.invoke('backend:stopLogs'),
  onLogLine: (callback) => {
    const subscription = (_, line) => callback(line);
    ipcRenderer.on('backend:logLine', subscription);
    return () => ipcRenderer.removeListener('backend:logLine', subscription);
  },
  
  // ============================================================
  // System Monitoring
  // ============================================================
  
  systemStats: () => ipcRenderer.invoke('system:stats'),
  gpuVerify: () => ipcRenderer.invoke('gpu:verify'),
  
  // ============================================================
  // External Links & File System
  // ============================================================
  
  openExternal: (url) => ipcRenderer.invoke('shell:open', url),
  openPath: (path) => ipcRenderer.invoke('fs:openPath', path),
  
  // ============================================================
  // Database Operations
  // ============================================================
  
  migrate: () => ipcRenderer.invoke('backend:migrate'),
});

console.log('Preload script loaded - electronAPI exposed');

