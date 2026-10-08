import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { ShieldBan, Plus, Trash2 } from 'lucide-react';
import {
  addBlockedDomain,
  removeBlockedDomain,
} from '../../store/slices/blocklistSlice';
import { addToast } from '../../store/slices/uiSlice';

export default function BlocklistTab() {
  const dispatch = useDispatch();
  const { items, isLoading } = useSelector((state) => state.blocklist);
  const { activeNetworkId } = useSelector((state) => state.network);

  const [domain, setDomain] = useState('');
  const [reason, setReason] = useState('');

  const handleAdd = async (e) => {
    e.preventDefault();
    if (!domain.trim()) return;

    try {
      await dispatch(
        addBlockedDomain({
          networkId: activeNetworkId,
          domain: domain.trim(),
          reason: reason.trim(),
        })
      ).unwrap();

      dispatch(
        addToast({
          message: `Domain ${domain.trim()} added to blocklist`,
          type: 'success',
        })
      );
      setDomain('');
      setReason('');
    } catch (err) {
      dispatch(
        addToast({
          message: 'Failed to add domain to blocklist: ' + err,
          type: 'threat',
        })
      );
    }
  };

  const handleRemove = async (domainToRemove) => {
    try {
      await dispatch(
        removeBlockedDomain({
          networkId: activeNetworkId,
          domain: domainToRemove,
        })
      ).unwrap();

      dispatch(
        addToast({
          message: `Removed ${domainToRemove} from blocklist`,
          type: 'success',
        })
      );
    } catch (err) {
      dispatch(
        addToast({
          message: 'Failed to remove domain: ' + err,
          type: 'threat',
        })
      );
    }
  };

  return (
    <div className="tab-pane active" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Add New Rule Card */}
      <div className="chart-card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <ShieldBan size={22} color="var(--accent-red)" />
          <h3>Enforce Gateway Domain Block Rule</h3>
        </div>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
          DNS queries matching blocked domains will receive immediate NXDOMAIN / Sinkhole responses at the gateway.
        </p>

        <form
          onSubmit={handleAdd}
          style={{
            display: 'flex',
            gap: '12px',
            alignItems: 'flex-end',
            flexWrap: 'wrap',
          }}
        >
          <div className="form-group" style={{ flex: '2', minWidth: '240px' }}>
            <label>Domain to Block (FQDN)</label>
            <input
              type="text"
              placeholder="e.g. adserver.tracking-malicious.com"
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              required
            />
          </div>

          <div className="form-group" style={{ flex: '2', minWidth: '240px' }}>
            <label>Policy Reason / Classification</label>
            <input
              type="text"
              placeholder="e.g. Telemetry / Cryptomining / Phishing"
              value={reason}
              onChange={(e) => setReason(e.target.value)}
            />
          </div>

          <button
            type="submit"
            className="btn-primary"
            style={{ height: '42px', padding: '0 20px' }}
          >
            <Plus size={16} /> Add Rule
          </button>
        </form>
      </div>

      {/* Blocklist Table */}
      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>BLOCKED DOMAIN</th>
              <th>POLICY REASON</th>
              <th>NETWORK ID</th>
              <th>DATE ENFORCED</th>
              <th>ACTION</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && items.length === 0 ? (
              <tr>
                <td colSpan="5" style={{ textAlign: 'center', padding: '30px' }}>
                  Loading blocklist rules...
                </td>
              </tr>
            ) : items.length === 0 ? (
              <tr>
                <td
                  colSpan="5"
                  style={{
                    textAlign: 'center',
                    padding: '40px',
                    color: 'var(--text-muted)',
                  }}
                >
                  No domain blocking rules enforced on this network.
                </td>
              </tr>
            ) : (
              items.map((item, idx) => {
                const dateStr = item.added_at
                  ? new Date(item.added_at).toLocaleDateString()
                  : 'Active';

                return (
                  <tr key={item.domain || idx}>
                    <td className="domain-cell threat">{item.domain}</td>
                    <td>{item.reason || 'Manual Policy'}</td>
                    <td className="mono" style={{ color: 'var(--text-secondary)' }}>
                      {item.network_id || activeNetworkId}
                    </td>
                    <td className="mono" style={{ color: 'var(--text-muted)' }}>
                      {dateStr}
                    </td>
                    <td>
                      <button
                        onClick={() => handleRemove(item.domain)}
                        className="btn-ghost btn-sm"
                        style={{ color: 'var(--accent-red)' }}
                      >
                        <Trash2 size={14} /> Remove
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
