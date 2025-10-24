import io from 'socket.io-client';
import axios from 'axios';

// Configuration
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';
// Set WS_URL default to Flask-SocketIO port
const WS_URL = process.env.REACT_APP_WS_URL || 'http://localhost:5000';

// Runtime-resolved URL helpers for auto-detecting backend port
const resolveWsUrl = () => {
  if (process.env.REACT_APP_WS_URL) return process.env.REACT_APP_WS_URL;
  if (typeof window !== 'undefined') {
    const injected = window.__JARVIS_WS_URL || (window.__JARVIS_CONFIG && window.__JARVIS_CONFIG.WS_URL);
    if (injected) return injected;
    try {
      const stored = localStorage.getItem('JARVIS_WS_URL');
      if (stored) return stored;
    } catch {}
  }
  return WS_URL;
};

// ... rest of the code unchanged ...


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
    return new Promise((resolve) => {
      try {
        const targetWsUrl = resolveWsUrl();
        socket = io(targetWsUrl, {
          reconnection: true,
          reconnectionAttempts: Infinity,
          reconnectionDelay: 1000,
          reconnectionDelayMax: 5000,
          timeout: 20000,
          transports: ['websocket'],
          autoConnect: true,
        });

        socket.on('connect', () => {
          eventListeners.get('connect')?.forEach(cb => {
            try { cb({ connected: true, socketId: socket.id }); } catch (e) {}
          });
          resolve({ success: true, socketId: socket.id });
        });

        socket.on('connect_error', (error) => {
          eventListeners.get('connect_error')?.forEach(cb => {
            try { cb(error); } catch (e) {}
          });
          resolve({ success: false, error });
        });

        socket.on('disconnect', (reason) => {
          eventListeners.get('disconnect')?.forEach(cb => {
            try { cb({ connected: false, reason }); } catch (e) {}
          });
        });

        socket.on('reconnect_attempt', (attemptNumber) => {
          eventListeners.get('reconnect_attempt')?.forEach(cb => {
            try { cb({ attempt: attemptNumber }); } catch (e) {}
          });
        });

        socket.on('reconnect', (attemptNumber) => {
          eventListeners.get('reconnect')?.forEach(cb => {
            try { cb({ connected: true, attempt: attemptNumber, socketId: socket.id }); } catch (e) {}
          });
        });

        socket.on('reconnect_error', (error) => {
          eventListeners.get('reconnect_error')?.forEach(cb => {
            try { cb(error); } catch (e) {}
          });
        });

        // Set up event listeners for various backend events
        socket.on('message', (data) => {
          eventListeners.get('message')?.forEach(callback => callback(data));
        });

        socket.on('chat_response', (data) => {
          eventListeners.get('chat_response')?.forEach(callback => callback(data));
        });

        socket.on('memory_update', (data) => {
          eventListeners.get('memory_update')?.forEach(callback => callback(data));
        });

        socket.on('system_update', (data) => {
          eventListeners.get('system_update')?.forEach(callback => callback(data));
        });

        socket.on('security_event', (data) => {
          eventListeners.get('security_event')?.forEach(callback => callback(data));
        });

        socket.on('status_update', (data) => {
          eventListeners.get('status_update')?.forEach(callback => callback(data));
        });

        socket.on('error', (error) => {
          eventListeners.get('error')?.forEach(callback => callback(error));
        });
      } catch (error) {
        resolve({ success: false, error });
      }
    });
  },

  /**
   * Check if we're in mock mode (always false; mock disabled)
   */
  isMockMode: () => false,

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
    return new Promise((resolve) => {
      if (!socket || !socket.connected) {
        resolve({ success: false, error: 'Socket not connected' });
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
  },

  // Interaction logging API
  logInteraction: async (payload) => {
    try {
      // Try primary endpoint
      const response = await axios.post(`${API_BASE_URL}/memory/log`, payload);
      return response.data;
    } catch (error) {
      // Fallback endpoint pattern
      try {
        const response = await axios.post(`${API_BASE_URL}/api/memory/log`, payload);
        return response.data;
      } catch (err) {
        console.error('Failed to log interaction:', err);
        // Do not throw to avoid UX interruption; return failure structure
        return { success: false, error: err?.message || String(err) };
      }
    }
  }
};

ApiService.startVoiceRecognition = () => socket.emit('start_voice_recognition');
ApiService.stopVoiceRecognition = () => socket.emit('stop_voice_recognition');
ApiService.sendChatMessage = (message) => socket.emit('user_message', { text: message });

export default ApiService;
// Hybrid Chat + Voice bridge for ChatPanel


