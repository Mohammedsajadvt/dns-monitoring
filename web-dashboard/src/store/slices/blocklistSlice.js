import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { api } from '../../services/api';

export const fetchBlocklist = createAsyncThunk(
  'blocklist/fetchBlocklist',
  async (networkId = 'all', { rejectWithValue }) => {
    try {
      return await api.getBlocklist(networkId);
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

export const addBlockedDomain = createAsyncThunk(
  'blocklist/addBlockedDomain',
  async ({ networkId, domain, reason }, { rejectWithValue }) => {
    try {
      await api.addBlockedDomain(networkId, domain, reason);
      return {
        domain,
        network_id: networkId === 'all' ? 'net_home_01' : networkId,
        reason: reason || 'Administrative policy',
        added_at: new Date().toISOString(),
      };
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

export const removeBlockedDomain = createAsyncThunk(
  'blocklist/removeBlockedDomain',
  async ({ networkId, domain }, { rejectWithValue }) => {
    try {
      await api.removeBlockedDomain(networkId, domain);
      return domain;
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

const blocklistSlice = createSlice({
  name: 'blocklist',
  initialState: {
    items: [],
    isLoading: false,
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchBlocklist.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchBlocklist.fulfilled, (state, action) => {
        state.isLoading = false;
        state.items = action.payload;
      })
      .addCase(fetchBlocklist.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      })
      .addCase(addBlockedDomain.fulfilled, (state, action) => {
        state.items.unshift(action.payload);
      })
      .addCase(removeBlockedDomain.fulfilled, (state, action) => {
        state.items = state.items.filter((i) => i.domain !== action.payload);
      });
  },
});

export default blocklistSlice.reducer;
