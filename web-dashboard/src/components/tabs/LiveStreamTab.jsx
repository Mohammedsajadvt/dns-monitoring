import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Search, RotateCcw, Pause, Play } from 'lucide-react';
import {
  toggleStreaming,
  setSearchFilter,
  setCategoryFilter,
  setThreatOnlyFilter,
  fetchLogs,
} from '../../store/slices/logsSlice';
import { addToast } from '../../store/slices/uiSlice';

export default function LiveStreamTab() {
  const dispatch = useDispatch();
  const {
    logs,
    isStreaming,
    searchFilter,
    categoryFilter,
    threatOnlyFilter,
    isLoading,
  } = useSelector((state) => state.logs);
  const { activeNetworkId } = useSelector((state) => state.network);

  const handleRefresh = () => {
    dispatch(fetchLogs({ networkId: activeNetworkId }));
    dispatch(addToast({ message: 'DNS logs refreshed', type: 'success' }));
  };

  const filteredLogs = logs.filter((log) => {
    const q = searchFilter.toLowerCase();
    const matchesSearch =
      !q ||
      log.domain?.toLowerCase().includes(q) ||
      log.client_ip?.toLowerCase().includes(q) ||
      log.client_name?.toLowerCase().includes(q);

    const matchesCategory =
      categoryFilter === 'all' ||
      log.category === categoryFilter ||
      (categoryFilter === 'Cryptomining' && log.threat_type === 'Cryptominer');

    const matchesThreat = !threatOnlyFilter || log.is_threat;

    return matchesSearch && matchesCategory && matchesThreat;
  });

  const getCategoryClass = (log) => {
    if (log.is_threat) return 'tag-category threat';
    if (log.category === 'Video Streaming') return 'tag-category streaming';
    if (log.category === 'Social Media') return 'tag-category social';
    if (log.category === 'Developer') return 'tag-category developer';
    if (log.category === 'Ads & Tracking') return 'tag-category ads';
    return 'tag-category';
  };

  const getActionPill = (log) => {
    if (log.action === 'BLOCKED' || log.is_threat) {
      return <span className="status-pill blocked">BLOCKED</span>;
    }
    if (log.action === 'CACHED') {
      return <span className="status-pill cached">CACHED</span>;
    }
    return <span className="status-pill forwarded">FORWARDED</span>;
  };

  return (
    <div className="tab-pane active">
      {/* Controls Bar */}
      <div className="controls-bar">
        <div className="search-box">
          <Search size={16} color="var(--accent-cyan)" />
          <input
            type="text"
            placeholder="Search domain, IP or client..."
            value={searchFilter}
            onChange={(e) => dispatch(setSearchFilter(e.target.value))}
          />
        </div>

        <div className="filter-group">
          <select
            value={categoryFilter}
            onChange={(e) => dispatch(setCategoryFilter(e.target.value))}
          >
            <option value="all">All Categories</option>
            <option value="Video Streaming">Video Streaming</option>
            <option value="Social Media">Social Media</option>
            <option value="Developer">Developer</option>
            <option value="Search & Cloud">Search & Cloud</option>
            <option value="Ads & Tracking">Ads & Tracking</option>
            <option value="Cryptomining">Cryptomining</option>
            <option value="Phishing">Phishing</option>
            <option value="Suspicious DGA">Suspicious DGA</option>
          </select>

          <select
            value={threatOnlyFilter ? 'threats' : 'all'}
            onChange={(e) =>
              dispatch(setThreatOnlyFilter(e.target.value === 'threats'))
            }
          >
            <option value="all">All Traffic</option>
            <option value="threats">Threats Only</option>
          </select>

          <button
            onClick={() => dispatch(toggleStreaming())}
            className={`btn-ghost btn-sm ${isStreaming ? 'active' : ''}`}
          >
            {isStreaming ? (
              <>
                <Pause size={14} /> STREAMING
              </>
            ) : (
              <>
                <Play size={14} /> PAUSED
              </>
            )}
          </button>

          <button onClick={handleRefresh} className="btn-secondary btn-sm">
            <RotateCcw size={14} /> Refresh
          </button>
        </div>
      </div>

      {/* Logs Table */}
      <div className="table-container" style={{ marginTop: '16px' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>TIMESTAMP</th>
              <th>CLIENT / DEVICE</th>
              <th>SOURCE IP</th>
              <th>QUERY DOMAIN</th>
              <th>CATEGORY / HEURISTIC</th>
              <th>TYPE</th>
              <th>LATENCY</th>
              <th>GATEWAY ACTION</th>
            </tr>
          </thead>
          <tbody>
            {isLoading && logs.length === 0 ? (
              <tr>
                <td colSpan="8" style={{ textAlign: 'center', padding: '30px' }}>
                  Loading DNS packet logs...
                </td>
              </tr>
            ) : filteredLogs.length === 0 ? (
              <tr>
                <td
                  colSpan="8"
                  style={{
                    textAlign: 'center',
                    padding: '40px',
                    color: 'var(--text-muted)',
                  }}
                >
                  No DNS queries matching current criteria.
                </td>
              </tr>
            ) : (
              filteredLogs.slice(0, 100).map((log, idx) => {
                const timeStr = new Date(log.timestamp).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                  second: '2-digit',
                });

                return (
                  <tr key={log.id || idx} className={log.is_threat ? 'threat-row' : ''}>
                    <td className="mono" style={{ color: 'var(--text-muted)' }}>
                      {timeStr}
                    </td>
                    <td>
                      <strong>{log.client_name || log.client_ip}</strong>
                    </td>
                    <td className="mono" style={{ color: 'var(--text-secondary)' }}>
                      {log.client_ip}
                    </td>
                    <td className={`domain-cell ${log.is_threat ? 'threat' : ''}`}>
                      {log.domain}
                    </td>
                    <td>
                      <span className={getCategoryClass(log)}>
                        {log.is_threat
                          ? log.threat_type || 'Malicious'
                          : log.category || 'General'}
                      </span>
                    </td>
                    <td>
                      <span className="mono" style={{ fontWeight: 700 }}>
                        {log.query_type || 'A'}
                      </span>
                    </td>
                    <td className="mono">
                      {log.response_time_ms
                        ? log.response_time_ms.toFixed(1)
                        : '12.0'}{' '}
                      ms
                    </td>
                    <td>{getActionPill(log)}</td>
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
