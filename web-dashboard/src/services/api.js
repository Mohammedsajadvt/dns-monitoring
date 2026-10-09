export const API_BASE = import.meta.env.VITE_API_BASE || 'https://dns-monitoring.onrender.com';

const getHeaders = (extraHeaders = {}) => {
  const headers = {
    'Content-Type': 'application/json',
    ...extraHeaders,
  };
  const token = localStorage.getItem('netsentry_token');
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
};

export const api = {
  // --- Auth Endpoints ---
  login: async (email, password) => {
    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email: email.trim().toLowerCase(),
        password,
      }),
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'Login failed');
    }
    return data;
  },

  register: async (fullName, email, password) => {
    const res = await fetch(`${API_BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        full_name: fullName.trim(),
        email: email.trim().toLowerCase(),
        password,
        role: 'admin',
      }),
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || 'Registration failed');
    }
    return data;
  },

  getMe: async () => {
    const res = await fetch(`${API_BASE}/api/auth/me`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to get user session');
    return res.json();
  },

  // --- Core Dynamic Endpoints ---
  getNetworks: async () => {
    const res = await fetch(`${API_BASE}/api/networks`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch networks');
    return res.json();
  },

  autoDetectNetwork: async () => {
    const res = await fetch(`${API_BASE}/api/networks/auto-detect`, {
      method: 'POST',
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to auto-detect network');
    return res.json();
  },

  getAnalyticsSummary: async (networkId = 'all') => {
    const query =
      networkId && networkId !== 'all' ? `?network_id=${networkId}` : '';
    const res = await fetch(`${API_BASE}/api/analytics/summary${query}`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch analytics');
    return res.json();
  },

  getLogs: async (networkId = 'all', limit = 100) => {
    const query =
      networkId && networkId !== 'all'
        ? `?network_id=${networkId}&limit=${limit}`
        : `?limit=${limit}`;
    const res = await fetch(`${API_BASE}/api/logs${query}`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch logs');
    return res.json();
  },

  getDevices: async (networkId = 'all') => {
    const query =
      networkId && networkId !== 'all' ? `?network_id=${networkId}` : '';
    const res = await fetch(`${API_BASE}/api/devices${query}`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch devices');
    return res.json();
  },

  updateDevice: async (networkId, ip, friendlyName, deviceType) => {
    const res = await fetch(`${API_BASE}/api/devices/${networkId}/${ip}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify({
        friendly_name: friendlyName,
        device_type: deviceType,
      }),
    });
    if (!res.ok) throw new Error('Failed to update device');
    return res.json();
  },

  getThreatAlerts: async (networkId = 'all') => {
    const query =
      networkId && networkId !== 'all' ? `?network_id=${networkId}` : '';
    const res = await fetch(`${API_BASE}/api/threats/alerts${query}`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch threat alerts');
    return res.json();
  },

  resolveThreat: async (alertId) => {
    const res = await fetch(
      `${API_BASE}/api/threats/alerts/${alertId}/resolve`,
      {
        method: 'POST',
        headers: getHeaders(),
      }
    );
    if (!res.ok) throw new Error('Failed to resolve threat');
    return res.json();
  },

  getBlocklist: async (networkId = 'all') => {
    const query =
      networkId && networkId !== 'all' ? `?network_id=${networkId}` : '';
    const res = await fetch(`${API_BASE}/api/threats/blocklist${query}`, {
      headers: getHeaders(),
    });
    if (!res.ok) throw new Error('Failed to fetch blocklist');
    return res.json();
  },

  addBlockedDomain: async (networkId, domain, reason) => {
    const res = await fetch(`${API_BASE}/api/threats/blocklist`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({
        network_id: networkId === 'all' ? 'net_home_01' : networkId,
        domain,
        reason: reason || 'Administrative policy',
      }),
    });
    if (!res.ok) throw new Error('Failed to add blocked domain');
    return res.json();
  },

  removeBlockedDomain: async (networkId, domain) => {
    const res = await fetch(
      `${API_BASE}/api/threats/blocklist/${networkId}/${domain}`,
      {
        method: 'DELETE',
        headers: getHeaders(),
      }
    );
    if (!res.ok) throw new Error('Failed to remove blocked domain');
    return res.json();
  },

  triggerSimulation: async (networkId, isThreat) => {
    const sampleDomains = isThreat
      ? [
        'coinhive.com',
        'paypa1-security-verify.com',
        'x78q3948u32kalsdkf.biz',
        'crypto-webminer.xyz',
      ]
      : [
        'youtube.com',
        'github.com',
        'instagram.com',
        'wikipedia.org',
        'netflix.com',
        'whatsapp.com',
      ];

    const domain =
      sampleDomains[Math.floor(Math.random() * sampleDomains.length)];
    let netId = networkId;
    if (netId === 'all' || !netId) {
      try {
        const nets = await api.getNetworks();
        netId = nets.length > 0 ? nets[0].network_id : 'net_default_primary';
      } catch {
        netId = 'net_default_primary';
      }
    }

    const payload = {
      network_id: netId,
      gateway_id: 'gw_home_router',
      client_ip: '192.168.1.120',
      client_mac: 'B4:2E:99:C1:88:41',
      client_hostname: 'MacBook-Pro-M2',
      domain: domain,
      query_type: 'A',
      response_code: 'NOERROR',
      response_ips: ['142.250.190.46'],
      response_time_ms: Math.random() * 20 + 5,
      action: isThreat ? 'BLOCKED' : 'FORWARDED',
    };

    const res = await fetch(`${API_BASE}/api/logs/ingest`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to trigger simulation');
    return { isThreat, domain };
  },

  getExportCsvUrl: (networkId = 'all') => {
    const query =
      networkId && networkId !== 'all' ? `?network_id=${networkId}` : '';
    return `${API_BASE}/api/export/csv${query}`;
  },
};
