import { useState } from 'react'
import useBackend from '../hooks/useBackend'
import useSystemStats from '../hooks/useSystemStats'
import { Server, Play, Square, RotateCw, Hammer, Terminal, Cpu } from 'lucide-react'

export default function System() {
  const backend = useBackend()
  const { stats } = useSystemStats()
  const [activeTab, setActiveTab] = useState('containers')

  const runningContainers = backend.status.containers?.filter(c => c.State === 'running') || []
  const stoppedContainers = backend.status.containers?.filter(c => c.State !== 'running') || []

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>System Control</h1>
          <p className="text-muted">Manage Docker backend and system resources</p>
        </div>
      </div>

      {/* Control Panel */}
      <div className="card">
        <div className="card-header">
          <Server size={20} />
          <h3>Docker Controls</h3>
        </div>
        <div className="card-body">
          <div className="control-buttons">
            <button 
              className="btn btn-success"
              onClick={backend.composeUp}
              disabled={backend.loading}
            >
              <Play size={20} />
              Start Stack
            </button>
            <button 
              className="btn btn-warning"
              onClick={backend.composeRestart}
              disabled={backend.loading}
            >
              <RotateCw size={20} />
              Restart
            </button>
            <button 
              className="btn btn-primary"
              onClick={backend.composeRebuild}
              disabled={backend.loading}
            >
              <Hammer size={20} />
              Rebuild
            </button>
            <button 
              className="btn btn-danger"
              onClick={backend.composeDown}
              disabled={backend.loading}
            >
              <Square size={20} />
              Stop Stack
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'containers' ? 'active' : ''}`}
          onClick={() => setActiveTab('containers')}
        >
          Containers
        </button>
        <button 
          className={`tab ${activeTab === 'logs' ? 'active' : ''}`}
          onClick={() => setActiveTab('logs')}
        >
          Logs
        </button>
        <button 
          className={`tab ${activeTab === 'stats' ? 'active' : ''}`}
          onClick={() => setActiveTab('stats')}
        >
          System Stats
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'containers' && (
        <div className="card">
          <div className="card-header">
            <h3>Containers</h3>
            <button className="btn btn-sm" onClick={backend.refresh}>
              Refresh
            </button>
          </div>
          <div className="card-body">
            {runningContainers.length > 0 && (
              <>
                <h4>Running ({runningContainers.length})</h4>
                <div className="container-list">
                  {runningContainers.map(c => (
                    <div key={c.Id} className="container-item running">
                      <div className="container-name">{c.Names?.[0]?.replace(/^\//, '')}</div>
                      <div className="container-status">{c.Status}</div>
                    </div>
                  ))}
                </div>
              </>
            )}

            {stoppedContainers.length > 0 && (
              <>
                <h4>Stopped ({stoppedContainers.length})</h4>
                <div className="container-list">
                  {stoppedContainers.map(c => (
                    <div key={c.Id} className="container-item stopped">
                      <div className="container-name">{c.Names?.[0]?.replace(/^\//, '')}</div>
                      <div className="container-status">{c.Status}</div>
                    </div>
                  ))}
                </div>
              </>
            )}

            {backend.status.containers?.length === 0 && (
              <div className="empty-state">
                <p>No containers found</p>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'logs' && (
        <div className="card">
          <div className="card-header">
            <Terminal size={20} />
            <h3>Backend Logs</h3>
            <div className="spacer" />
            <button 
              className="btn btn-sm"
              onClick={() => backend.startLogs('backend')}
            >
              Start
            </button>
            <button 
              className="btn btn-sm"
              onClick={backend.stopLogs}
            >
              Stop
            </button>
          </div>
          <div className="card-body">
            <pre className="logs-output">{backend.logs || 'No logs yet. Click Start to stream logs.'}</pre>
          </div>
        </div>
      )}

      {activeTab === 'stats' && (
        <div className="grid grid-2">
          {/* GPU */}
          <div className="card">
            <div className="card-header">
              <Cpu size={20} />
              <h3>GPU</h3>
            </div>
            <div className="card-body">
              {stats?.gpu?.controllers?.[0] ? (
                <>
                  <div className="stat-item">
                    <span className="stat-label">Model</span>
                    <span className="stat-value">{stats.gpu.controllers[0].model}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">VRAM</span>
                    <span className="stat-value">
                      {stats.gpu.controllers[0].vramUsed || 0} MB / {stats.gpu.controllers[0].vramTotal || 0} MB
                    </span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Temperature</span>
                    <span className="stat-value">{stats.gpu.controllers[0].temperatureGpu || 'N/A'}°C</span>
                  </div>
                </>
              ) : (
                <p className="text-muted">No GPU detected</p>
              )}
            </div>
          </div>

          {/* CPU */}
          <div className="card">
            <div className="card-header">
              <Cpu size={20} />
              <h3>CPU</h3>
            </div>
            <div className="card-body">
              <div className="stat-item">
                <span className="stat-label">Load</span>
                <span className="stat-value">{(stats?.cpu?.currentload || 0).toFixed(1)}%</span>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${stats?.cpu?.currentload || 0}%` }}
                />
              </div>
            </div>
          </div>

          {/* Memory */}
          <div className="card">
            <div className="card-header">
              <h3>Memory</h3>
            </div>
            <div className="card-body">
              <div className="stat-item">
                <span className="stat-label">Used</span>
                <span className="stat-value">
                  {((stats?.mem?.active || 0) / 1e9).toFixed(1)} / {((stats?.mem?.total || 0) / 1e9).toFixed(1)} GB
                </span>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ 
                    width: `${((stats?.mem?.active || 0) / (stats?.mem?.total || 1)) * 100}%` 
                  }}
                />
              </div>
            </div>
          </div>

          {/* Disk */}
          <div className="card">
            <div className="card-header">
              <h3>Disk</h3>
            </div>
            <div className="card-body">
              <div className="stat-item">
                <span className="stat-label">Used</span>
                <span className="stat-value">
                  {((stats?.disk?.[0]?.used || 0) / 1e9).toFixed(0)} / {((stats?.disk?.[0]?.size || 0) / 1e9).toFixed(0)} GB
                </span>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ 
                    width: `${((stats?.disk?.[0]?.used || 0) / (stats?.disk?.[0]?.size || 1)) * 100}%` 
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

