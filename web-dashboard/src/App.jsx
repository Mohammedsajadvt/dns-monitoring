import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import KpiGrid from './components/KpiGrid';
import ToastContainer from './components/ToastContainer';
import EditDeviceModal from './components/modals/EditDeviceModal';
import AuthModal from './components/auth/AuthModal';

import LiveStreamTab from './components/tabs/LiveStreamTab';
import DevicesTab from './components/tabs/DevicesTab';
import ThreatsTab from './components/tabs/ThreatsTab';
import AnalyticsTab from './components/tabs/AnalyticsTab';
import BlocklistTab from './components/tabs/BlocklistTab';

import { fetchNetworks } from './store/slices/networkSlice';
import { fetchLogs } from './store/slices/logsSlice';
import { fetchDevices } from './store/slices/devicesSlice';
import { fetchThreats } from './store/slices/threatsSlice';
import { fetchAnalytics } from './store/slices/analyticsSlice';
import { fetchBlocklist } from './store/slices/blocklistSlice';
import { socketService } from './services/socket';

export default function App() {
  const dispatch = useDispatch();
  const { activeNetworkId } = useSelector((state) => state.network);
  const { activeTab } = useSelector((state) => state.ui);
  const { isAuthenticated } = useSelector((state) => state.auth);

  // Initial load of networks
  useEffect(() => {
    if (isAuthenticated) {
      dispatch(fetchNetworks());
    }
  }, [dispatch, isAuthenticated]);

  // Load dynamic telemetry whenever network or auth state changes
  useEffect(() => {
    if (isAuthenticated) {
      dispatch(fetchLogs({ networkId: activeNetworkId }));
      dispatch(fetchDevices(activeNetworkId));
      dispatch(fetchThreats(activeNetworkId));
      dispatch(fetchAnalytics(activeNetworkId));
      dispatch(fetchBlocklist(activeNetworkId));

      socketService.connect(activeNetworkId);
    } else {
      socketService.disconnect();
    }
  }, [dispatch, activeNetworkId, isAuthenticated]);

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'devices':
        return <DevicesTab />;
      case 'threats':
        return <ThreatsTab />;
      case 'analytics':
        return <AnalyticsTab />;
      case 'blocklist':
        return <BlocklistTab />;
      case 'live-stream':
      default:
        return <LiveStreamTab />;
    }
  };

  return (
    <>
      {/* Background ambient lighting */}
      <div className="glow-orb glow-top-left" />
      <div className="glow-orb glow-bottom-right" />

      {/* Auth Screen / Gate if not logged in */}
      {!isAuthenticated && <AuthModal isOpen={true} isRequired={true} />}

      {/* Dashboard View */}
      {isAuthenticated && (
        <div className="app-layout">
          {/* Left Sidebar */}
          <Sidebar />

          {/* Main Content Viewport */}
          <main className="main-content">
            <Header />
            <KpiGrid />
            {renderActiveTab()}
          </main>
        </div>
      )}

      {/* Global Modals & Notifications */}
      <EditDeviceModal />
      <ToastContainer />
    </>
  );
}
