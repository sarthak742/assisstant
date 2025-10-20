import { configureStore } from '@reduxjs/toolkit';
import appReducer from './slices/appSlice';
import chatReducer from './slices/chatSlice';
import memoryReducer from './slices/memorySlice';
import updateReducer from './slices/updateSlice';
import securityReducer from './slices/securitySlice';

export const store = configureStore({
  reducer: {
    app: appReducer,
    chat: chatReducer,
    memory: memoryReducer,
    update: updateReducer,
    security: securityReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
    }),
});

export default store;