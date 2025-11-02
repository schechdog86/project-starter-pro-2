import { useCallback, useEffect, useState } from 'react'

/**
 * Hook for managing Docker backend via Electron IPC
 */
export default function useBackend() {
  const [status, setStatus] = useState({ containers: [], ok: false })
  const [logs, setLogs] = useState('')
  const [loading, setLoading] = useState(false)

  const refresh = useCallback(async () => {
    if (!window.electronAPI) return
    setLoading(true)
    try {
      const res = await window.electronAPI.status()
      setStatus(res)
    } catch (error) {
      console.error('Failed to refresh status:', error)
    } finally {
      setLoading(false)
    }
  }, [])

  const composeUp = useCallback(async () => {
    if (!window.electronAPI) return
    setLoading(true)
    try {
      await window.electronAPI.composeUp()
      await refresh()
    } catch (error) {
      console.error('Failed to start backend:', error)
    } finally {
      setLoading(false)
    }
  }, [refresh])

  const composeDown = useCallback(async () => {
    if (!window.electronAPI) return
    setLoading(true)
    try {
      await window.electronAPI.composeDown()
      await refresh()
    } catch (error) {
      console.error('Failed to stop backend:', error)
    } finally {
      setLoading(false)
    }
  }, [refresh])

  const composeRestart = useCallback(async () => {
    if (!window.electronAPI) return
    setLoading(true)
    try {
      await window.electronAPI.composeRestart()
      await refresh()
    } catch (error) {
      console.error('Failed to restart backend:', error)
    } finally {
      setLoading(false)
    }
  }, [refresh])

  const composeRebuild = useCallback(async () => {
    if (!window.electronAPI) return
    setLoading(true)
    try {
      await window.electronAPI.composeRebuild()
      await refresh()
    } catch (error) {
      console.error('Failed to rebuild backend:', error)
    } finally {
      setLoading(false)
    }
  }, [refresh])

  const startLogs = useCallback(async (service = 'backend') => {
    if (!window.electronAPI) return
    setLogs('')
    try {
      await window.electronAPI.startLogs(service)
    } catch (error) {
      console.error('Failed to start logs:', error)
    }
  }, [])

  const stopLogs = useCallback(async () => {
    if (!window.electronAPI) return
    try {
      await window.electronAPI.stopLogs()
    } catch (error) {
      console.error('Failed to stop logs:', error)
    }
  }, [])

  const migrate = useCallback(async () => {
    if (!window.electronAPI) return
    setLoading(true)
    try {
      await window.electronAPI.migrate()
      return { ok: true }
    } catch (error) {
      console.error('Failed to run migrations:', error)
      return { ok: false, error }
    } finally {
      setLoading(false)
    }
  }, [])

  // Subscribe to log lines
  useEffect(() => {
    if (!window.electronAPI) return
    
    const unsubscribe = window.electronAPI.onLogLine((line) => {
      setLogs(prev => prev + line)
    })
    
    return () => {
      if (unsubscribe) unsubscribe()
    }
  }, [])

  // Initial refresh
  useEffect(() => {
    refresh()
    const interval = setInterval(refresh, 10000) // Refresh every 10s
    return () => clearInterval(interval)
  }, [refresh])

  return {
    status,
    logs,
    loading,
    refresh,
    composeUp,
    composeDown,
    composeRestart,
    composeRebuild,
    startLogs,
    stopLogs,
    migrate,
  }
}

