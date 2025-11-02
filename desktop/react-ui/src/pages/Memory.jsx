import { useEffect, useState } from 'react'
import { apiClient } from '../api/client'
import { Brain, Search, Plus } from 'lucide-react'

export default function Memory() {
  const [stats, setStats] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState([])
  const [searching, setSearching] = useState(false)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      const res = await apiClient.memory.stats()
      setStats(res.data)
    } catch (error) {
      console.error('Failed to load memory stats:', error)
    }
  }

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!searchQuery.trim()) return

    setSearching(true)
    try {
      const res = await apiClient.memory.search({ query: searchQuery, limit: 10 })
      setSearchResults(res.data.results || [])
    } catch (error) {
      console.error('Failed to search memory:', error)
    } finally {
      setSearching(false)
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Memory System</h1>
          <p className="text-muted">4-tier memory: ST, MT, LT_HOT, FV</p>
        </div>
      </div>

      {/* Memory Stats */}
      {stats && (
        <div className="grid grid-4">
          <div className="card">
            <div className="card-header">
              <h3>ST (Short-term)</h3>
            </div>
            <div className="card-body">
              <div className="stat-value">{stats.st_count || 0}</div>
              <div className="stat-label">memories</div>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h3>MT (Mid-term)</h3>
            </div>
            <div className="card-body">
              <div className="stat-value">{stats.mt_count || 0}</div>
              <div className="stat-label">memories</div>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h3>LT_HOT (Long-term)</h3>
            </div>
            <div className="card-body">
              <div className="stat-value">{stats.lt_hot_count || 0}</div>
              <div className="stat-label">memories</div>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h3>FV (Forever)</h3>
            </div>
            <div className="card-body">
              <div className="stat-value">{stats.fv_count || 0}</div>
              <div className="stat-label">memories</div>
            </div>
          </div>
        </div>
      )}

      {/* Search */}
      <div className="card">
        <div className="card-header">
          <Search size={20} />
          <h3>Search Memory</h3>
        </div>
        <div className="card-body">
          <form onSubmit={handleSearch} className="search-form">
            <input
              type="text"
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              placeholder="Search memories..."
              className="search-input"
            />
            <button type="submit" className="btn btn-primary" disabled={searching}>
              {searching ? 'Searching...' : 'Search'}
            </button>
          </form>

          {searchResults.length > 0 && (
            <div className="search-results">
              <h4>Results ({searchResults.length})</h4>
              <div className="list">
                {searchResults.map((result, idx) => (
                  <div key={idx} className="list-item">
                    <div>
                      <div className="list-item-title">{result.title || 'Untitled'}</div>
                      <div className="list-item-subtitle">{result.text}</div>
                    </div>
                    <div className="list-item-meta">
                      Score: {result.score?.toFixed(3)}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

