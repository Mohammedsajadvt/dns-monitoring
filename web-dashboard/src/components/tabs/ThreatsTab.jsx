import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { ShieldAlert, ShieldCheck, CheckCircle } from 'lucide-react';
import { resolveThreat } from '../../store/slices/threatsSlice';
import { addToast } from '../../store/slices/uiSlice';

export default function ThreatsTab() {
  const dispatch = useDispatch();
  const { alerts, isLoading } = useSelector((state) => state.threats);

  const handleResolve = async (alertId) => {
    try {
      await dispatch(resolveThreat(alertId)).unwrap();
      dispatch(
        addToast({ message: 'Threat alert marked as resolved', type: 'success' })
      );
    } catch (e) {
      dispatch(
        addToast({ message: 'Failed to resolve alert: ' + e, type: 'threat' })
      );
    }
  };

  return (
    <div className="tab-pane active">
      {isLoading && alerts.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
          Scanning threat telemetry...
        </div>
      ) : alerts.length === 0 ? (
        <div
          style={{
            textAlign: 'center',
            padding: '60px 20px',
            color: 'var(--text-muted)',
            background: 'var(--bg-surface)',
            borderRadius: 'var(--radius-lg)',
            border: '1px solid var(--border-subtle)',
          }}
        >
          <ShieldCheck size={52} color="var(--accent-green)" />
          <h3 style={{ color: '#fff', marginTop: '14px', fontSize: '1.2rem' }}>
            No Active Security Threats
          </h3>
          <p style={{ marginTop: '6px', fontSize: '0.85rem' }}>
            All DNS queries within security baseline policy. Network is clean.
          </p>
        </div>
      ) : (
        <div className="threats-list">
          {alerts.map((alert) => {
            const timeStr = new Date(alert.timestamp).toLocaleString();

            return (
              <div key={alert.id} className="threat-card">
                <div className="threat-main">
                  <div className="threat-icon">
                    <ShieldAlert size={24} />
                  </div>
                  <div className="threat-info">
                    <h4>{alert.domain}</h4>
                    <div className="threat-details">
                      <strong style={{ color: 'var(--accent-red)' }}>
                        {alert.threat_type}
                      </strong>{' '}
                      | Source:{' '}
                      <span className="mono">
                        {alert.client_name} ({alert.client_ip})
                      </span>{' '}
                      | Time: {timeStr}
                    </div>
                    <p
                      style={{
                        fontSize: '0.78rem',
                        color: 'var(--text-muted)',
                        marginTop: '4px',
                      }}
                    >
                      {alert.details}
                    </p>
                  </div>
                </div>

                <div>
                  {alert.is_resolved ? (
                    <span className="status-pill forwarded">RESOLVED</span>
                  ) : (
                    <button
                      onClick={() => handleResolve(alert.id)}
                      className="btn-secondary btn-sm"
                    >
                      <CheckCircle size={14} color="var(--accent-green)" /> Mark Resolved
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
