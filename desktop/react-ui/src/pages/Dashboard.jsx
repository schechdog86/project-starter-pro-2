import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiClient } from '../api/client'
import useBackend from '../hooks/useBackend'
import useSystemStats from '../hooks/useSystemStats'
import { Activity, Database, Cpu, HardDrive, Zap, CheckCircle, XCircle } from 'lucide-react'

export default function Dashboard() {
  const { status, loading: backendLoading } = useBackend()
  const { stats } = useSystemStats()
  const [health, setHealth] = useState(null)
  const [aiStatus, setAiStatus] = useState(null)
  const [projects, setProjects] = useState([])

  useEffect(() => {
    // Load health
    apiClient.health()
      .then(res => setHealth(res.data))
      .catch(() => setHealth({ status: 'error' }))

    // Load AI status
    apiClient.ai.status()
      .then(res => setAiStatus(res.data))
      .catch(() => setAiStatus(null))

    // Load recent projects
    apiClient.projects.list({ limit: 5 })
      .then(res => setProjects(res.data))
      .catch(() => setProjects([]))
  }, [])

  const runningContainers = status.containers?.filter(c => c.State === 'running').length || 0
  const totalContainers = status.containers?.length || 0

  return (
    <div className="page">
      <div className="page-header">
        <h1>Dashboard</h1>
        <p className="text-muted">Welcome to Project Starter Pro 2</p>
      </div>

      {/* Status Cards */}
      <div className="grid grid-4">
        {/* Backend Health */}
        <div className="card">
          <div className="card-header">
            <Activity size={20} />
            <h3>Backend</h3>
          </div>
          <div className="card-body">
            <div className="stat-value">
              {health?.status === 'healthy' ? (
                <span className="status-badge success">
                  <CheckCircle size={16} /> Healthy
                </span>
              ) : (
                <span className="status-badge error">
                  <XCircle size={16} /> Offline
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Docker Containers */}
        <div className="card">
          <div className="card-header">
            <Database size={20} />
            <h3>Containers</h3>
          </div>
          <div className="card-body">
            <div className="stat-value">{runningContainers} / {totalContainers}</div>
            <div className="stat-label">Running</div>
          </div>
        </div>

        {/* AI Frameworks */}
        <div className="card">
          <div className="card-header">
            <Zap size={20} />
            <h3>AI Frameworks</h3>
          </div>
          <div className="card-body">
            <div className="stat-value">{aiStatus?.total_frameworks || 0}</div>
            <div className="stat-label">Loaded</div>
          </div>
        </div>

        {/* GPU Status */}
        <div className="card">
          <div className="card-header">
            <Cpu size={20} />
            <h3>GPU</h3>
          </div>
          <div className="card-body">
            <div className="stat-value">
              {stats?.gpu?.controllers?.[0]?.model || 'N/A'}
            </div>
            <div className="stat-label">
              {stats?.gpu?.controllers?.[0]?.vramUsed || 0} MB / {stats?.gpu?.controllers?.[0]?.vramTotal || 0} MB
            </div>
          </div>
        </div>
      </div>

      {/* System Resources */}
      <div className="grid grid-3">
        <div className="card">
          <div className="card-header">
            <Cpu size={20} />
            <h3>CPU</h3>
          </div>
          <div className="card-body">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${stats?.cpu?.currentload || 0}%` }}
              />
            </div>
            <div className="stat-label">{(stats?.cpu?.currentload || 0).toFixed(1)}% Load</div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <Database size={20} />
            <h3>Memory</h3>
          </div>
          <div className="card-body">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ 
                  width: `${((stats?.mem?.active || 0) / (stats?.mem?.total || 1)) * 100}%` 
                }}
              />
            </div>
            <div className="stat-label">
              {((stats?.mem?.active || 0) / 1e9).toFixed(1)} / {((stats?.mem?.total || 0) / 1e9).toFixed(1)} GB
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <HardDrive size={20} />
            <h3>Disk</h3>
          </div>
          <div className="card-body">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ 
                  width: `${((stats?.disk?.[0]?.used || 0) / (stats?.disk?.[0]?.size || 1)) * 100}%` 
                }}
              />
            </div>
            <div className="stat-label">
              {((stats?.disk?.[0]?.used || 0) / 1e9).toFixed(0)} / {((stats?.disk?.[0]?.size || 0) / 1e9).toFixed(0)} GB
            </div>
          </div>
        </div>
      </div>

      {/* Recent Projects */}
      <div className="card">
        <div className="card-header">
          <h3>Recent Projects</h3>
          <Link to="/projects" className="btn btn-sm">View All</Link>
        </div>
        <div className="card-body">
          {projects.length === 0 ? (
            <div className="empty-state">
              <p>No projects yet</p>
              <Link to="/projects" className="btn btn-primary">Create Project</Link>
            </div>
          ) : (
            <div className="list">
              {projects.map(project => (
                <Link 
                  key={project.id} 
                  to={`/projects/${project.id}`}
                  className="list-item"
                >
                  <div>
                    <div className="list-item-title">{project.name}</div>
                    <div className="list-item-subtitle">{project.description}</div>
                  </div>
                  <div className="list-item-meta">
                    {new Date(project.created_at).toLocaleDateString()}
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-3">
        <Link to="/projects" className="action-card">
          <div className="action-icon">📁</div>
          <h3>New Project</h3>
          <p>Start a new project with AI assistance</p>
        </Link>

        <Link to="/chat" className="action-card">
          <div className="action-icon">💬</div>
          <h3>Chat with AI</h3>
          <p>Get help from AI agents</p>
        </Link>

        <Link to="/research" className="action-card">
          <div className="action-icon">🔍</div>
          <h3>Research</h3>
          <p>Scrape and analyze web data</p>
        </Link>
      </div>
    </div>
  )
}

