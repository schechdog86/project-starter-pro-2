import { useState } from 'react'
import { Outlet, useLocation } from 'react-router-dom'
import {
  Home, Bot, Search, Settings as SettingsIcon,
  FileText, Code, Image, Megaphone, BookOpen,
  ChevronRight, ChevronDown, File, Folder
} from 'lucide-react'
import FileTree from './FileTree'
import InsightsPanel from './InsightsPanel'

export default function Layout() {
  const location = useLocation()
  const [activeTab, setActiveTab] = useState('workspace')
  const [expandedTrees, setExpandedTrees] = useState({
    docs: true,
    code: true,
    graphics: false,
    marketing: false,
    research: true,
  })

  const tabs = [
    { id: 'workspace', label: 'Workspace', icon: Home },
    { id: 'ai', label: 'AI Agents', icon: Bot },
    { id: 'research', label: 'Research', icon: Search },
    { id: 'settings', label: 'Settings', icon: SettingsIcon },
  ]

  const toggleTree = (tree) => {
    setExpandedTrees(prev => ({ ...prev, [tree]: !prev[tree] }))
  }

  return (
    <div className="workspace-layout">
      {/* Top Tab Bar */}
      <div className="top-tabs">
        <div className="tabs-left">
          <div className="app-logo">
            <span className="logo-icon">🚀</span>
            <span className="logo-text">Project Starter Pro 2</span>
          </div>
        </div>
        <div className="tabs-center">
          {tabs.map(tab => (
            <button
              key={tab.id}
              className={`tab-btn ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <tab.icon size={18} />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
        <div className="tabs-right">
          <div className="status-indicator">
            <span className="status-dot online"></span>
            <span className="status-text">Backend Online</span>
          </div>
        </div>
      </div>

      {/* Main Workspace */}
      <div className="workspace-container">
        {/* Left Main View */}
        <div className="main-view">
          <Outlet context={{ activeTab }} />
        </div>

        {/* Right Sidebar - Split into two panels */}
        <div className="right-sidebar">
          {/* Top Panel - File Trees */}
          <div className="right-panel top-panel">
            <div className="panel-header">
              <h3>Project Files</h3>
            </div>
            <div className="panel-content">
              <FileTree
                title="Documentation"
                icon={FileText}
                expanded={expandedTrees.docs}
                onToggle={() => toggleTree('docs')}
                items={[
                  { name: '01_project_scope.md', type: 'file' },
                  { name: '02_research_outline.md', type: 'file' },
                  { name: '03_technical_spec.md', type: 'file' },
                  { name: '04_project_outline.md', type: 'file' },
                  { name: '10_business_plan.md', type: 'file' },
                  { name: 'README.md', type: 'file' },
                ]}
              />

              <FileTree
                title="Code"
                icon={Code}
                expanded={expandedTrees.code}
                onToggle={() => toggleTree('code')}
                items={[
                  { name: 'backend/', type: 'folder', children: [
                    { name: 'app/', type: 'folder' },
                    { name: 'requirements.txt', type: 'file' },
                  ]},
                  { name: 'frontend/', type: 'folder' },
                  { name: 'desktop/', type: 'folder' },
                ]}
              />

              <FileTree
                title="Graphics"
                icon={Image}
                expanded={expandedTrees.graphics}
                onToggle={() => toggleTree('graphics')}
                items={[
                  { name: 'logo.png', type: 'file' },
                  { name: 'screenshots/', type: 'folder' },
                ]}
              />

              <FileTree
                title="Marketing"
                icon={Megaphone}
                expanded={expandedTrees.marketing}
                onToggle={() => toggleTree('marketing')}
                items={[
                  { name: 'pitch_deck.pdf', type: 'file' },
                  { name: 'social_media/', type: 'folder' },
                ]}
              />

              <FileTree
                title="Research"
                icon={BookOpen}
                expanded={expandedTrees.research}
                onToggle={() => toggleTree('research')}
                items={[
                  { name: 'market_analysis.md', type: 'file' },
                  { name: 'competitor_research.md', type: 'file' },
                  { name: 'scraped_data/', type: 'folder' },
                ]}
              />
            </div>
          </div>

          {/* Bottom Panel - Insights & Information */}
          <div className="right-panel bottom-panel">
            <InsightsPanel activeTab={activeTab} />
          </div>
        </div>
      </div>
    </div>
  )
}

