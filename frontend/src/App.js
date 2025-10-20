import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { ThemeProvider } from './contexts/ThemeContext';

// Import new futuristic components
import ParticleSystem from './components/ParticleSystem/ParticleSystem';
import AIOrb from './components/AIOrb/AIOrb';
import ChatInterface from './components/Chat/ChatInterface';
import Sidebar from './components/Navigation/Sidebar';
import StatusBar from './components/StatusBar/StatusBar';
import { MainContainer } from './components/Glass/GlassComponents';

// Import floating panels
import MemoryPanel from './components/Panels/MemoryPanel';
import UpdatePanel from './components/Panels/UpdatePanel';
import SecurityPanel from './components/Panels/SecurityPanel';
import ApiService from './services/api';

// Global styles
const GlobalContainer = styled.div`
  width: 100vw;
  height: 100vh;
  background: #0A0F1C;
  overflow: hidden;
  position: relative;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
`;

const AppLayout = styled.div`
  display: flex;
  width: 100%;
  height: 100%;
  position: relative;
  z-index: 10;
`;

const MainContent = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
`;

const OrbContainer = styled.div`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 5;
`;

const ChatContainer = styled.div`
  width: 100%;
  max-width: 800px;
  height: 60vh;
  position: relative;
  z-index: 15;
  margin-top: 120px; /* Space for the orb */
`;

function App() {
  const [activePanel, setActivePanel] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('connecting');

  // Initialize backend connection
  useEffect(() => {
    const initializeBackend = async () => {
      try {
        setConnectionStatus('connecting');
        // Initialize WebSocket connection to backend
        await ApiService.initializeSocket().catch(() => {});
        setConnectionStatus('connected');
        console.log('Connected to Jarvis backend via WebSocket');
      } catch (error) {
        console.error('Backend connection error:', error);
        setConnectionStatus('error');
      }
    };

    initializeBackend();
  }, []);

  const handlePanelOpen = (panelType) => {
    setActivePanel(panelType);
  };

  const handlePanelClose = () => {
    setActivePanel(null);
  };

  return (
    <ThemeProvider>
      <GlobalContainer>
        {/* Animated particle background */}
        <ParticleSystem />
        
        {/* Status bar */}
        <StatusBar />
        
        <AppLayout>
          {/* Navigation sidebar */}
          <Sidebar onPanelOpen={handlePanelOpen} />
          
          {/* Main content area */}
          <MainContent>
            {/* Central AI Orb */}
            <OrbContainer>
              <AIOrb connectionStatus={connectionStatus} />
            </OrbContainer>
            
            {/* Chat interface */}
            <ChatContainer>
              <ChatInterface />
            </ChatContainer>
          </MainContent>
        </AppLayout>
        
        {/* Floating panels */}
        <MemoryPanel 
          isVisible={activePanel === 'memory'} 
          onClose={handlePanelClose} 
        />
        
        <UpdatePanel 
          isVisible={activePanel === 'updates'} 
          onClose={handlePanelClose} 
        />
        
        <SecurityPanel 
          isVisible={activePanel === 'security'} 
          onClose={handlePanelClose} 
        />
        
        {/* Additional panels can be added here */}
        {/* Context Panel, Logs Panel, Settings Panel */}
      </GlobalContainer>
    </ThemeProvider>
  );
}

export default App;