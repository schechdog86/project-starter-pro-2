import { useEffect, useState } from 'react'
import { apiClient } from '../api/client'
import { Zap, Plus, Play, Check, X } from 'lucide-react'

export default function Skills() {
  const [skills, setSkills] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadSkills()
  }, [])

  const loadSkills = async () => {
    setLoading(true)
    try {
      const res = await apiClient.skills.list()
      setSkills(res.data.skills || [])
    } catch (error) {
      console.error('Failed to load skills:', error)
    } finally {
      setLoading(false)
    }
  }

  const toggleSkill = async (name, enabled) => {
    try {
      await apiClient.skills.approve(name, { enabled: !enabled })
      await loadSkills()
    } catch (error) {
      console.error('Failed to toggle skill:', error)
    }
  }

  const executeSkill = async (name) => {
    try {
      const params = prompt('Enter parameters (JSON):')
      if (!params) return
      
      const result = await apiClient.skills.execute(name, { params: JSON.parse(params) })
      alert(`Result: ${JSON.stringify(result.data, null, 2)}`)
    } catch (error) {
      console.error('Failed to execute skill:', error)
      alert('Failed to execute skill')
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Skills</h1>
          <p className="text-muted">Manage AI skills and capabilities</p>
        </div>
        <button className="btn btn-primary">
          <Plus size={20} />
          Add Skill
        </button>
      </div>

      {loading ? (
        <div className="loading">Loading skills...</div>
      ) : (
        <div className="grid grid-2">
          {skills.map(skill => (
            <div key={skill.name} className="card">
              <div className="card-header">
                <Zap size={20} />
                <h3>{skill.name}</h3>
                <div className="spacer" />
                {skill.enabled ? (
                  <span className="status-badge success">
                    <Check size={14} /> Enabled
                  </span>
                ) : (
                  <span className="status-badge">
                    <X size={14} /> Disabled
                  </span>
                )}
              </div>
              <div className="card-body">
                <p className="text-muted">{skill.description || 'No description'}</p>
                {skill.parameters && (
                  <div className="skill-params">
                    <strong>Parameters:</strong>
                    <ul>
                      {Object.keys(skill.parameters).map(param => (
                        <li key={param}>{param}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
              <div className="card-footer">
                <button
                  className="btn btn-sm"
                  onClick={() => toggleSkill(skill.name, skill.enabled)}
                >
                  {skill.enabled ? 'Disable' : 'Enable'}
                </button>
                {skill.enabled && (
                  <button
                    className="btn btn-sm btn-primary"
                    onClick={() => executeSkill(skill.name)}
                  >
                    <Play size={16} />
                    Execute
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

