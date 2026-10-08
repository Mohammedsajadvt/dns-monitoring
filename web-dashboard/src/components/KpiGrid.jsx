import React from 'react';
import { useSelector } from 'react-redux';
import { Globe, Smartphone, ShieldAlert, ShieldCheck } from 'lucide-react';

export default function KpiGrid() {
  const { stats } = useSelector((state) => state.analytics);

  const totalQueries = stats.total_queries_today ?? 0;
  const activeDevices = stats.active_devices_count ?? 0;
  const threatsBlocked = stats.threats_blocked_today ?? 0;

  return (
    <section className="kpi-grid">
      {/* Total Queries */}
      <div className="kpi-card">
        <div className="kpi-icon-wrap cyan">
          <Globe size={24} />
        </div>
        <div className="kpi-content">
          <span className="kpi-label">Queries Today</span>
          <h3 className="kpi-value">{totalQueries.toLocaleString()}</h3>
          <span className="kpi-sub">Across active gateways</span>
        </div>
      </div>

      {/* Active Devices */}
      <div className="kpi-card">
        <div className="kpi-icon-wrap purple">
          <Smartphone size={24} />
        </div>
        <div className="kpi-content">
          <span className="kpi-label">Active Devices</span>
          <h3 className="kpi-value">{activeDevices}</h3>
          <span className="kpi-sub">DHCP & ARP discovered</span>
        </div>
      </div>

      {/* Blocked Threats */}
      <div className="kpi-card">
        <div className="kpi-icon-wrap red">
          <ShieldAlert size={24} />
        </div>
        <div className="kpi-content">
          <span className="kpi-label">Threats Blocked</span>
          <h3 className="kpi-value" style={{ color: 'var(--accent-red)' }}>
            {threatsBlocked}
          </h3>
          <span className="kpi-sub">DGA, Mining & Phishing</span>
        </div>
      </div>

      {/* Policy Enforcement */}
      <div className="kpi-card">
        <div className="kpi-icon-wrap green">
          <ShieldCheck size={24} />
        </div>
        <div className="kpi-content">
          <span className="kpi-label">Security Policy</span>
          <h3 className="kpi-value" style={{ color: 'var(--accent-green)' }}>
            100%
          </h3>
          <span className="kpi-sub">Active Filter Coverage</span>
        </div>
      </div>
    </section>
  );
}
