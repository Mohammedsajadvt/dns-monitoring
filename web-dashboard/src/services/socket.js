import { API_BASE } from './api';
import { addLiveLog } from '../store/slices/logsSlice';
import { addLiveThreat } from '../store/slices/threatsSlice';
import { updateLiveDevice } from '../store/slices/devicesSlice';
import {
  incrementQueriesCount,
  incrementThreatCount,
  updateActiveDevicesCount,
} from '../store/slices/analyticsSlice';
import { setGatewayOnline } from '../store/slices/networkSlice';
import { addToast } from '../store/slices/uiSlice';

class WebSocketService {
  constructor() {
    this.ws = null;
    this.store = null;
    this.activeNetworkId = 'all';
    this.reconnectTimer = null;
    this.isExplicitClose = false;
  }

  init(store) {
    this.store = store;
  }

  connect(networkId = 'all') {
    this.activeNetworkId = networkId;
    this.isExplicitClose = false;

    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }

    if (this.ws) {
      this.isExplicitClose = true;
      try {
        this.ws.close();
      } catch (_) { }
    }

    const channel = networkId || 'all';
    let wsUrl;
    try {
      const url = new URL(API_BASE);
      const protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
      wsUrl = `${protocol}//${url.host}/ws/${channel}`;
    } catch {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      wsUrl = `${protocol}//${window.location.host}/ws/${channel}`;
    }

    try {
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        if (this.store) {
          this.store.dispatch(setGatewayOnline(true));
        }
      };

      this.ws.onmessage = (evt) => {
        try {
          const payload = JSON.parse(evt.data);
          if (!payload || !payload.event) return;

          const state = this.store ? this.store.getState() : null;
          const isStreaming = state?.logs?.isStreaming ?? true;

          if (payload.event === 'dns_query') {
            if (isStreaming && this.store) {
              this.store.dispatch(addLiveLog(payload.data));
              this.store.dispatch(incrementQueriesCount());
              if (payload.data.is_threat) {
                this.store.dispatch(incrementThreatCount());
              }
              // Dynamically ensure device is tracked if not already
              if (payload.data.client_ip) {
                this.store.dispatch(
                  updateLiveDevice({
                    network_id: payload.data.network_id,
                    ip: payload.data.client_ip,
                    mac: payload.data.client_mac || 'Unknown',
                    hostname: payload.data.client_name || payload.data.client_ip,
                    friendly_name: payload.data.client_name || payload.data.client_ip,
                    device_type: 'laptop',
                    last_seen: payload.data.timestamp,
                    is_online: true,
                    total_queries: 1,
                  })
                );
                const currentDevs = this.store.getState().devices?.devices?.length ?? 0;
                this.store.dispatch(updateActiveDevicesCount(currentDevs));
              }
            }
          } else if (payload.event === 'threat_alert') {
            if (this.store) {
              this.store.dispatch(addLiveThreat(payload.data));
              this.store.dispatch(
                addToast({
                  message: `THREAT BLOCKED: ${payload.data.domain} (${payload.data.threat_type})`,
                  type: 'threat',
                })
              );
            }
          } else if (payload.event === 'device_update') {
            if (this.store) {
              this.store.dispatch(updateLiveDevice(payload.data));
              const currentDevs = this.store.getState().devices?.devices?.length ?? 0;
              this.store.dispatch(updateActiveDevicesCount(currentDevs));
            }
          }
        } catch (e) {
          console.error('[WS Parse Error]:', e);
        }
      };

      this.ws.onclose = () => {
        if (this.store) {
          this.store.dispatch(setGatewayOnline(false));
        }
        if (!this.isExplicitClose) {
          this.reconnectTimer = setTimeout(() => {
            this.connect(this.activeNetworkId);
          }, 3000);
        }
      };

      this.ws.onerror = () => {
        if (this.store) {
          this.store.dispatch(setGatewayOnline(false));
        }
      };
    } catch (e) {
      console.error('[WS Connection Exception]:', e);
      if (this.store) {
        this.store.dispatch(setGatewayOnline(false));
      }
    }
  }

  disconnect() {
    this.isExplicitClose = true;
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.ws) {
      try {
        this.ws.close();
      } catch (_) { }
      this.ws = null;
    }
  }
}

export const socketService = new WebSocketService();
