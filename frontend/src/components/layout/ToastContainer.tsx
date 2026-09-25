import React from 'react';
import { useToast, type ToastType } from '../../context/ToastContext';

const ICONS: Record<ToastType, string> = {
  info: 'ℹ',
  success: '✓',
  warning: '⚠',
  error: '✕',
};

export const ToastContainer: React.FC = () => {
  const { toasts, removeToast } = useToast();

  if (toasts.length === 0) return null;

  return (
    <div className="toast-portal-container">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`toast-item toast-${toast.type}`}
          role="alert"
        >
          <div className="toast-icon-wrap">
            <span className="toast-type-icon">{ICONS[toast.type]}</span>
          </div>
          <div className="toast-body">
            <div className="toast-title">{toast.title}</div>
            {toast.message && (
              <div className="toast-message">{toast.message}</div>
            )}
          </div>
          <button
            className="toast-close-btn"
            onClick={() => removeToast(toast.id)}
            aria-label="Dismiss Notification"
          >
            ✕
          </button>
        </div>
      ))}
    </div>
  );
};
