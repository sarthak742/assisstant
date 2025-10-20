import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import ApiService from '../../services/api';

export const checkForUpdates = createAsyncThunk(
  'update/checkForUpdates',
  async (_, { rejectWithValue }) => {
    try {
      const response = await ApiService.checkForUpdates();
      return response;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const getVersionInfo = createAsyncThunk(
  'update/getVersionInfo',
  async (_, { rejectWithValue }) => {
    try {
      const response = await ApiService.getVersionInfo();
      return response;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const initialState = {
  currentVersion: null,
  latestVersion: null,
  updateAvailable: false,
  updateStatus: 'idle', // 'idle', 'checking', 'downloading', 'installing', 'complete', 'error'
  updateProgress: 0,
  updateDetails: null,
  isLoading: false,
  error: null,
};

export const updateSlice = createSlice({
  name: 'update',
  initialState,
  reducers: {
    setUpdateStatus: (state, action) => {
      state.updateStatus = action.payload;
    },
    setUpdateProgress: (state, action) => {
      state.updateProgress = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(checkForUpdates.pending, (state) => {
        state.isLoading = true;
        state.updateStatus = 'checking';
        state.error = null;
      })
      .addCase(checkForUpdates.fulfilled, (state, action) => {
        state.isLoading = false;
        state.updateStatus = 'idle';
        state.updateAvailable = action.payload.updateAvailable;
        state.latestVersion = action.payload.latestVersion;
        state.updateDetails = action.payload.details;
      })
      .addCase(checkForUpdates.rejected, (state, action) => {
        state.isLoading = false;
        state.updateStatus = 'error';
        state.error = action.payload;
      })
      .addCase(getVersionInfo.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(getVersionInfo.fulfilled, (state, action) => {
        state.isLoading = false;
        state.currentVersion = action.payload.currentVersion;
        state.latestVersion = action.payload.latestVersion;
        state.updateAvailable = action.payload.updateAvailable;
      })
      .addCase(getVersionInfo.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      });
  },
});

export const { setUpdateStatus, setUpdateProgress } = updateSlice.actions;

export default updateSlice.reducer;