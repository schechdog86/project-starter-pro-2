import { useState, useRef, useEffect } from 'react'
import { apiClient } from '../api/client'
import { Send, Bot, User, Settings } from 'lucide-react'

export default function Chat() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const messagesEndRef = useRef(null)

  // Project-aware chat state
  const [projects, setProjects] = useState([])
  const [selectedProject, setSelectedProject] = useState('')
  const [category, setCategory] = useState('docs')
  const [contextK, setContextK] = useState(8)

  // Chat settings
  const [showSettings, setShowSettings] = useState(false)
  const [provider, setProvider] = useState('openai')
  const [model, setModel] = useState('gpt-4o-mini')
  const [temperature, setTemperature] = useState(0.7)
  const [maxTokens, setMaxTokens] = useState(1000)
  const [providerOptions, setProviderOptions] = useState([])
  const [modelOptionsDyn, setModelOptionsDyn] = useState([])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Load available projects for selector (best-effort)
  useEffect(() => {
    const loadProjects = async () => {
      try {
        const res = await apiClient.projects.list()
        const items = res?.data?.projects || res?.data?.items || res?.data || []
        setProjects(Array.isArray(items) ? items : [])
      } catch (e) {
        console.warn('Projects list unavailable:', e)
      }
    }
    const loadProviders = async () => {
      try {
        const res = await apiClient.llm.providers()
        const provs = res?.data?.providers || []
        setProviderOptions(provs)
        if (provs.length && !provs.includes(provider)) {
          setProvider(provs[0])
        }
      } catch (e) {
        // fall back to static
      }
    }
    loadProjects()
    loadProviders()
  }, [])

  // Load models for selected provider (dynamic if available)
  useEffect(() => {
    const loadModels = async () => {
      if (!provider) return
      try {
        const res = await apiClient.llm.models(provider)
        const models = res?.data?.models || []
        setModelOptionsDyn(models)
        if (models.length && !models.includes(model)) {
          setModel(models[0])
        }
      } catch (e) {
        setModelOptionsDyn([])
      }
    }
    loadModels()
  }, [provider])

  const modelOptions = (prov) => {
    switch (prov) {
      case 'openai':
        return ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo']
      case 'anthropic':
        return ['claude-3-5-sonnet-20241022', 'claude-3-haiku']
      case 'deepseek':
        return ['deepseek-chat', 'deepseek-coder']
      default:
        return ['gpt-3.5-turbo']
    }
  }

  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim() || sending) return

    const userMessage = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
    setInput('')
    setSending(true)

    try {
      const res = await apiClient.llm.chatHistory({
        messages: [...messages, userMessage],
        provider,
        model,
        temperature,
        max_tokens: maxTokens,
        project: selectedProject || null,
        category,
        context_k: contextK,
      })

      const assistantMessage = {
        role: 'assistant',
        content: res.data.response || res.data.message || 'No response',
      }
      
      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Failed to send message:', error)
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Error: Failed to get response',
      }])
    } finally {
      setSending(false)
    }
  }

  return (
    <div className="page chat-page">
      <div className="page-header">
        <div>
          <h1>AI Chat</h1>
          <p className="text-muted">Chat with AI agents</p>
        </div>
        <div className="header-actions" style={{ display: 'flex', gap: 12, alignItems: 'center' }}>
          <select
            value={selectedProject}
            onChange={(e) => setSelectedProject(e.target.value)}
            className="select"
          >
            <option value="">No Project (General)</option>
            {projects.map((p) => (
              <option key={p.id || p.name} value={p.name || p.id}>{p.name || p.id}</option>
            ))}
          </select>
          <select value={category} onChange={(e) => setCategory(e.target.value)} className="select">
            <option value="docs">docs</option>
            <option value="code">code</option>
            <option value="graphics">graphics</option>
            <option value="marketing">marketing</option>
            <option value="research">research</option>
          </select>
          <button className="btn" onClick={() => setShowSettings(s => !s)} title="Chat settings">
            <Settings size={18} />
          </button>
        </div>
      </div>

      {showSettings && (
        <div className="card" style={{ marginBottom: 16 }}>
          <div className="card-header">
            <h3>Chat Settings</h3>
          </div>
          <div className="card-body settings-grid" style={{ display: 'grid', gap: 12, gridTemplateColumns: 'repeat(4, minmax(0, 1fr))' }}>
            <div>
              <label className="label">Provider</label>
              <select className="select" value={provider} onChange={(e) => {
                const p = e.target.value
                setProvider(p)
                const opts = modelOptionsDyn.length ? modelOptionsDyn : modelOptions(p)
                if (opts.length && !opts.includes(model)) setModel(opts[0])
              }}>
                {(providerOptions.length ? providerOptions : ['openai','anthropic','deepseek']).map((prov) => (
                  <option key={prov} value={prov}>{prov}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="label">Model</label>
              <select className="select" value={model} onChange={(e) => setModel(e.target.value)}>
                {(modelOptionsDyn.length ? modelOptionsDyn : modelOptions(provider)).map(m => <option key={m} value={m}>{m}</option>)}
              </select>
            </div>
            <div>
              <label className="label">Temperature: {temperature}</label>
              <input type="range" min="0" max="2" step="0.1" value={temperature} onChange={(e) => setTemperature(parseFloat(e.target.value))} />
            </div>
            <div>
              <label className="label">Max Tokens</label>
              <input className="input" type="number" min={1} max={32768} value={maxTokens} onChange={(e) => setMaxTokens(parseInt(e.target.value || '0', 10))} />
            </div>
            <div>
              <label className="label">Context K</label>
              <input className="input" type="number" min={1} max={20} value={contextK} onChange={(e) => setContextK(parseInt(e.target.value || '8', 10))} />
            </div>
          </div>
        </div>
      )}

      <div className="chat-container">
        <div className="chat-messages">
          {messages.length === 0 ? (
            <div className="empty-state">
              <Bot size={64} className="empty-icon" />
              <h2>Start a conversation</h2>
              <p>Ask me anything about your projects</p>
            </div>
          ) : (
            <>
              {messages.map((msg, idx) => (
                <div key={idx} className={`message ${msg.role}`}>
                  <div className="message-icon">
                    {msg.role === 'user' ? <User size={20} /> : <Bot size={20} />}
                  </div>
                  <div className="message-content">
                    <div className="message-text">{msg.content}</div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        <form onSubmit={handleSend} className="chat-input-form">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Type your message..."
            className="chat-input"
            disabled={sending}
          />
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={sending || !input.trim()}
          >
            <Send size={20} />
          </button>
        </form>
      </div>
    </div>
  )
}

