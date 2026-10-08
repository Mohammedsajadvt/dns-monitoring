import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import networkReducer from './slices/networkSlice';
import logsReducer from './slices/logsSlice';
import devicesReducer from './slices/devicesSlice';
import threatsReducer from './slices/threatsSlice';
import analyticsReducer from './slices/analyticsSlice';
import blocklistReducer from './slices/blocklistSlice';
import uiReducer from './slices/uiSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    network: networkReducer,
    logs: logsReducer,
    devices: devicesReducer,
    threats: threatsReducer,
    analytics: analyticsReducer,
    blocklist: blocklistReducer,
    ui: uiReducer,
  },
});
