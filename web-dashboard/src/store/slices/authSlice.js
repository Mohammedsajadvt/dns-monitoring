import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { api } from '../../services/api';

const savedToken = localStorage.getItem('netsentry_token');
let savedUser = null;
try {
  const userStr = localStorage.getItem('netsentry_user');
  if (userStr) savedUser = JSON.parse(userStr);
} catch (_) {}

export const loginUser = createAsyncThunk(
  'auth/loginUser',
  async ({ email, password }, { rejectWithValue }) => {
    try {
      const data = await api.login(email, password);
      localStorage.setItem('netsentry_token', data.access_token);
      localStorage.setItem('netsentry_user', JSON.stringify(data.user));
      return data;
    } catch (err) {
      return rejectWithValue(err.message || 'Login failed');
    }
  }
);

export const registerUser = createAsyncThunk(
  'auth/registerUser',
  async ({ fullName, email, password }, { rejectWithValue }) => {
    try {
      const data = await api.register(fullName, email, password);
      localStorage.setItem('netsentry_token', data.access_token);
      localStorage.setItem('netsentry_user', JSON.stringify(data.user));
      return data;
    } catch (err) {
      return rejectWithValue(err.message || 'Registration failed');
    }
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    token: savedToken || null,
    user: savedUser || null,
    isAuthenticated: !!savedToken || localStorage.getItem('netsentry_guest') === 'true',
    isGuest: localStorage.getItem('netsentry_guest') === 'true',
    isLoading: false,
    error: null,
  },
  reducers: {
    loginAsGuest(state) {
      state.token = null;
      state.user = {
        id: 'guest_viewer',
        email: 'guest@netsentry.io',
        full_name: 'SecOps Guest',
        role: 'viewer',
        created_at: new Date().toISOString(),
      };
      state.isAuthenticated = true;
      state.isGuest = true;
      state.error = null;
      localStorage.removeItem('netsentry_token');
      localStorage.setItem('netsentry_guest', 'true');
      localStorage.setItem('netsentry_user', JSON.stringify(state.user));
    },
    logoutUser(state) {
      state.token = null;
      state.user = null;
      state.isAuthenticated = false;
      state.isGuest = false;
      state.error = null;
      localStorage.removeItem('netsentry_token');
      localStorage.removeItem('netsentry_guest');
      localStorage.removeItem('netsentry_user');
    },
    clearAuthError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(loginUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.token = action.payload.access_token;
        state.user = action.payload.user;
        state.isAuthenticated = true;
        state.isGuest = false;
        localStorage.removeItem('netsentry_guest');
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      })
      // Register
      .addCase(registerUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(registerUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.token = action.payload.access_token;
        state.user = action.payload.user;
        state.isAuthenticated = true;
        state.isGuest = false;
        localStorage.removeItem('netsentry_guest');
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      });
  },
});

export const { loginAsGuest, logoutUser, clearAuthError } = authSlice.actions;
export default authSlice.reducer;
