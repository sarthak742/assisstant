const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');

// Keep a global reference of the window object
let mainWindow;

function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, 'public/jarvis-icon.png'),
    backgroundColor: '#1a1a2e', // Dark background color
    show: false // Don't show until ready-to-show
  });

  // Load the app with dev fallback
  const devUrl = 'http://localhost:3000';
  const previewUrl = 'http://localhost:8000/preview.html';
  const buildFileUrl = `file://${path.join(__dirname, './build/index.html')}`;
  const localPreviewFile = `file://${path.join(__dirname, 'public', 'preview.html')}`;

  if (isDev) {
    mainWindow.loadURL(devUrl).catch(() => {
      // If dev server is not available, try preview server
      mainWindow.loadURL(previewUrl).catch(() => {
        // Fallback to local preview file
        mainWindow.loadURL(localPreviewFile);
      });
    });
  } else {
    mainWindow.loadURL(buildFileUrl);
  }

  // Fallback when dev URL fails after load attempt
  mainWindow.webContents.on('did-fail-load', (_event, errorCode, errorDescription, validatedURL) => {
    if (isDev && validatedURL === devUrl) {
      mainWindow.loadURL(previewUrl).catch(() => {
        mainWindow.loadURL(localPreviewFile);
      });
    }
  });

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    
    // Open DevTools in development mode
    if (isDev) {
      mainWindow.webContents.openDevTools();
    }
  });

  // Handle window close
  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// Create window when Electron is ready
app.whenReady().then(createWindow);

// Quit when all windows are closed, except on macOS
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// On macOS, re-create window when dock icon is clicked
app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// IPC handlers for communication with backend
ipcMain.handle('connect-backend', async () => {
  // Logic to connect to Python backend via WebSocket or REST
  return { status: 'connected' };
});

// Handle voice recognition start/stop
ipcMain.handle('voice-control', async (event, action) => {
  // Logic to control voice recognition
  return { status: action };
});

// Handle backend API requests
ipcMain.handle('api-request', async (event, { module, action, data }) => {
  // Route requests to appropriate backend module
  console.log(`API Request: ${module}.${action}`, data);
  
  // This would be replaced with actual API calls to the Python backend
  return { success: true, data: {} };
});