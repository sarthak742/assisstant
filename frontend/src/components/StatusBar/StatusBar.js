import React from 'react';
import styled from 'styled-components';
import { useTheme } from '../../contexts/ThemeContext';

const StatusBarContainer = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.7);
  color: #fff;
  padding: 5px 15px;
  height: 30px;
  font-size: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  z-index: 1000;
`;

const StatusItem = styled.div`
  display: flex;
  align-items: center;
  margin: 0 10px;
`;

const LeftSection = styled.div`
  display: flex;
  align-items: center;
`;

const RightSection = styled.div`
  display: flex;
  align-items: center;
`;

const TimeDisplay = styled.div`
  font-weight: 500;
  letter-spacing: 0.5px;
`;

const BackendStatus = styled(StatusItem)`
  color: ${props => {
    if (props.$isConnected && props.$isMock) return '#ff9800';
    if (props.$isConnected) return '#4caf50';
    if (props.$isConnecting) return '#ff9800';
    return '#f44336';
  }};
`;

const StatusContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const StatusBadge = styled.div`
  padding: 6px 10px;
  border-radius: 12px;
  font-size: 12px;
  border: 1px solid ${props => props.theme.border};
  background: ${props => props.theme.glass};
  color: ${props => props.theme.textSecondary};
`;

const StatusIndicator = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: ${props => props.$isConnected ? props.theme.success : props.$isConnecting ? props.theme.warning : props.theme.error};
  box-shadow: 0 0 10px ${props => props.$isConnected ? props.theme.success : props.$isConnecting ? props.theme.warning : props.theme.error};
`;

const StatusBar = ({ connectionStatus }) => {
  const { theme } = useTheme();
  const isConnected = connectionStatus === 'connected';
  const isConnecting = connectionStatus === 'reconnecting' || connectionStatus === 'connecting';
  const text = isConnected ? 'Connected to backend' : isConnecting ? 'Connecting to backend…' : 'Disconnected';
  
  return (
    <StatusContainer>
      <StatusIndicator
        theme={theme}
        $isConnected={isConnected}
        $isConnecting={isConnecting}
      />
      <StatusBadge theme={theme}>{text}</StatusBadge>
    </StatusContainer>
  );
};

export default StatusBar;