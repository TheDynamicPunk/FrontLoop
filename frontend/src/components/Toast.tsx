import { AlertCircle, CheckCircle, X } from 'lucide-react'
import { useToast } from '../context/ToastContext'
import './Toast.css'

export function ToastContainer() {
  const { toasts, removeToast } = useToast()

  return (
    <div className="toast-container">
      {toasts.map(toast => (
        <div key={toast.id} className={`toast toast-${toast.type}`}>
          <div className="toast-icon">
            {toast.type === 'error' && <AlertCircle size={20} />}
            {toast.type === 'success' && <CheckCircle size={20} />}
          </div>
          <p className="toast-message">{toast.message}</p>
          <button className="toast-close" onClick={() => removeToast(toast.id)}>
            <X size={18} />
          </button>
        </div>
      ))}
    </div>
  )
}
