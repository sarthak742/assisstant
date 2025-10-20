import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import ApiService from '../../services/api';

export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async (message, { rejectWithValue }) => {
    try {
      const response = await ApiService.sendMessage(message);
      return response;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

export const textToSpeech = createAsyncThunk(
  'chat/textToSpeech',
  async (text, { rejectWithValue }) => {
    try {
      const response = await ApiService.textToSpeech(text);
      return response;
    } catch (error) {
      return rejectWithValue(error.message);
    }
  }
);

const initialState = {
  messages: [],
  isProcessing: false,
  error: null,
  lastMessageId: null,
};

export const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    addMessage: (state, action) => {
      state.messages.push({
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        ...action.payload,
      });
    },
    clearMessages: (state) => {
      state.messages = [];
    },
    setProcessing: (state, action) => {
      state.isProcessing = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state) => {
        state.isProcessing = true;
        state.error = null;
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.isProcessing = false;
        state.messages.push({
          id: Date.now().toString(),
          timestamp: new Date().toISOString(),
          content: action.payload.response,
          sender: 'jarvis',
          type: 'text',
        });
        state.lastMessageId = state.messages[state.messages.length - 1].id;
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.isProcessing = false;
        state.error = action.payload;
        state.messages.push({
          id: Date.now().toString(),
          timestamp: new Date().toISOString(),
          content: 'Sorry, I encountered an error processing your request.',
          sender: 'jarvis',
          type: 'error',
        });
      })
      .addCase(textToSpeech.pending, (state) => {
        state.isSpeaking = true;
      })
      .addCase(textToSpeech.fulfilled, (state) => {
        state.isSpeaking = false;
      })
      .addCase(textToSpeech.rejected, (state, action) => {
        state.isSpeaking = false;
        state.error = action.payload;
      });
  },
});

export const { addMessage, clearMessages, setProcessing } = chatSlice.actions;

export default chatSlice.reducer;