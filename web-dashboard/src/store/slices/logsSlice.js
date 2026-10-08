import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { api } from '../../services/api';

export const fetchLogs = createAsyncThunk(
  'logs/fetchLogs',
  async ({ networkId = 'all', limit = 100 } = {}, { rejectWithValue }) => {
    try {
      return await api.getLogs(networkId, limit);
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

const logsSlice = createSlice({
  name: 'logs',
  initialState: {
    logs: [],
    isStreaming: true,
    categoryFilter: 'all',
    searchFilter: '',
    threatOnlyFilter: false,
    isLoading: false,
    error: null,
  },
  reducers: {
    addLiveLog(state, action) {
      state.logs.unshift(action.payload);
      if (state.logs.length > 300) {
        state.logs.pop();
      }
    },
    toggleStreaming(state) {
      state.isStreaming = !state.isStreaming;
    },
    setCategoryFilter(state, action) {
      state.categoryFilter = action.payload;
    },
    setSearchFilter(state, action) {
      state.searchFilter = action.payload;
    },
    setThreatOnlyFilter(state, action) {
      state.threatOnlyFilter = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchLogs.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchLogs.fulfilled, (state, action) => {
        state.isLoading = false;
        state.logs = action.payload;
      })
      .addCase(fetchLogs.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      });
  },
});

export const {
  addLiveLog,
  toggleStreaming,
  setCategoryFilter,
  setSearchFilter,
  setThreatOnlyFilter,
} = logsSlice.actions;

export default logsSlice.reducer;
