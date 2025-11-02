import { useEffect, useState } from 'react'
import { apiClient } from '../api/client'
import { 
  TrendingUp, AlertCircle, CheckCircle, Clock, 
  Zap, Brain, Activity 
} from 'lucide-react'

export default function InsightsPanel({ activeTab }) {
  const [insights, setInsights] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadInsights()
  }, [activeTab])

  const loadInsights = async () => {
    setLoading(true)
    try {
      // Load different insights based on active tab
      if (activeTab === 'workspace') {
        await loadWorkspaceInsights()
      } else if (activeTab === 'ai') {
        await loadAIInsights()
      } else if (activeTab === 'research') {
        await loadResearchInsights()
      }
    } catch (error) {
      console.error('Failed to load insights:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadWorkspaceInsights = async () => {
    try {
      const [projectsRes, healthRes] = await Promise.all([
        apiClient.projects.list({ limit: 5 }),
        apiClient.health(),
      ])

      setStats({
        totalProjects: projectsRes.data.length,
        backendStatus: healthRes.data.status,
      })

      setInsights([
        {
          type: 'success',
          icon: CheckCircle,
          title: 'Backend Healthy',
          description: 'All systems operational',
          time: 'Just now',
        },
        {
          type: 'info',
          icon: TrendingUp,
          title: `${projectsRes.data.length} Active Projects`,
          description: 'View all projects',
          time: '2m ago',
        },
      ])
    } catch (error) {
      setInsights([
        {
          type: 'error',
          icon: AlertCircle,
          title: 'Backend Offline',
          description: 'Start the backend to continue',
          time: 'Just now',
        },
      ])
    }
  }

  const loadAIInsights = async () => {
    try {
      const [statusRes, agentsRes] = await Promise.all([
        apiClient.ai.status(),
        apiClient.orchestrator.agents(),
      ])

      setStats({
        frameworks: statusRes.data.total_frameworks,
        agents: agentsRes.data.agents?.length || 0,
      })

      setInsights([
        {
          type: 'success',
          icon: Zap,
          title: `${statusRes.data.total_frameworks} AI Frameworks`,
          description: 'All frameworks loaded',
          time: 'Just now',
        },
        {
          type: 'info',
          icon: Brain,
          title: `${agentsRes.data.agents?.length || 0} Active Agents`,
          description: 'Ready to assist',
          time: '1m ago',
        },
      ])
    } catch (error) {
      setInsights([
        {
          type: 'warning',
          icon: AlertCircle,
          title: 'AI System Loading',
          description: 'Please wait...',
          time: 'Just now',
        },
      ])
    }
  }

  const loadResearchInsights = async () => {
    setInsights([
      {
        type: 'info',
        icon: Activity,
        title: 'Research Tools Ready',
        description: 'ScrapeGraphAI, Firecrawl, Playwright',
        time: 'Just now',
      },
      {
        type: 'success',
        icon: CheckCircle,
        title: 'Memory System Active',
        description: '4-tier memory available',
        time: '5m ago',
      },
    ])
  }

  return (
    <div className="insights-panel">
      <div className="panel-header">
        <h3>Insights & Information</h3>
      </div>
      <div className="panel-content">
        {loading ? (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Loading insights...</p>
          </div>
        ) : (
          <>
            {/* Quick Stats */}
            {stats && (
              <div className="quick-stats">
                {Object.entries(stats).map(([key, value]) => (
                  <div key={key} className="stat-item">
                    <div className="stat-value">{value}</div>
                    <div className="stat-label">{key.replace(/([A-Z])/g, ' $1').trim()}</div>
                  </div>
                ))}
              </div>
            )}

            {/* Insights List */}
            <div className="insights-list">
              {insights.map((insight, idx) => (
                <div key={idx} className={`insight-item ${insight.type}`}>
                  <div className="insight-icon">
                    <insight.icon size={18} />
                  </div>
                  <div className="insight-content">
                    <div className="insight-title">{insight.title}</div>
                    <div className="insight-description">{insight.description}</div>
                  </div>
                  <div className="insight-time">
                    <Clock size={12} />
                    <span>{insight.time}</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Quick Actions */}
            <div className="quick-actions">
              <h4>Quick Actions</h4>
              <div className="action-buttons">
                {activeTab === 'workspace' && (
                  <>
                    <button className="action-btn">📝 New Note</button>
                    <button className="action-btn">📁 New Project</button>
                  </>
                )}
                {activeTab === 'ai' && (
                  <>
                    <button className="action-btn">💬 Chat with AI</button>
                    <button className="action-btn">⚡ Run Skill</button>
                  </>
                )}
                {activeTab === 'research' && (
                  <>
                    <button className="action-btn">🔍 New Research</button>
                    <button className="action-btn">📊 View Results</button>
                  </>
                )}
              </div>
            </div>

            {/* Recent Activity */}
            <div className="recent-activity">
              <h4>Recent Activity</h4>
              <div className="activity-list">
                <div className="activity-item">
                  <div className="activity-dot"></div>
                  <div className="activity-text">Project created</div>
                  <div className="activity-time">10m ago</div>
                </div>
                <div className="activity-item">
                  <div className="activity-dot"></div>
                  <div className="activity-text">Research completed</div>
                  <div className="activity-time">1h ago</div>
                </div>
                <div className="activity-item">
                  <div className="activity-dot"></div>
                  <div className="activity-text">Skill executed</div>
                  <div className="activity-time">2h ago</div>
                </div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

