import { createSlice } from '@reduxjs/toolkit';

let toastIdCounter = 0;

const uiSlice = createSlice({
  name: 'ui',
  initialState: {
    activeTab: 'live-stream',
    toasts: [],
  },
  reducers: {
    setActiveTab(state, action) {
      state.activeTab = action.payload;
    },
    addToast: {
      reducer(state, action) {
        state.toasts.push(action.payload);
      },
      prepare({ message, type = 'info' }) {
        return {
          payload: {
            id: ++toastIdCounter,
            message,
            type,
          },
        };
      },
    },
    removeToast(state, action) {
      state.toasts = state.toasts.filter((t) => t.id !== action.payload);
    },
  },
});

export const { setActiveTab, addToast, removeToast } = uiSlice.actions;
export default uiSlice.reducer;
