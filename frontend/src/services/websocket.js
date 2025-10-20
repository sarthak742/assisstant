import io from 'socket.io-client';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.listeners = new Map();
  }

  connect(url = 'ws://localhost:8765') {
    return new Promise((resolve, reject) => {
      try {
        // Initialize socket connection
        this.socket = io(url, {
          transports: ['websocket'],
          timeout: 5000,
          reconnection: true,
          reconnectionAttempts: this.maxReconnectAttempts,
          reconnectionDelay: this.reconnectDelay
        });

        // Connection successful
        this.socket.on('connect', () => {
          console.log('WebSocket connected to Jarvis backend');
          this.isConnected = true;
          this.reconnectAttempts = 0;
          resolve({ success: true, socket: this.socket });
        });

        // Connection error
        this.socket.on('connect_error', (error) => {
          console.error('WebSocket connection error:', error);
          this.isConnected = false;
          
          if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            reject({ success: false, error: 'Max reconnection attempts reached' });
          }
        });

        // Disconnection
        this.socket.on('disconnect', (reason) => {
          console.log('WebSocket disconnected:', reason);
          this.isConnected = false;
          
          // Attempt to reconnect if not intentional
          if (reason !== 'io client disconnect') {
            this.attemptReconnect();
          }
        });

        // Handle incoming messages
        this.socket.on('message', (data) => {
          this.handleMessage(data);
        });

        // Handle chat responses
        this.socket.on('chat_response', (data) => {
          this.emit('chat_response', data);
        });

        // Handle memory updates
        this.socket.on('memory_update', (data) => {
          this.emit('memory_update', data);
        });

        // Handle system updates
        this.socket.on('system_update', (data) => {
          this.emit('system_update', data);
        });

        // Handle security events
        this.socket.on('security_event', (data) => {
          this.emit('security_event', data);
        });

      } catch (error) {
        console.error('Failed to initialize WebSocket:', error);
        reject({ success: false, error: error.message });
      }
    });
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.isConnected = false;
    }
  }

  attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        if (this.socket) {
          this.socket.connect();
        }
      }, this.reconnectDelay * this.reconnectAttempts);
    }
  }

  // Send message to backend
  sendMessage(type, data) {
    if (this.isConnected && this.socket) {
      this.socket.emit(type, data);
      return true;
    } else {
      console.warn('WebSocket not connected. Message not sent:', { type, data });
      return false;
    }
  }

  // Send chat message
  sendChatMessage(message, options = {}) {
    return this.sendMessage('chat_message', {
      message,
      timestamp: new Date().toISOString(),
      ...options
    });
  }

  // Send voice data
  sendVoiceData(audioData) {
    return this.sendMessage('voice_data', {
      audio: audioData,
      timestamp: new Date().toISOString()
    });
  }

  // Request memory data
  requestMemoryData(filters = {}) {
    return this.sendMessage('memory_request', filters);
  }

  // Request system status
  requestSystemStatus() {
    return this.sendMessage('system_status_request', {
      timestamp: new Date().toISOString()
    });
  }

  // Handle incoming messages
  handleMessage(data) {
    console.log('Received WebSocket message:', data);
    this.emit('message', data);
  }

  // Event listener management
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index > -1) {
        callbacks.splice(index, 1);
      }
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in WebSocket event listener for ${event}:`, error);
        }
      });
    }
  }

  // Get connection status
  getConnectionStatus() {
    return {
      connected: this.isConnected,
      reconnectAttempts: this.reconnectAttempts,
      socket: this.socket
    };
  }
}

// Create singleton instance
const webSocketService = new WebSocketService();

export default webSocketService;