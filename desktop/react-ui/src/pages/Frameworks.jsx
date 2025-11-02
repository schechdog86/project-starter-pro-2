import { useEffect, useState } from 'react'
import { apiClient } from '../api/client'
import { Package, CheckCircle, XCircle, Filter, Search } from 'lucide-react'

export default function Frameworks() {
  const [frameworks, setFrameworks] = useState({})
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    loadFrameworks()
  }, [])

  const loadFrameworks = async () => {
    try {
      setLoading(true)
      const res = await apiClient.frameworks.list()
      setFrameworks(res.data)
    } catch (error) {
      console.error('Failed to load frameworks:', error)
    } finally {
      setLoading(false)
    }
  }

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'core':
        return '🎯'
      case 'multi_agents':
        return '🤖'
      case 'enterprise':
        return '🏢'
      case 'transformers':
        return '🔄'
      default:
        return '📦'
    }
  }

  const getCategoryName = (category) => {
    switch (category) {
      case 'core':
        return 'Core AI Frameworks'
      case 'multi_agents':
        return 'Multi-Agent Systems'
      case 'enterprise':
        return 'Enterprise Frameworks'
      case 'transformers':
        return 'Transformers & Models'
      default:
        return category
    }
  }

  const filteredFrameworks = () => {
    let result = frameworks

    // Filter by category
    if (filter !== 'all') {
      result = { [filter]: frameworks[filter] }
    }

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      result = Object.entries(result).reduce((acc, [category, fws]) => {
        const filtered = fws.filter(fw => fw.toLowerCase().includes(query))
        if (filtered.length > 0) {
          acc[category] = filtered
        }
        return acc
      }, {})
    }

    return result
  }

  const totalCount = Object.values(frameworks).reduce((sum, fws) => sum + fws.length, 0)
  const filtered = filteredFrameworks()
  const filteredCount = Object.values(filtered).reduce((sum, fws) => sum + fws.length, 0)

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>AI Frameworks</h1>
          <p className="text-muted">
            {totalCount} frameworks loaded across {Object.keys(frameworks).length} categories
          </p>
        </div>
        <button className="btn btn-primary" onClick={loadFrameworks}>
          Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="frameworks-filters">
        <div className="filter-group">
          <Filter size={18} />
          <select 
            value={filter} 
            onChange={(e) => setFilter(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Categories</option>
            <option value="core">Core AI</option>
            <option value="multi_agents">Multi-Agent Systems</option>
            <option value="enterprise">Enterprise</option>
            <option value="transformers">Transformers</option>
          </select>
        </div>

        <div className="search-group">
          <Search size={18} />
          <input
            type="text"
            placeholder="Search frameworks..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="search-input"
          />
        </div>
      </div>

      {loading ? (
        <div className="empty-state">
          <Package size={48} />
          <p>Loading frameworks...</p>
        </div>
      ) : filteredCount === 0 ? (
        <div className="empty-state">
          <XCircle size={48} />
          <h3>No Frameworks Found</h3>
          <p>Try adjusting your filters or search query</p>
        </div>
      ) : (
        <div className="frameworks-grid">
          {Object.entries(filtered).map(([category, fws]) => (
            <div key={category} className="framework-category">
              <div className="category-header">
                <span className="category-icon">{getCategoryIcon(category)}</span>
                <h2>{getCategoryName(category)}</h2>
                <span className="category-count">{fws.length}</span>
              </div>

              <div className="framework-list">
                {fws.map((fw) => (
                  <div key={fw} className="framework-item">
                    <CheckCircle size={16} className="framework-status" />
                    <span className="framework-name">{fw}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Summary Stats */}
      <div className="frameworks-summary">
        <div className="summary-card">
          <Package size={24} />
          <div>
            <div className="summary-value">{totalCount}</div>
            <div className="summary-label">Total Frameworks</div>
          </div>
        </div>
        <div className="summary-card">
          <CheckCircle size={24} />
          <div>
            <div className="summary-value">{Object.keys(frameworks).length}</div>
            <div className="summary-label">Categories</div>
          </div>
        </div>
        <div className="summary-card">
          <Filter size={24} />
          <div>
            <div className="summary-value">{filteredCount}</div>
            <div className="summary-label">Filtered Results</div>
          </div>
        </div>
      </div>

      {/* Framework Details */}
      <div className="framework-details">
        <h3>Framework Categories</h3>
        <div className="details-grid">
          <div className="detail-card">
            <h4>🎯 Core AI Frameworks</h4>
            <p>Primary LLM application frameworks for building AI-powered applications</p>
            <ul>
              <li>LangChain - Modular framework with RAG, memory, tools</li>
              <li>LlamaIndex - Data ingestion and retrieval (RAG-focused)</li>
              <li>Haystack - End-to-end NLP framework</li>
              <li>LiteLLM - Unified API for 100+ LLMs</li>
              <li>ScrapeGraphAI - AI-powered web scraping</li>
            </ul>
          </div>

          <div className="detail-card">
            <h4>🤖 Multi-Agent Systems</h4>
            <p>Frameworks for building collaborative AI agent teams</p>
            <ul>
              <li>AutoGen - Microsoft multi-agent communication</li>
              <li>CrewAI - Role-based agent teamwork</li>
              <li>LangGraph - Graph-based stateful agents</li>
              <li>MetaGPT - Hierarchical agent collaboration</li>
              <li>Semantic Kernel - Microsoft AI skills framework</li>
              <li>Atomic Agents - Schema-based modular agents</li>
              <li>Smolagents - Lightweight minimal agents</li>
            </ul>
          </div>

          <div className="detail-card">
            <h4>🏢 Enterprise Frameworks</h4>
            <p>Production-ready frameworks for enterprise applications</p>
            <ul>
              <li>Semantic Kernel - Enterprise AI orchestration</li>
              <li>Rasa - Conversational AI platform</li>
            </ul>
          </div>

          <div className="detail-card">
            <h4>🔄 Transformers & Models</h4>
            <p>Hugging Face ecosystem and model infrastructure</p>
            <ul>
              <li>Transformers - Pre-trained models</li>
              <li>Sentence-Transformers - Semantic embeddings</li>
              <li>Datasets - Data loading and processing</li>
              <li>Accelerate - Training acceleration</li>
              <li>PyTorch - Deep learning framework</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

