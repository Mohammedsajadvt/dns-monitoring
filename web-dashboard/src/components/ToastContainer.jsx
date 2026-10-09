import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  AlertTriangle,
  AlertCircle,
  CheckCircle,
  Info,
  X,
} from 'lucide-react';
import { removeToast } from '../store/slices/uiSlice';

function ToastItem({ toast }) {
  const dispatch = useDispatch();

  useEffect(() => {
    const timer = setTimeout(() => {
      dispatch(removeToast(toast.id));
    }, 4500);
    return () => clearTimeout(timer);
  }, [toast.id, dispatch]);

  const getIcon = () => {
    switch (toast.type) {
      case 'error':
        return <AlertCircle size={18} color="#ef4444" style={{ flexShrink: 0 }} />;
      case 'threat':
        return <AlertTriangle size={18} color="#f43f5e" style={{ flexShrink: 0 }} />;
      case 'warning':
        return <AlertTriangle size={18} color="#f59e0b" style={{ flexShrink: 0 }} />;
      case 'success':
        return <CheckCircle size={18} color="#10b981" style={{ flexShrink: 0 }} />;
      case 'info':
      default:
        return <Info size={18} color="#06b6d4" style={{ flexShrink: 0 }} />;
    }
  };

  return (
    <div className={`toast ${toast.type || 'info'}`}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flex: 1 }}>
        {getIcon()}
        <span style={{ lineHeight: '1.4' }}>{toast.message}</span>
      </div>
      <button
        type="button"
        onClick={() => dispatch(removeToast(toast.id))}
        style={{
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          padding: '2px',
          color: 'rgba(255, 255, 255, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          borderRadius: '4px',
          transition: 'color 0.2s',
        }}
        aria-label="Dismiss toast"
      >
        <X size={14} />
      </button>
    </div>
  );
}

export default function ToastContainer() {
  const { toasts } = useSelector((state) => state.ui);

  if (!toasts || toasts.length === 0) return null;

  return (
    <div className="toast-container">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} />
      ))}
    </div>
  );
}
