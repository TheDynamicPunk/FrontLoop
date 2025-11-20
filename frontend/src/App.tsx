import { useState, useEffect } from 'react'
import { Sun, Moon } from 'lucide-react'
import { ToastProvider } from './context/ToastContext'
import { ThemeProvider, useTheme } from './context/ThemeContext'
import { ToastContainer } from './components/Toast'
import CustomerChat from './components/CustomerChat'
import SupervisorDashboard from './components/SupervisorDashboard'
import axios from 'axios'
import './App.css'

function AppContent() {
  const [activeTab, setActiveTab] = useState<'customer' | 'supervisor'>('customer')
  const [pendingCount, setPendingCount] = useState(0)
  const { theme, toggleTheme } = useTheme()

  useEffect(() => {
    fetchPendingCount()
    const interval = setInterval(fetchPendingCount, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchPendingCount = async () => {
    try {
      const response = await axios.get('/api/requests')
      const requests = response.data || []
      const pending = requests.filter((r: any) => r.status === 'pending').length
      setPendingCount(pending)
    } catch (error) {
      console.error('Error fetching pending requests:', error)
    }
  }

  return (
    <ToastProvider>
      <div className="app-container">
        <header className="app-header">
          <h1>🏥 FrontLoop - Salon Agent</h1>
          <div className="tab-switcher">
            <button
              className={`tab-btn ${activeTab === 'customer' ? 'active' : ''}`}
              onClick={() => setActiveTab('customer')}
            >
              Customer Chat
            </button>
            <button
              className={`tab-btn ${activeTab === 'supervisor' ? 'active' : ''}`}
              onClick={() => setActiveTab('supervisor')}
            >
              Supervisor Dashboard
              {pendingCount > 0 && (
                <span className="notification-badge">{pendingCount}</span>
              )}
            </button>
          </div>
          <button className="theme-toggle" onClick={toggleTheme} title="Toggle dark/light mode">
            {theme === 'light' ? <Moon size={24} /> : <Sun size={24} />}
          </button>
        </header>

        <main className="app-main">
          {activeTab === 'customer' && <CustomerChat />}
          {activeTab === 'supervisor' && <SupervisorDashboard onPendingCountChange={setPendingCount} />}
        </main>

        <ToastContainer />
      </div>
    </ToastProvider>
  )
}

export default function App() {
  return (
    <ThemeProvider>
      <ToastProvider>
        <AppContent />
        <ToastContainer />
      </ToastProvider>
    </ThemeProvider>
  )
}
