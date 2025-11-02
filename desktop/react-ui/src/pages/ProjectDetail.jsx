import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { apiClient } from '../api/client'
import { ArrowLeft, Play, FileText } from 'lucide-react'

export default function ProjectDetail() {
  const { id } = useParams()
  const [project, setProject] = useState(null)
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)
  const [flow, setFlow] = useState(null)
  const [ragQuery, setRagQuery] = useState('')
  const [ragResults, setRagResults] = useState([])
  const [ingesting, setIngesting] = useState(false)
  const [docCategory, setDocCategory] = useState('docs')
  const [docFiles, setDocFiles] = useState([])
  const [docsLoading, setDocsLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [uploadFile, setUploadFile] = useState(null)


  useEffect(() => {
    loadProject()
  }, [id])

  const loadProject = async () => {
    setLoading(true)
    try {
      const res = await apiClient.projects.get(id)
      setProject(res.data)
    } catch (error) {
      console.error('Failed to load project:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadFlow = async () => {
    if (!project?.name) return
    try {
      const res = await apiClient.projects.status(project.name)
      setFlow(res.data.project || res.data)
    } catch (e) {
      console.error('Failed to load flow:', e)
    }
  }

  const ingestDocs = async () => {
    if (!project?.name) return
    setIngesting(true)
    try {
      await apiClient.rag.ingest(project.name, { categories: null })
      alert('Ingestion started/completed')
    } catch (e) {
      console.error('Failed to ingest:', e)
      alert('Failed to ingest')
    } finally {
      setIngesting(false)
    }
  }

  const searchRag = async () => {
    if (!project?.name || !ragQuery.trim()) return
    try {
      const res = await apiClient.rag.search(project.name, { q: ragQuery, k: 8 })
      setRagResults(res?.data?.results || [])
    } catch (e) {
      console.error('RAG search failed:', e)
      setRagResults([])
    }
  }

  const refreshDocs = async () => {
    if (!project?.name) return
    setDocsLoading(true)
    try {
      const res = await apiClient.docs.list(project.name, { category: docCategory })
      setDocFiles(res?.data?.items || [])
    } catch (e) {
      console.error('List docs failed:', e)
      setDocFiles([])
    } finally {
      setDocsLoading(false)
    }
  }

  const doUpload = async () => {
    if (!project?.name || !uploadFile) return
    setUploading(true)
    try {
      const fd = new FormData()
      fd.append('category', docCategory)
      fd.append('file', uploadFile)
      await apiClient.rag.upload(project.name, fd)
      setUploadFile(null)
      await refreshDocs()
      alert('Uploaded and indexed')
    } catch (e) {
      console.error('Upload failed:', e)
      alert('Upload failed')
    } finally {
      setUploading(false)
    }
  }

  useEffect(() => {
    if (project?.name) {
      loadFlow()
      refreshDocs()
    }
  }, [project?.name])

  useEffect(() => {
    if (project?.name) {
      refreshDocs()
    }
  }, [docCategory])

  const runProject = async () => {
    setRunning(true)
    try {
      await apiClient.projects.run(project.name)
      await loadFlow()
      alert('Project started successfully')
    } catch (error) {
      console.error('Failed to run project:', error)
      alert('Failed to run project')
    } finally {
      setRunning(false)
    }
  }

  if (loading) return <div className="page"><div className="loading">Loading...</div></div>
  if (!project) return <div className="page"><div className="error">Project not found</div></div>

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <Link to="/projects" className="back-link">
            <ArrowLeft size={20} />
            Back to Projects
          </Link>
          <h1>{project.name}</h1>
          <p className="text-muted">{project.description}</p>
        </div>
        <button
          className="btn btn-primary"
          onClick={runProject}
          disabled={running}
        >
          <Play size={20} />
          {running ? 'Running...' : 'Run Project'}
        </button>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <div className="card-header">
            <FileText size={20} />
            <h3>Project Info</h3>
          </div>
          <div className="card-body">
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">ID</span>
                <span className="info-value">{project.id}</span>
              </div>
              <div className="info-item">
                <span className="info-label">Created</span>
                <span className="info-value">
                  {new Date(project.created_at).toLocaleString()}
                </span>
              </div>
            </div>
          </div>
        </div>


        <div className="card">
          <div className="card-header">
            <h3>Document Flow</h3>
          </div>
          <div className="card-body">
            {!flow ? (
              <div className="text-muted">No workflow data yet.</div>
            ) : (
              <div className="info-grid">
                <div className="info-item">
                  <span className="info-label">Phase</span>
                  <span className="info-value">{flow.phase}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Next Doc</span>
                  <span className="info-value">{flow.next_required_doc || 'None'}</span>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3>Project RAG</h3>
          </div>
          <div className="card-body">
            <div style={{ display: 'grid', gap: 12 }}>
              <div style={{ display: 'flex', gap: 8 }}>
                <button className="btn" onClick={ingestDocs} disabled={ingesting}>
                  {ingesting ? 'Ingesting…' : 'Ingest Docs'}
                </button>
                <input className="input" placeholder="Search project RAG…" value={ragQuery} onChange={(e)=>setRagQuery(e.target.value)} />
                <button className="btn" onClick={searchRag}>Search</button>
              </div>

              <div className="divider" />

              <div>
                <h4>Upload to Category</h4>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
                  <select className="select" value={docCategory} onChange={(e)=>setDocCategory(e.target.value)}>
                    <option value="docs">docs</option>
                    <option value="code">code</option>
                    <option value="graphics">graphics</option>
                    <option value="marketing">marketing</option>
                    <option value="research">research</option>
                  </select>
                  <input className="input" type="file" onChange={(e)=>setUploadFile(e.target.files?.[0] || null)} />
                  <button className="btn" onClick={doUpload} disabled={uploading || !uploadFile}>{uploading ? 'Uploading…' : 'Upload'}</button>
                  <button className="btn" onClick={refreshDocs} disabled={docsLoading}>{docsLoading ? 'Refreshing…' : 'Refresh'}</button>
                </div>
              </div>

              <div>
                <h4>Files in {docCategory}</h4>
                {docsLoading ? (
                  <div className="text-muted">Loading…</div>
                ) : docFiles.length > 0 ? (
                  <ul className="list">
                    {docFiles.map((f) => (
                      <li key={f.path}>
                        <div>{f.name}</div>
                        <div className="text-muted" style={{ fontSize: 12 }}>{(f.size || 0)} bytes</div>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <div className="text-muted">No files found</div>
                )}
              </div>

              <div className="divider" />

              <div>
                <h4>RAG Results</h4>
                {ragResults.length > 0 ? (
                  <ul className="list">
                    {ragResults.map((it, idx) => (
                      <li key={it.id || idx}>
                        <div className="text-muted" style={{ fontSize: 12 }}>
                          {it.source ? `${it.source}/` : ''}{it.category || it.tier || ''}
                        </div>
                        <div>{it.title || it.meta?.title || 'Untitled'}</div>
                        <div className="text-muted" style={{ fontSize: 12 }}>
                          {(it.summary || it.text || it.meta?.text || '').slice(0, 160)}
                        </div>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <div className="text-muted">No results</div>
                )}
              </div>
            </div>
              <ul className="list">
                {ragResults.map((it, idx) => (
                  <li key={it.id || idx}>
                    <div className="text-muted" style={{ fontSize: 12 }}>
                      {it.source ? `${it.source}/` : ''}{it.category || it.tier || ''}
                    </div>
                    <div>{it.title || it.meta?.title || 'Untitled'}</div>
                    <div className="text-muted" style={{ fontSize: 12 }}>
                      {(it.summary || it.text || it.meta?.text || '').slice(0, 160)}
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <div className="text-muted">No results</div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

