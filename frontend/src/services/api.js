import io from 'socket.io-client';
import axios from 'axios';

// Configuration
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8765';

// Socket.io connection
let socket = null;
let eventListeners = new Map();

/**
 * API Service for communicating with the Jarvis backend
 */
export const ApiService = {
  /**
   * Initialize WebSocket connection to backend
   */
  initializeSocket: () => {
    return new Promise((resolve, reject) => {
      try {
        socket = io(WS_URL, {
          reconnectionAttempts: 5,
          reconnectionDelay: 1000,
        });

        socket.on('connect', () => {
          console.log('WebSocket connected');
          resolve({ success: true, socketId: socket.id });
        });

        socket.on('connect_error', (error) => {
          console.error('WebSocket connection error:', error);
          reject({ success: false, error });
        });

        // Set up event listeners for various backend events
        socket.on('message', (data) => {
          console.log('Received message:', data);
          eventListeners.get('message')?.forEach(callback => callback(data));
        });

        socket.on('chat_response', (data) => {
          console.log('Chat response:', data);
          eventListeners.get('chat_response')?.forEach(callback => callback(data));
        });

        socket.on('memory_update', (data) => {
          console.log('Memory update:', data);
          eventListeners.get('memory_update')?.forEach(callback => callback(data));
        });

        socket.on('system_update', (data) => {
          console.log('System update:', data);
          eventListeners.get('system_update')?.forEach(callback => callback(data));
        });

        socket.on('security_event', (data) => {
          console.log('Security event:', data);
          eventListeners.get('security_event')?.forEach(callback => callback(data));
        });

        socket.on('status_update', (data) => {
          console.log('Status update:', data);
          eventListeners.get('status_update')?.forEach(callback => callback(data));
        });

        socket.on('error', (error) => {
          console.error('Backend error:', error);
          eventListeners.get('error')?.forEach(callback => callback(error));
        });
      } catch (error) {
        console.error('Failed to initialize socket:', error);
        reject({ success: false, error });
      }
    });
  },

  /**
   * Disconnect WebSocket
   */
  disconnectSocket: () => {
    if (socket) {
      socket.disconnect();
      socket = null;
    }
    eventListeners.clear();
  },

  /**
   * Add event listener for WebSocket events
   */
  addEventListener: (event, callback) => {
    if (!eventListeners.has(event)) {
      eventListeners.set(event, new Set());
    }
    eventListeners.get(event).add(callback);
  },

  /**
   * Remove event listener
   */
  removeEventListener: (event, callback) => {
    if (eventListeners.has(event)) {
      eventListeners.get(event).delete(callback);
    }
  },

  /**
   * Send message via WebSocket
   */
  sendSocketMessage: (event, data) => {
    return new Promise((resolve, reject) => {
      if (!socket || !socket.connected) {
        reject(new Error('Socket not connected'));
        return;
      }

      socket.emit(event, data, (response) => {
        resolve(response);
      });
    });
  },

  /**
   * REST API calls
   */
  // Memory Manager API
  getRecentInteractions: async (count = 10) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/memory/interactions`, {
        params: { count }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch interactions:', error);
      throw error;
    }
  },

  getContext: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/memory/context`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch context:', error);
      throw error;
    }
  },

  // Additional Memory API used by panels
  listMemories: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/memory/list`);
      return response.data;
    } catch (error) {
      console.error('Failed to list memories:', error);
      throw error;
    }
  },

  deleteMemory: async (id) => {
    try {
      const response = await axios.delete(`${API_BASE_URL}/api/memory/${id}`);
      return response.data;
    } catch (error) {
      console.error('Failed to delete memory:', error);
      throw error;
    }
  },

  updateMemory: async (id, payload) => {
    try {
      const response = await axios.patch(`${API_BASE_URL}/api/memory/${id}`, payload);
      return response.data;
    } catch (error) {
      console.error('Failed to update memory:', error);
      throw error;
    }
  },

  // AI Chat API
  sendMessage: async (message) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/ai/chat`, { message });
      return response.data;
    } catch (error) {
      console.error('Failed to send message:', error);
      throw error;
    }
  },

  // Voice API
  startVoiceRecognition: async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/voice/start`);
      return response.data;
    } catch (error) {
      console.error('Failed to start voice recognition:', error);
      throw error;
    }
  },

  stopVoiceRecognition: async () => {
    try {
      const response = await axios.post(`${API_BASE_URL}/voice/stop`);
      return response.data;
    } catch (error) {
      console.error('Failed to stop voice recognition:', error);
      throw error;
    }
  },

  textToSpeech: async (text) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/voice/speak`, { text });
      return response.data;
    } catch (error) {
      console.error('Failed to convert text to speech:', error);
      throw error;
    }
  },

  // Self-Update API
  checkForUpdates: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/updates/check`);
      return response.data;
    } catch (error) {
      console.error('Failed to check for updates:', error);
      throw error;
    }
  },

  getVersionInfo: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/updates/version`);
      return response.data;
    } catch (error) {
      console.error('Failed to get version info:', error);
      throw error;
    }
  },

  // Security API
  authenticate: async (credentials) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/security/auth`, credentials);
      return response.data;
    } catch (error) {
      console.error('Authentication failed:', error);
      throw error;
    }
  },

  getSecuritySettings: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/security/settings`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch security settings:', error);
      throw error;
    }
  },

  updateSecuritySettings: async (payload) => {
    try {
      const response = await axios.patch(`${API_BASE_URL}/api/security/settings`, payload);
      return response.data;
    } catch (error) {
      console.error('Failed to update security settings:', error);
      throw error;
    }
  },

  verifyPin: async (pin) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/security/verify-pin`, { pin });
      return response.data;
    } catch (error) {
      console.error('Failed to verify PIN:', error);
      throw error;
    }
  },

  // System API
  getLogs: async (count = 50) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/system/logs`, {
        params: { count }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to fetch logs:', error);
      throw error;
    }
  },

  executeCommand: async (command) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/system/execute`, { command });
      return response.data;
    } catch (error) {
      console.error('Failed to execute command:', error);
      throw error;
    }
  }
};

export default ApiService;