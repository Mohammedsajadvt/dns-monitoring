import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { api } from '../../services/api';

export const fetchThreats = createAsyncThunk(
  'threats/fetchThreats',
  async (networkId = 'all', { rejectWithValue }) => {
    try {
      return await api.getThreatAlerts(networkId);
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

export const resolveThreat = createAsyncThunk(
  'threats/resolveThreat',
  async (alertId, { rejectWithValue }) => {
    try {
      await api.resolveThreat(alertId);
      return alertId;
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

const threatsSlice = createSlice({
  name: 'threats',
  initialState: {
    alerts: [],
    isLoading: false,
    error: null,
  },
  reducers: {
    addLiveThreat(state, action) {
      state.alerts.unshift(action.payload);
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchThreats.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchThreats.fulfilled, (state, action) => {
        state.isLoading = false;
        state.alerts = action.payload;
      })
      .addCase(fetchThreats.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      })
      .addCase(resolveThreat.fulfilled, (state, action) => {
        const alert = state.alerts.find((a) => a.id === action.payload);
        if (alert) {
          alert.is_resolved = true;
        }
      });
  },
});

export const { addLiveThreat } = threatsSlice.actions;
export default threatsSlice.reducer;
