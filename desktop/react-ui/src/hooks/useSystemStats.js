import { useEffect, useState } from 'react'

/**
 * Hook for system stats (GPU, CPU, RAM, Disk)
 */
export default function useSystemStats(interval = 5000) {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!window.electronAPI) {
      setError('Electron API not available')
      setLoading(false)
      return
    }

    const loadStats = async () => {
      try {
        const res = await window.electronAPI.systemStats()
        if (res.ok) {
          setStats(res)
          setError(null)
        } else {
          setError(res.error)
        }
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    loadStats()
    const id = setInterval(loadStats, interval)
    
    return () => clearInterval(id)
  }, [interval])

  return { stats, loading, error }
}

