import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Zap, Play, LogOut, UserCircle } from 'lucide-react';
import { api } from '../services/api';
import { addToast } from '../store/slices/uiSlice';
import { logoutUser } from '../store/slices/authSlice';
import AuthModal from './auth/AuthModal';

const TAB_TITLES = {
  'live-stream': {
    title: 'Real-Time DNS Traffic Monitor',
    sub: 'Live deep-packet metadata, threat heuristics & device inspection',
  },
  devices: {
    title: 'Connected Devices & User Inventory',
    sub: 'Assign friendly device aliases, track online status & query footprint',
  },
  threats: {
    title: 'Threat Detection & Anomaly Center',
    sub: 'Shannon entropy DGA alarms, brand phishing and crypto-mining beacons',
  },
  analytics: {
    title: 'DNS Analytics & Traffic Insights',
    sub: 'Historical trends, volume distribution and category breakdowns',
  },
  blocklist: {
    title: 'Network Domain Blocklist',
    sub: 'Enforce gateway level domain blocking and policy filters',
  },
};

export default function Header() {
  const dispatch = useDispatch();
  const { activeTab } = useSelector((state) => state.ui);
  const { activeNetworkId } = useSelector((state) => state.network);
  const { user, isGuest } = useSelector((state) => state.auth);

  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

  const headerInfo = TAB_TITLES[activeTab] || TAB_TITLES['live-stream'];

  const handleSimulate = async (isThreat) => {
    try {
      const res = await api.triggerSimulation(activeNetworkId, isThreat);
      dispatch(
        addToast({
          message: isThreat
            ? `Threat Simulation Injected: ${res.domain}`
            : `Test Traffic Injected: ${res.domain}`,
          type: isThreat ? 'threat' : 'success',
        })
      );
    } catch (e) {
      dispatch(
        addToast({
          message: 'Simulation trigger failed: ' + e.message,
          type: 'threat',
        })
      );
    }
  };

  const handleSignOut = () => {
    dispatch(logoutUser());
    dispatch(
      addToast({
        message: 'Signed out of session',
        type: 'info',
      })
    );
  };

  const initials = user?.full_name
    ? user.full_name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2)
    : 'SA';

  return (
    <>
      <header className="top-header">
        <div className="header-left">
          <h1>{headerInfo.title}</h1>
          <p className="subtitle">{headerInfo.sub}</p>
        </div>

        <div className="header-right">
          {/* Simulation Triggers */}
          <button
            onClick={() => handleSimulate(true)}
            className="btn-ghost btn-sm"
            title="Simulate Threat Beacon"
          >
            <Zap size={15} color="#ef4444" /> Simulate Threat
          </button>
          <button
            onClick={() => handleSimulate(false)}
            className="btn-ghost btn-sm"
            title="Inject Test Benign Traffic"
          >
            <Play size={15} color="#06b6d4" /> Test Traffic
          </button>

          {/* User Profile Pill */}
          <div className="user-pill" style={{ position: 'relative' }}>
            <div className="avatar">{initials}</div>
            <div className="user-info">
              <span className="user-name">
                {user?.full_name || 'Administrator'}
              </span>
              <span className="user-role">
                {isGuest
                  ? 'Viewer Demo'
                  : (user?.role || 'admin').toUpperCase()}
              </span>
            </div>

            <button
              onClick={handleSignOut}
              className="btn-icon"
              title="Sign Out / Switch User"
              style={{
                marginLeft: '6px',
                padding: '4px',
                color: 'var(--text-muted)',
                cursor: 'pointer',
              }}
            >
              <LogOut size={15} />
            </button>
          </div>
        </div>
      </header>

      {/* Manual Auth Switcher Modal if opened */}
      {isAuthModalOpen && (
        <AuthModal
          isOpen={isAuthModalOpen}
          onClose={() => setIsAuthModalOpen(false)}
        />
      )}
    </>
  );
}
