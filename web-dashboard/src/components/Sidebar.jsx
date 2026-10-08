import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import {
  ShieldAlert,
  Wifi,
  Activity,
  Smartphone,
  AlertTriangle,
  BarChart3,
  ShieldBan,
  Download,
} from 'lucide-react';
import { setActiveNetworkId } from '../store/slices/networkSlice';
import { setActiveTab, addToast } from '../store/slices/uiSlice';
import { api } from '../services/api';

export default function Sidebar() {
  const dispatch = useDispatch();
  const { networks, activeNetworkId, gatewayOnline } = useSelector(
    (state) => state.network
  );
  const { activeTab } = useSelector((state) => state.ui);
  const { devices } = useSelector((state) => state.devices);
  const { alerts } = useSelector((state) => state.threats);
  const activeThreatsCount = alerts.filter((a) => !a.is_resolved).length;

  const handleNetworkChange = (e) => {
    dispatch(setActiveNetworkId(e.target.value));
  };

  const handleExportCSV = () => {
    const url = api.getExportCsvUrl(activeNetworkId);
    window.open(url, '_blank');
    dispatch(
      addToast({ message: 'Exporting CSV audit log...', type: 'success' })
    );
  };

  return (
    <aside className="sidebar">
      {/* Brand Header */}
      <div className="brand-container">
        <div className="brand-logo">
          <ShieldAlert size={24} />
        </div>
        <div className="brand-text">
          <h2>NetSentry</h2>
          <span className="brand-tag">DNS CYBER INTELLIGENCE</span>
        </div>
      </div>

      {/* Network Selector */}
      <div className="network-selector-card">
        <label htmlFor="networkSelect">
          <Wifi size={14} /> ACTIVE NETWORK
        </label>
        <div className="select-wrapper">
          <select
            id="networkSelect"
            value={activeNetworkId}
            onChange={handleNetworkChange}
          >
            <option value="all">Global View (All Networks)</option>
            {networks.map((net) => (
              <option key={net.network_id} value={net.network_id}>
                {net.name} ({net.location})
              </option>
            ))}
          </select>
        </div>
        <div
          className={`network-status-badge ${gatewayOnline ? 'online' : ''}`}
        >
          <span className="pulse-dot" />
          <span>{gatewayOnline ? 'Gateway Connected (Live)' : 'Gateway Disconnected'}</span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="nav-links">
        <button
          className={`nav-btn ${activeTab === 'live-stream' ? 'active' : ''}`}
          onClick={() => dispatch(setActiveTab('live-stream'))}
        >
          <Activity size={18} />
          <span>Live DNS Stream</span>
          <span className="live-counter">LIVE</span>
        </button>

        <button
          className={`nav-btn ${activeTab === 'devices' ? 'active' : ''}`}
          onClick={() => dispatch(setActiveTab('devices'))}
        >
          <Smartphone size={18} />
          <span>Connected Devices</span>
          <span className="badge">{devices.length}</span>
        </button>

        <button
          className={`nav-btn ${activeTab === 'threats' ? 'active' : ''}`}
          onClick={() => dispatch(setActiveTab('threats'))}
        >
          <AlertTriangle size={18} />
          <span>Security Threats</span>
          <span className="badge danger">{activeThreatsCount}</span>
        </button>

        <button
          className={`nav-btn ${activeTab === 'analytics' ? 'active' : ''}`}
          onClick={() => dispatch(setActiveTab('analytics'))}
        >
          <BarChart3 size={18} />
          <span>Analytics & Trends</span>
        </button>

        <button
          className={`nav-btn ${activeTab === 'blocklist' ? 'active' : ''}`}
          onClick={() => dispatch(setActiveTab('blocklist'))}
        >
          <ShieldBan size={18} />
          <span>Domain Blocklist</span>
        </button>
      </nav>

      {/* Footer */}
      <div className="sidebar-footer">
        <div className="live-indicator">
          <span className="status-pulse" />
          <span>FastAPI & Redux Connected</span>
        </div>
        <button
          onClick={handleExportCSV}
          className="btn-secondary btn-sm btn-block"
        >
          <Download size={14} /> Export Logs CSV
        </button>
      </div>
    </aside>
  );
}
