import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { AlertTriangle, CheckCircle, Info } from 'lucide-react';
import { removeToast } from '../store/slices/uiSlice';

function ToastItem({ toast }) {
  const dispatch = useDispatch();

  useEffect(() => {
    const timer = setTimeout(() => {
      dispatch(removeToast(toast.id));
    }, 4000);
    return () => clearTimeout(timer);
  }, [toast.id, dispatch]);

  const getIcon = () => {
    if (toast.type === 'threat') return <AlertTriangle size={16} color="#ef4444" />;
    if (toast.type === 'success') return <CheckCircle size={16} color="#10b981" />;
    return <Info size={16} color="#06b6d4" />;
  };

  return (
    <div className={`toast ${toast.type}`}>
      {getIcon()}
      <span>{toast.message}</span>
    </div>
  );
}

export default function ToastContainer() {
  const { toasts } = useSelector((state) => state.ui);

  if (toasts.length === 0) return null;

  return (
    <div className="toast-container">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} />
      ))}
    </div>
  );
}
