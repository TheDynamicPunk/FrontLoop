import { useState, useEffect } from 'react'
import { Send, CheckCircle, Clock, AlertCircle } from 'lucide-react'
import axios from 'axios'
import { useToast } from '../context/ToastContext'
import './SupervisorDashboard.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

interface HelpRequest {
  id: string
  customer_name: string
  question: string
  status: 'pending' | 'resolved'
  created_at: string
  resolved_at?: string
  answer?: string
}

interface SupervisorDashboardProps {
  onPendingCountChange?: (count: number) => void
}

export default function SupervisorDashboard({ onPendingCountChange }: SupervisorDashboardProps) {
  const [requests, setRequests] = useState<HelpRequest[]>([])
  const [selectedRequest, setSelectedRequest] = useState<HelpRequest | null>(null)
  const [responseText, setResponseText] = useState('')
  const [loading, setLoading] = useState(false)
  const [filterMode, setFilterMode] = useState<'pending' | 'resolved'>('pending')
  const { addToast } = useToast()

  useEffect(() => {
    fetchRequests()
    const interval = setInterval(fetchRequests, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchRequests = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/requests`)
      const requestsData = response.data || []
      setRequests(requestsData)
      
      // Update pending count in parent
      if (onPendingCountChange) {
        const pendingCount = requestsData.filter((r: HelpRequest) => r.status === 'pending').length
        onPendingCountChange(pendingCount)
      }
    } catch (error) {
      console.error('Error fetching requests:', error)
      const errorMsg = axios.isAxiosError(error)
        ? error.response?.data?.detail || error.message
        : 'Failed to fetch requests'
      addToast('error', `Error: ${errorMsg}`)
    }
  }

  const handleSubmitResponse = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedRequest || !responseText.trim()) return

    setLoading(true)
    try {
      await axios.post(`${API_BASE_URL}/respond`), {
        request_id: selectedRequest.id,
        answer: responseText
      }

      addToast('success', 'Response sent successfully!')
      setResponseText('')
      setSelectedRequest(null)
      await fetchRequests()
    } catch (error) {
      console.error('Error submitting response:', error)
      const errorMsg = axios.isAxiosError(error)
        ? error.response?.data?.detail || error.message
        : 'Failed to send response'
      addToast('error', `Error: ${errorMsg}`)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return '#f59e0b'
      case 'resolved':
        return '#10b981'
      default:
        return '#6b7280'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Clock size={18} />
      case 'resolved':
        return <CheckCircle size={18} />
      default:
        return null
    }
  }

  const getFilteredRequests = () => {
    let filtered: HelpRequest[]
    
    if (filterMode === 'pending') {
      filtered = requests.filter(r => r.status === 'pending')
    } else {
      filtered = requests.filter(r => r.status === 'resolved')
    }
    
    // Sort by created_at date, newest first
    return filtered.sort((a, b) => {
      const dateA = new Date(a.created_at).getTime()
      const dateB = new Date(b.created_at).getTime()
      return dateB - dateA
    })
  }

  const filteredRequests = getFilteredRequests()

  return (
    <div className="supervisor-container">
      <div className="supervisor-layout">
        <div className="requests-list">
          <h2>Help Requests</h2>
          <div className="filter-toggle">
            <button
              className={`filter-btn ${filterMode === 'pending' ? 'active' : ''}`}
              onClick={() => setFilterMode('pending')}
            >
              <Clock size={16} />
              Pending
            </button>
            <button
              className={`filter-btn ${filterMode === 'resolved' ? 'active' : ''}`}
              onClick={() => setFilterMode('resolved')}
            >
              <CheckCircle size={16} />
              Resolved
            </button>
          </div>
          <div className="requests-scroll">
            {filteredRequests.length === 0 ? (
              <div className="empty-state">
                <p>No {filterMode} requests</p>
              </div>
            ) : (
              filteredRequests.map(request => (
                <div
                  key={request.id}
                  className={`request-item ${selectedRequest?.id === request.id ? 'selected' : ''}`}
                  onClick={() => setSelectedRequest(request)}
                >
                  <div className="request-header">
                    <span className="customer-name">{request.customer_name}</span>
                    <span className="status-badge" style={{ borderColor: getStatusColor(request.status) }}>
                      {getStatusIcon(request.status)}
                      <span>{request.status}</span>
                    </span>
                  </div>
                  <p className="request-question">{request.question}</p>
                  <span className="request-time">
                    {new Date(request.created_at).toLocaleTimeString()}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="response-panel">
          {selectedRequest ? (
            <>
              <div className="request-detail">
                <div className="detail-header">
                  <div>
                    <h3>{selectedRequest.customer_name}</h3>
                    <p className="detail-status" style={{ color: getStatusColor(selectedRequest.status) }}>
                      {getStatusIcon(selectedRequest.status)}
                      {selectedRequest.status}
                    </p>
                  </div>
                </div>

                <div className="question-section">
                  <h4>Customer Question</h4>
                  <p className="question-text">{selectedRequest.question}</p>
                </div>

                {selectedRequest.answer && (
                  <div className="answer-section">
                    <h4>Your Response</h4>
                    <p className="answer-text">{selectedRequest.answer}</p>
                  </div>
                )}

                {selectedRequest.status === 'pending' && (
                  <form onSubmit={handleSubmitResponse} className="response-form">
                    <textarea
                      value={responseText}
                      onChange={e => setResponseText(e.target.value)}
                      placeholder="Type your response here..."
                      className="response-textarea"
                      disabled={loading}
                    ></textarea>
                    <button type="submit" disabled={loading || !responseText.trim()} className="submit-btn">
                      <Send size={18} />
                      {loading ? 'Sending...' : 'Send Response'}
                    </button>
                  </form>
                )}
              </div>
            </>
          ) : (
            <div className="empty-panel">
              <p>Select a request to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
