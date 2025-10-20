const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld(
  'api', {
    // Backend connection
    connectBackend: () => ipcRenderer.invoke('connect-backend'),
    
    // Voice control
    startVoiceRecognition: () => ipcRenderer.invoke('voice-control', 'start'),
    stopVoiceRecognition: () => ipcRenderer.invoke('voice-control', 'stop'),
    
    // Memory manager
    getRecentInteractions: (count) => 
      ipcRenderer.invoke('api-request', { 
        module: 'memory', 
        action: 'getRecentInteractions',
        data: { count } 
      }),
    
    // Context management
    getContext: (key) => 
      ipcRenderer.invoke('api-request', { 
        module: 'memory', 
        action: 'getContext',
        data: { key } 
      }),
    
    // Self-update manager
    checkForUpdates: () => 
      ipcRenderer.invoke('api-request', { 
        module: 'selfUpdate', 
        action: 'checkForUpdates' 
      }),
    
    getVersionInfo: () => 
      ipcRenderer.invoke('api-request', { 
        module: 'selfUpdate', 
        action: 'getVersionInfo' 
      }),
    
    // Security module
    authenticate: (password) => 
      ipcRenderer.invoke('api-request', { 
        module: 'security', 
        action: 'authenticate',
        data: { password } 
      }),
    
    // Send message to Jarvis
    sendMessage: (message) => 
      ipcRenderer.invoke('api-request', { 
        module: 'aiChat', 
        action: 'processMessage',
        data: { message } 
      }),
      
    // System control
    executeSystemCommand: (command) => 
      ipcRenderer.invoke('api-request', { 
        module: 'system', 
        action: 'executeCommand',
        data: { command } 
      }),
      
    // Get logs
    getLogs: (count) => 
      ipcRenderer.invoke('api-request', { 
        module: 'system', 
        action: 'getLogs',
        data: { count } 
      })
  }
);