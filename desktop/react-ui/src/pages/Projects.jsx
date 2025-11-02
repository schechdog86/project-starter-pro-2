import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { apiClient } from '../api/client'
import { Plus, FolderKanban, Calendar, Trash2 } from 'lucide-react'

export default function Projects() {
  const [projects, setProjects] = useState([])
  const [loading, setLoading] = useState(true)
  const [showWizard, setShowWizard] = useState(false)

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    setLoading(true)
    try {
      const res = await apiClient.projects.list()
      setProjects(res.data)
    } catch (error) {
      console.error('Failed to load projects:', error)
    } finally {
      setLoading(false)
    }
  }

  const deleteProject = async (id) => {
    if (!confirm('Are you sure you want to delete this project?')) return
    
    try {
      await apiClient.projects.delete(id)
      await loadProjects()
    } catch (error) {
      console.error('Failed to delete project:', error)
      alert('Failed to delete project')
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Projects</h1>
          <p className="text-muted">Manage your projects</p>
        </div>
        <button 
          className="btn btn-primary"
          onClick={() => setShowWizard(true)}
        >
          <Plus size={20} />
          New Project
        </button>
      </div>

      {loading ? (
        <div className="loading">Loading projects...</div>
      ) : projects.length === 0 ? (
        <div className="empty-state">
          <FolderKanban size={64} className="empty-icon" />
          <h2>No projects yet</h2>
          <p>Create your first project to get started</p>
          <button 
            className="btn btn-primary"
            onClick={() => setShowWizard(true)}
          >
            <Plus size={20} />
            Create Project
          </button>
        </div>
      ) : (
        <div className="grid grid-3">
          {projects.map(project => (
            <div key={project.id} className="card project-card">
              <div className="card-header">
                <FolderKanban size={20} />
                <h3>{project.name}</h3>
              </div>
              <div className="card-body">
                <p className="text-muted">{project.description || 'No description'}</p>
                <div className="project-meta">
                  <div className="meta-item">
                    <Calendar size={14} />
                    <span>{new Date(project.created_at).toLocaleDateString()}</span>
                  </div>
                </div>
              </div>
              <div className="card-footer">
                <Link 
                  to={`/projects/${project.id}`}
                  className="btn btn-sm"
                >
                  Open
                </Link>
                <button
                  className="btn btn-sm btn-danger"
                  onClick={() => deleteProject(project.id)}
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {showWizard && (
        <ProjectWizard 
          onClose={() => setShowWizard(false)}
          onComplete={() => {
            setShowWizard(false)
            loadProjects()
          }}
        />
      )}
    </div>
  )
}

// Project Creation Wizard
function ProjectWizard({ onClose, onComplete }) {
  const [step, setStep] = useState(1)
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    type: 'software',
    template: 'blank',
  })
  const [creating, setCreating] = useState(false)

  const updateField = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const handleCreate = async () => {
    setCreating(true)
    try {
      await apiClient.projects.create(formData)
      onComplete()
    } catch (error) {
      console.error('Failed to create project:', error)
      alert('Failed to create project')
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Create New Project</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>

        <div className="modal-body">
          {step === 1 && (
            <div className="wizard-step">
              <h3>Project Details</h3>
              <div className="form-group">
                <label>Project Name *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={e => updateField('name', e.target.value)}
                  placeholder="My Awesome Project"
                  autoFocus
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={formData.description}
                  onChange={e => updateField('description', e.target.value)}
                  placeholder="What is this project about?"
                  rows={4}
                />
              </div>
            </div>
          )}

          {step === 2 && (
            <div className="wizard-step">
              <h3>Project Type</h3>
              <div className="type-grid">
                {[
                  { value: 'software', label: 'Software', icon: '💻', desc: 'Code project' },
                  { value: 'business', label: 'Business', icon: '💼', desc: 'Business plan' },
                  { value: 'research', label: 'Research', icon: '🔬', desc: 'Research project' },
                  { value: 'personal', label: 'Personal', icon: '📝', desc: 'Personal project' },
                ].map(type => (
                  <div
                    key={type.value}
                    className={`type-card ${formData.type === type.value ? 'selected' : ''}`}
                    onClick={() => updateField('type', type.value)}
                  >
                    <div className="type-icon">{type.icon}</div>
                    <h4>{type.label}</h4>
                    <p>{type.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="wizard-step">
              <h3>Template</h3>
              <div className="template-list">
                {[
                  { value: 'blank', label: 'Blank Project', desc: 'Start from scratch' },
                  { value: 'web-app', label: 'Web Application', desc: 'React + FastAPI template' },
                  { value: 'api', label: 'REST API', desc: 'FastAPI backend template' },
                  { value: 'ml', label: 'ML Project', desc: 'Machine learning template' },
                ].map(template => (
                  <div
                    key={template.value}
                    className={`template-item ${formData.template === template.value ? 'selected' : ''}`}
                    onClick={() => updateField('template', template.value)}
                  >
                    <h4>{template.label}</h4>
                    <p>{template.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="modal-footer">
          {step > 1 && (
            <button className="btn" onClick={() => setStep(step - 1)}>
              Back
            </button>
          )}
          <div className="spacer" />
          {step < 3 ? (
            <button 
              className="btn btn-primary" 
              onClick={() => setStep(step + 1)}
              disabled={step === 1 && !formData.name}
            >
              Next
            </button>
          ) : (
            <button 
              className="btn btn-primary" 
              onClick={handleCreate}
              disabled={creating || !formData.name}
            >
              {creating ? 'Creating...' : 'Create Project'}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

