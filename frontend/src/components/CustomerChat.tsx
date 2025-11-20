import { useState, useRef, useEffect } from 'react'
import { Send } from 'lucide-react'
import axios from 'axios'
import { useToast } from '../context/ToastContext'
import './CustomerChat.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

interface Message {
  id: string
  sender: 'customer' | 'agent'
  text: string
  timestamp: Date
}

export default function CustomerChat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      sender: 'agent',
      text: 'Hello! Welcome to our salon. How can I assist you today?',
      timestamp: new Date()
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const { addToast } = useToast()

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputValue.trim()) return

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      sender: 'customer',
      text: inputValue,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setLoading(true)

    try {
      // Send to backend
      const response = await axios.post(`${API_BASE_URL}/api/chat`, {
        message: inputValue,
        customer_name: 'Customer'
      })

      // Add agent response
      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'agent',
        text: response.data.response || 'I understand. Let me help you with that.',
        timestamp: new Date()
      }

      setMessages(prev => [...prev, agentMessage])
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMsg = axios.isAxiosError(error)
        ? error.response?.data?.detail || error.message
        : 'Failed to send message'
      addToast('error', `Error: ${errorMsg}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="customer-chat-container">
      <div className="chat-card">
        <div className="chat-header">
          <h2>Chat with Agent</h2>
          <div className="status-indicator">
            <span className="status-dot"></span>
            Agent Online
          </div>
        </div>

        <div className="chat-messages">
          {messages.map(message => (
            <div
              key={message.id}
              className={`message ${message.sender === 'customer' ? 'user-message' : 'agent-message'}`}
            >
              <div className="message-content">
                <p>{message.text}</p>
                <span className="message-time">
                  {message.timestamp.toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </span>
              </div>
            </div>
          ))}
          {loading && (
            <div className="message agent-message">
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form onSubmit={handleSendMessage} className="chat-input-form">
          <input
            type="text"
            value={inputValue}
            onChange={e => setInputValue(e.target.value)}
            placeholder="Type your message..."
            disabled={loading}
            className="chat-input"
          />
          <button type="submit" disabled={loading || !inputValue.trim()} className="send-btn">
            <Send size={20} />
          </button>
        </form>
      </div>
    </div>
  )
}
