import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { api } from '../../services/api';

export const fetchNetworks = createAsyncThunk(
  'network/fetchNetworks',
  async (_, { rejectWithValue }) => {
    try {
      return await api.getNetworks();
    } catch (err) {
      return rejectWithValue(err.message);
    }
  }
);

const networkSlice = createSlice({
  name: 'network',
  initialState: {
    networks: [],
    activeNetworkId: 'all',
    gatewayOnline: true,
    isLoading: false,
    error: null,
  },
  reducers: {
    setActiveNetworkId(state, action) {
      state.activeNetworkId = action.payload;
    },
    setGatewayOnline(state, action) {
      state.gatewayOnline = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchNetworks.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchNetworks.fulfilled, (state, action) => {
        state.isLoading = false;
        state.networks = action.payload;
      })
      .addCase(fetchNetworks.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      });
  },
});

export const { setActiveNetworkId, setGatewayOnline } = networkSlice.actions;
export default networkSlice.reducer;
