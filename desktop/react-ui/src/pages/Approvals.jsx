import { useEffect, useState } from 'react'
import { apiClient } from '../api/client'
import { CheckCircle, XCircle, Clock, AlertCircle, Eye } from 'lucide-react'

export default function Approvals() {
  const [pending, setPending] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedApproval, setSelectedApproval] = useState(null)
  const [showDetail, setShowDetail] = useState(false)

  useEffect(() => {
    loadPending()
  }, [])

  const loadPending = async () => {
    try {
      setLoading(true)
      const res = await apiClient.approvals.pending()
      setPending(res.data.pending || [])
    } catch (error) {
      console.error('Failed to load pending approvals:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = async (id) => {
    try {
      await apiClient.approvals.approve(id, { approver: 'user' })
      alert('Approval granted!')
      loadPending()
    } catch (error) {
      console.error('Approval failed:', error)
      alert('Failed to approve: ' + error.message)
    }
  }

  const handleReject = async (id) => {
    const reason = prompt('Rejection reason (optional):')
    try {
      await apiClient.approvals.reject(id, { reason, rejector: 'user' })
      alert('Approval rejected')
      loadPending()
    } catch (error) {
      console.error('Rejection failed:', error)
      alert('Failed to reject: ' + error.message)
    }
  }

  const viewDetail = async (approval) => {
    try {
      const res = await apiClient.approvals.get(approval.id)
      setSelectedApproval(res.data)
      setShowDetail(true)
    } catch (error) {
      console.error('Failed to load approval detail:', error)
      setSelectedApproval(approval)
      setShowDetail(true)
    }
  }

  const getTypeIcon = (type) => {
    switch (type) {
      case 'skill':
        return '🛠️'
      case 'agent':
        return '🤖'
      default:
        return '📋'
    }
  }

  const getStatusBadge = (status) => {
    switch (status) {
      case 'pending':
        return <span className="status-badge status-warning"><Clock size={14} /> Pending</span>
      case 'approved':
        return <span className="status-badge status-success"><CheckCircle size={14} /> Approved</span>
      case 'rejected':
        return <span className="status-badge status-danger"><XCircle size={14} /> Rejected</span>
      default:
        return <span className="status-badge"><AlertCircle size={14} /> {status}</span>
    }
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>Approvals</h1>
          <p className="text-muted">Review and approve pending requests</p>
        </div>
        <button className="btn btn-primary" onClick={loadPending}>
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="empty-state">
          <Clock size={48} />
          <p>Loading approvals...</p>
        </div>
      ) : pending.length === 0 ? (
        <div className="empty-state">
          <CheckCircle size={48} />
          <h3>No Pending Approvals</h3>
          <p>All requests have been processed</p>
        </div>
      ) : (
        <div className="approvals-list">
          {pending.map((approval) => (
            <div key={approval.id} className="approval-card">
              <div className="approval-header">
                <div className="approval-title">
                  <span className="approval-icon">{getTypeIcon(approval.type)}</span>
                  <div>
                    <h3>{approval.name}</h3>
                    <p className="text-muted">{approval.type}</p>
                  </div>
                </div>
                {getStatusBadge(approval.status)}
              </div>

              <div className="approval-body">
                {approval.reason && (
                  <div className="approval-reason">
                    <strong>Reason:</strong> {approval.reason}
                  </div>
                )}
                
                {approval.config && (
                  <div className="approval-config">
                    <strong>Configuration:</strong>
                    <pre>{JSON.stringify(approval.config, null, 2)}</pre>
                  </div>
                )}

                <div className="approval-meta">
                  <span>Requested: {new Date(approval.timestamp || Date.now()).toLocaleString()}</span>
                  {approval.requester && <span>By: {approval.requester}</span>}
                </div>
              </div>

              <div className="approval-actions">
                <button 
                  className="btn btn-sm"
                  onClick={() => viewDetail(approval)}
                >
                  <Eye size={16} /> View Details
                </button>
                <button 
                  className="btn btn-sm btn-success"
                  onClick={() => handleApprove(approval.id)}
                >
                  <CheckCircle size={16} /> Approve
                </button>
                <button 
                  className="btn btn-sm btn-danger"
                  onClick={() => handleReject(approval.id)}
                >
                  <XCircle size={16} /> Reject
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Detail Modal */}
      {showDetail && selectedApproval && (
        <div className="modal-overlay" onClick={() => setShowDetail(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Approval Details</h2>
              <button className="modal-close" onClick={() => setShowDetail(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="detail-grid">
                <div className="detail-item">
                  <label>ID:</label>
                  <span>{selectedApproval.id}</span>
                </div>
                <div className="detail-item">
                  <label>Type:</label>
                  <span>{selectedApproval.type}</span>
                </div>
                <div className="detail-item">
                  <label>Name:</label>
                  <span>{selectedApproval.name}</span>
                </div>
                <div className="detail-item">
                  <label>Status:</label>
                  {getStatusBadge(selectedApproval.status)}
                </div>
                {selectedApproval.reason && (
                  <div className="detail-item full-width">
                    <label>Reason:</label>
                    <p>{selectedApproval.reason}</p>
                  </div>
                )}
                {selectedApproval.config && (
                  <div className="detail-item full-width">
                    <label>Configuration:</label>
                    <pre className="code-block">{JSON.stringify(selectedApproval.config, null, 2)}</pre>
                  </div>
                )}
                {selectedApproval.timestamp && (
                  <div className="detail-item">
                    <label>Requested:</label>
                    <span>{new Date(selectedApproval.timestamp).toLocaleString()}</span>
                  </div>
                )}
                {selectedApproval.requester && (
                  <div className="detail-item">
                    <label>Requester:</label>
                    <span>{selectedApproval.requester}</span>
                  </div>
                )}
                {selectedApproval.approver && (
                  <div className="detail-item">
                    <label>Approver:</label>
                    <span>{selectedApproval.approver}</span>
                  </div>
                )}
                {selectedApproval.approved_at && (
                  <div className="detail-item">
                    <label>Approved At:</label>
                    <span>{new Date(selectedApproval.approved_at).toLocaleString()}</span>
                  </div>
                )}
              </div>
            </div>
            <div className="modal-footer">
              {selectedApproval.status === 'pending' && (
                <>
                  <button 
                    className="btn btn-success"
                    onClick={() => {
                      handleApprove(selectedApproval.id)
                      setShowDetail(false)
                    }}
                  >
                    <CheckCircle size={16} /> Approve
                  </button>
                  <button 
                    className="btn btn-danger"
                    onClick={() => {
                      handleReject(selectedApproval.id)
                      setShowDetail(false)
                    }}
                  >
                    <XCircle size={16} /> Reject
                  </button>
                </>
              )}
              <button className="btn" onClick={() => setShowDetail(false)}>
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

