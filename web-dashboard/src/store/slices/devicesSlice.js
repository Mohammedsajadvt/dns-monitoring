import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { api } from '../../services/api';

export const fetchDevices = createAsyncThunk(
  'devices/fetchDevices',
  async (networkId = 'all', { rejectWithValue }) => {
    try {
      return await api.getDevices(networkId);
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

export const updateDevice = createAsyncThunk(
  'devices/updateDevice',
  async ({ networkId, ip, friendlyName, deviceType }, { rejectWithValue }) => {
    try {
      await api.updateDevice(networkId, ip, friendlyName, deviceType);
      return { networkId, ip, friendlyName, deviceType };
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

const devicesSlice = createSlice({
  name: 'devices',
  initialState: {
    devices: [],
    selectedDevice: null,
    isModalOpen: false,
    isLoading: false,
    error: null,
  },
  reducers: {
    openEditModal(state, action) {
      state.selectedDevice = action.payload;
      state.isModalOpen = true;
    },
    closeEditModal(state) {
      state.selectedDevice = null;
      state.isModalOpen = false;
    },
    updateLiveDevice(state, action) {
      const updated = action.payload;
      const idx = state.devices.indexWhere?.((d) => d.ip === updated.ip) ??
        state.devices.findIndex((d) => d.ip === updated.ip);
      if (idx >= 0) {
        state.devices[idx] = { ...state.devices[idx], ...updated };
      } else {
        state.devices.unshift(updated);
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchDevices.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchDevices.fulfilled, (state, action) => {
        state.isLoading = false;
        state.devices = action.payload;
      })
      .addCase(fetchDevices.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      })
      .addCase(updateDevice.fulfilled, (state, action) => {
        const { ip, friendlyName, deviceType } = action.payload;
        const dev = state.devices.find((d) => d.ip === ip);
        if (dev) {
          dev.friendly_name = friendlyName;
          dev.device_type = deviceType;
        }
        state.isModalOpen = false;
        state.selectedDevice = null;
      });
  },
});

export const { openEditModal, closeEditModal, updateLiveDevice } = devicesSlice.actions;
export default devicesSlice.reducer;
