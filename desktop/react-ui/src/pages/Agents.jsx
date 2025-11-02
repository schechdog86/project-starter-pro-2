import { useEffect, useState } from 'react'
import { apiClient } from '../api/client'
import { Bot, Plus, Trash2, Eye } from 'lucide-react'

export default function Agents() {
  const [agents, setAgents] = useState([])
  const [status, setStatus] = useState(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [newAgent, setNewAgent] = useState({ name: '', config: {}, approve: true })

  useEffect(() => {
    loadAgents()
    loadStatus()
  }, [])

  const loadAgents = async () => {
    try {
      const res = await apiClient.orchestrator.agents()
      setAgents(res.data.agents || [])
    } catch (error) {
      console.error('Failed to load agents:', error)
    }
  }

  const loadStatus = async () => {
    try {
      const res = await apiClient.orchestrator.status()
      setStatus(res.data)
    } catch (error) {
      console.error('Failed to load status:', error)
    }
  }

  const handleCreateAgent = async (e) => {
    e.preventDefault()
    try {
      await apiClient.orchestrator.createAgent(newAgent)
      alert('Agent created successfully!')
      setShowCreateModal(false)
      setNewAgent({ name: '', config: {}, approve: true })
      loadAgents()
    } catch (error) {
      console.error('Failed to create agent:', error)
      alert('Failed to create agent: ' + error.message)
    }
  }

  const handleDeleteAgent = async (name) => {
    if (!confirm(`Are you sure you want to delete agent "${name}"?`)) {
      return
    }
    try {
      await apiClient.orchestrator.destroyAgent(name)
      alert('Agent deleted successfully!')
      loadAgents()
    } catch (error) {
      console.error('Failed to delete agent:', error)
      alert('Failed to delete agent: ' + error.message)
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>AI Agents</h1>
          <p className="text-muted">Manage and monitor AI agents</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
          <Plus size={20} />
          Create Agent
        </button>
      </div>

      <div className="card">
        <div className="card-header">
          <Bot size={20} />
          <h3>Active Agents ({agents.length})</h3>
        </div>
        <div className="card-body">
          {agents.length === 0 ? (
            <div className="empty-state">
              <p>No agents loaded</p>
            </div>
          ) : (
            <div className="list">
              {agents.map((agent, idx) => (
                <div key={idx} className="list-item">
                  <div className="list-item-title">
                    <Bot size={16} />
                    {agent}
                  </div>
                  <div className="list-item-actions">
                    <button className="btn btn-sm" title="View Details">
                      <Eye size={16} />
                    </button>
                    <button
                      className="btn btn-sm btn-danger"
                      onClick={() => handleDeleteAgent(agent)}
                      title="Delete Agent"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {status && (
        <div className="card">
          <div className="card-header">
            <h3>Orchestrator Status</h3>
          </div>
          <div className="card-body">
            <pre className="code-block">{JSON.stringify(status, null, 2)}</pre>
          </div>
        </div>
      )}

      {/* Create Agent Modal */}
      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Create New Agent</h2>
              <button className="modal-close" onClick={() => setShowCreateModal(false)}>×</button>
            </div>
            <form onSubmit={handleCreateAgent}>
              <div className="modal-body">
                <div className="form-group">
                  <label>Agent Name *</label>
                  <input
                    type="text"
                    value={newAgent.name}
                    onChange={(e) => setNewAgent({ ...newAgent, name: e.target.value })}
                    placeholder="e.g., research_agent"
                    required
                  />
                </div>
                <div className="form-group">
                  <label>Configuration (JSON)</label>
                  <textarea
                    value={JSON.stringify(newAgent.config, null, 2)}
                    onChange={(e) => {
                      try {
                        setNewAgent({ ...newAgent, config: JSON.parse(e.target.value) })
                      } catch (err) {
                        // Invalid JSON, ignore
                      }
                    }}
                    rows={6}
                    placeholder='{"role": "researcher", "skills": []}'
                  />
                </div>
                <div className="form-group">
                  <label className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={newAgent.approve}
                      onChange={(e) => setNewAgent({ ...newAgent, approve: e.target.checked })}
                    />
                    Auto-approve agent
                  </label>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn" onClick={() => setShowCreateModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  <Plus size={16} /> Create Agent
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
