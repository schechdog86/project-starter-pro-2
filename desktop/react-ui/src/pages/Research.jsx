import { useState } from 'react'
import { apiClient } from '../api/client'
import { Search, Play } from 'lucide-react'

export default function Research() {
  const [url, setUrl] = useState('')
  const [query, setQuery] = useState('')
  const [running, setRunning] = useState(false)
  const [result, setResult] = useState(null)

  const handleRun = async (e) => {
    e.preventDefault()
    if (!url.trim()) return

    setRunning(true)
    setResult(null)
    
    try {
      const res = await apiClient.research.run({ url, query })
      setResult(res.data)
    } catch (error) {
      console.error('Failed to run research:', error)
      alert('Failed to run research')
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Research & Scraping</h1>
          <p className="text-muted">Extract and analyze web data with AI</p>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <Search size={20} />
          <h3>New Research Task</h3>
        </div>
        <div className="card-body">
          <form onSubmit={handleRun} className="form">
            <div className="form-group">
              <label>URL *</label>
              <input
                type="url"
                value={url}
                onChange={e => setUrl(e.target.value)}
                placeholder="https://example.com"
                required
              />
            </div>

            <div className="form-group">
              <label>Query (optional)</label>
              <input
                type="text"
                value={query}
                onChange={e => setQuery(e.target.value)}
                placeholder="What information to extract?"
              />
            </div>

            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={running}
            >
              <Play size={20} />
              {running ? 'Running...' : 'Run Research'}
            </button>
          </form>
        </div>
      </div>

      {result && (
        <div className="card">
          <div className="card-header">
            <h3>Results</h3>
          </div>
          <div className="card-body">
            <pre className="code-block">{JSON.stringify(result, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  )
}

