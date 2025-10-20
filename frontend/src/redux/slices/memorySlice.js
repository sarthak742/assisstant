import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import ApiService from '../../services/api';

export const fetchRecentInteractions = createAsyncThunk(
  'memory/fetchRecentInteractions',
  async (count = 15, { rejectWithValue }) => {
    try {
      const response = await ApiService.getRecentInteractions(count);
      return response;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const fetchContext = createAsyncThunk(
  'memory/fetchContext',
  async (_, { rejectWithValue }) => {
    try {
      const response = await ApiService.getContext();
      return response;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const initialState = {
  interactions: [],
  context: {},
  isLoading: false,
  error: null,
};

export const memorySlice = createSlice({
  name: 'memory',
  initialState,
  reducers: {
    clearMemory: (state) => {
      state.interactions = [];
    },
    clearContext: (state) => {
      state.context = {};
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchRecentInteractions.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchRecentInteractions.fulfilled, (state, action) => {
        state.isLoading = false;
        state.interactions = action.payload;
      })
      .addCase(fetchRecentInteractions.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      })
      .addCase(fetchContext.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchContext.fulfilled, (state, action) => {
        state.isLoading = false;
        state.context = action.payload;
      })
      .addCase(fetchContext.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload;
      });
  },
});

export const { clearMemory, clearContext } = memorySlice.actions;

export default memorySlice.reducer;