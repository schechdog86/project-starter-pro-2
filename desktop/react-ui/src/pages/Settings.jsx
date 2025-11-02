import { useState, useEffect } from 'react'
import { Settings as SettingsIcon, Save } from 'lucide-react'

export default function Settings() {
  const [settings, setSettings] = useState({
    apiUrl: localStorage.getItem('api_url') || 'http://localhost:8000',
    theme: localStorage.getItem('theme') || 'dark',
    autoStart: localStorage.getItem('auto_start') === 'true',
    notifications: localStorage.getItem('notifications') !== 'false',
  })

  const updateSetting = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }))
  }

  const handleSave = () => {
    localStorage.setItem('api_url', settings.apiUrl)
    localStorage.setItem('theme', settings.theme)
    localStorage.setItem('auto_start', settings.autoStart)
    localStorage.setItem('notifications', settings.notifications)
    alert('Settings saved!')
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Settings</h1>
          <p className="text-muted">Configure application preferences</p>
        </div>
        <button className="btn btn-primary" onClick={handleSave}>
          <Save size={20} />
          Save Settings
        </button>
      </div>

      <div className="card">
        <div className="card-header">
          <SettingsIcon size={20} />
          <h3>General</h3>
        </div>
        <div className="card-body">
          <div className="form-group">
            <label>API Base URL</label>
            <input
              type="url"
              value={settings.apiUrl}
              onChange={e => updateSetting('apiUrl', e.target.value)}
              placeholder="http://localhost:8000"
            />
            <small className="text-muted">Backend API endpoint</small>
          </div>

          <div className="form-group">
            <label>Theme</label>
            <select 
              value={settings.theme}
              onChange={e => updateSetting('theme', e.target.value)}
            >
              <option value="dark">Dark</option>
              <option value="light">Light</option>
            </select>
          </div>

          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={settings.autoStart}
                onChange={e => updateSetting('autoStart', e.target.checked)}
              />
              <span>Auto-start backend on launch</span>
            </label>
          </div>

          <div className="form-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={settings.notifications}
                onChange={e => updateSetting('notifications', e.target.checked)}
              />
              <span>Enable notifications</span>
            </label>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h3>About</h3>
        </div>
        <div className="card-body">
          <div className="info-grid">
            <div className="info-item">
              <span className="info-label">Version</span>
              <span className="info-value">1.0.0</span>
            </div>
            <div className="info-item">
              <span className="info-label">Electron</span>
              <span className="info-value">{process.versions.electron || 'N/A'}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Node</span>
              <span className="info-value">{process.versions.node || 'N/A'}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Chrome</span>
              <span className="info-value">{process.versions.chrome || 'N/A'}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

