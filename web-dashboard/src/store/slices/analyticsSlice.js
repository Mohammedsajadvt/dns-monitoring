import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { api } from '../../services/api';

export const fetchAnalytics = createAsyncThunk(
  'analytics/fetchAnalytics',
  async (networkId = 'all', { rejectWithValue }) => {
    try {
      return await api.getAnalyticsSummary(networkId);
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

const analyticsSlice = createSlice({
  name: 'analytics',
  initialState: {
    stats: {
      total_queries_today: 0,
      active_devices_count: 0,
      threats_blocked_today: 0,
      top_domains: [],
      query_timeline: [],
      category_distribution: [],
    },
    isLoading: false,
    error: null,
  },
  reducers: {
    incrementQueriesCount(state) {
      state.stats.total_queries_today += 1;
    },
    incrementThreatCount(state) {
      state.stats.threats_blocked_today += 1;
    },
    updateActiveDevicesCount(state, action) {
      state.stats.active_devices_count = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchAnalytics.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchAnalytics.fulfilled, (state, action) => {
        state.isLoading = false;
        state.stats = action.payload;
      })
      .addCase(fetchAnalytics.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      });
  },
});

export const {
  incrementQueriesCount,
  incrementThreatCount,
  updateActiveDevicesCount,
} = analyticsSlice.actions;
export default analyticsSlice.reducer;
