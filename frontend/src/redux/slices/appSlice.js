import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  isConnected: false,
  connectionStatus: 'disconnected', // 'disconnected', 'connecting', 'connected', 'error'
  isVoiceActive: false,
  isListening: false,
  theme: 'dark', // 'dark', 'light', 'blue', 'teal', 'violet'
  activePanel: 'chat', // 'chat', 'memory', 'context', 'update', 'security', 'logs'
  isOffline: false,
  error: null,
  notifications: [],
};

export const appSlice = createSlice({
  name: 'app',
  initialState,
  reducers: {
    setConnectionStatus: (state, action) => {
      state.connectionStatus = action.payload;
      state.isConnected = action.payload === 'connected';
    },
    setVoiceActive: (state, action) => {
      state.isVoiceActive = action.payload;
    },
    setListening: (state, action) => {
      state.isListening = action.payload;
    },
    setTheme: (state, action) => {
      state.theme = action.payload;
    },
    setActivePanel: (state, action) => {
      state.activePanel = action.payload;
    },
    setOfflineStatus: (state, action) => {
      state.isOffline = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
    addNotification: (state, action) => {
      state.notifications.push({
        id: Date.now(),
        ...action.payload,
      });
      // Keep only the last 10 notifications
      if (state.notifications.length > 10) {
        state.notifications.shift();
      }
    },
    clearNotification: (state, action) => {
      state.notifications = state.notifications.filter(
        (notification) => notification.id !== action.payload
      );
    },
    clearAllNotifications: (state) => {
      state.notifications = [];
    },
  },
});

export const {
  setConnectionStatus,
  setVoiceActive,
  setListening,
  setTheme,
  setActivePanel,
  setOfflineStatus,
  setError,
  addNotification,
  clearNotification,
  clearAllNotifications,
} = appSlice.actions;

export default appSlice.reducer;