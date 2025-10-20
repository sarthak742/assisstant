import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import ApiService from '../../services/api';

export const authenticate = createAsyncThunk(
  'security/authenticate',
  async (credentials, { rejectWithValue }) => {
    try {
      const response = await ApiService.authenticate(credentials);
      return response;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const initialState = {
  isAuthenticated: false,
  user: null,
  securityLevel: 'standard', // 'standard', 'high', 'custom'
  privacySettings: {
    dataRetention: 30, // days
    voiceDataStorage: true,
    locationTracking: false,
  },
  isLoading: false,
  error: null,
};

export const securitySlice = createSlice({
  name: 'security',
  initialState,
  reducers: {
    logout: (state) => {
      state.isAuthenticated = false;
      state.user = null;
    },
    setSecurityLevel: (state, action) => {
      state.securityLevel = action.payload;
    },
    updatePrivacySettings: (state, action) => {
      state.privacySettings = {
        ...state.privacySettings,
        ...action.payload,
      };
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(authenticate.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(authenticate.fulfilled, (state, action) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        state.user = action.payload.user;
      })
      .addCase(authenticate.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
        state.isAuthenticated = false;
      });
  },
});

export const { logout, setSecurityLevel, updatePrivacySettings } = securitySlice.actions;

export default securitySlice.reducer;