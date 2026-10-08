import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  Laptop,
  Smartphone,
  Tv,
  Cpu,
  Network,
  Edit3,
} from 'lucide-react';
import { openEditModal } from '../../store/slices/devicesSlice';

export default function DevicesTab() {
  const dispatch = useDispatch();
  const { devices, isLoading } = useSelector((state) => state.devices);

  const getDeviceIcon = (type) => {
    switch (type) {
      case 'phone':
        return <Smartphone size={20} />;
      case 'smart_tv':
        return <Tv size={20} />;
      case 'iot':
        return <Cpu size={20} />;
      case 'router':
        return <Network size={20} />;
      default:
        return <Laptop size={20} />;
    }
  };

  return (
    <div className="tab-pane active">
      {isLoading && devices.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
          Discovering network devices...
        </div>
      ) : devices.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
          No devices discovered on this network yet.
        </div>
      ) : (
        <div className="devices-grid">
          {devices.map((dev) => (
            <div key={dev.ip} className="device-card">
              <div className="device-card-top">
                <div className="device-icon-wrap">
                  {getDeviceIcon(dev.device_type)}
                </div>
                <span
                  className={`status-pill ${
                    dev.is_online ? 'forwarded' : ''
                  }`}
                >
                  {dev.is_online ? 'ONLINE' : 'OFFLINE'}
                </span>
              </div>

              <div className="device-title-area">
                <h4>{dev.friendly_name || dev.hostname || dev.ip}</h4>
                <span className="device-hostname">{dev.hostname}</span>
              </div>

              <div className="device-meta-row">
                <span className="device-meta-label">IP Address</span>
                <span className="mono">{dev.ip}</span>
              </div>

              <div className="device-meta-row">
                <span className="device-meta-label">MAC Address</span>
                <span className="mono">{dev.mac}</span>
              </div>

              <div className="device-meta-row">
                <span className="device-meta-label">Total Queries</span>
                <span className="mono" style={{ fontWeight: 700 }}>
                  {(dev.total_queries ?? 0).toLocaleString()}
                </span>
              </div>

              <div style={{ marginTop: '8px' }}>
                <button
                  onClick={() => dispatch(openEditModal(dev))}
                  className="btn-secondary btn-sm btn-block"
                >
                  <Edit3 size={14} /> Edit Alias & Type
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
