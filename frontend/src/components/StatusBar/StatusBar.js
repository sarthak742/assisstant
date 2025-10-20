import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { Wifi, WifiOff, Battery, Clock, Signal } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';

const StatusBarContainer = styled(motion.div)`
  position: fixed;
  top: 20px;
  right: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  background: ${props => props.theme.glass};
  backdrop-filter: blur(25px);
  border: 1px solid ${props => props.theme.border};
  border-radius: 12px;
  padding: 8px 16px;
  z-index: 100;
  box-shadow: ${props => props.theme.shadow};
`;

const StatusItem = styled(motion.div)`
  display: flex;
  align-items: center;
  gap: 6px;
  color: ${props => props.theme.textSecondary};
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  
  &:hover {
    color: ${props => props.theme.text};
  }
`;

const StatusIcon = styled.div`
  color: ${props => {
    if (props.status === 'good') return '#10B981';
    if (props.status === 'warning') return '#F59E0B';
    if (props.status === 'error') return '#EF4444';
    return props.theme.textSecondary;
  }};
  display: flex;
  align-items: center;
`;

const BatteryIndicator = styled.div`
  width: 20px;
  height: 10px;
  border: 1px solid ${props => props.theme.textSecondary};
  border-radius: 2px;
  position: relative;
  
  &::after {
    content: '';
    position: absolute;
    right: -3px;
    top: 2px;
    width: 2px;
    height: 6px;
    background: ${props => props.theme.textSecondary};
    border-radius: 0 1px 1px 0;
  }
`;

const BatteryFill = styled(motion.div)`
  height: 100%;
  background: ${props => {
    if (props.level > 50) return '#10B981';
    if (props.level > 20) return '#F59E0B';
    return '#EF4444';
  }};
  border-radius: 1px;
  transition: all 0.3s ease;
`;

const NetworkStrength = styled.div`
  display: flex;
  align-items: flex-end;
  gap: 1px;
  height: 12px;
`;

const SignalBar = styled.div`
  width: 2px;
  background: ${props => props.active ? 
    (props.strength > 75 ? '#10B981' : 
     props.strength > 50 ? '#F59E0B' : '#EF4444') : 
    props.theme.border
  };
  height: ${props => props.height}px;
  border-radius: 1px;
  transition: all 0.3s ease;
`;

const TimeDisplay = styled.div`
  font-family: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
  font-weight: 600;
  color: ${props => props.theme.text};
`;

const StatusBar = () => {
  const { theme } = useTheme();
  const [status, setStatus] = useState({
    time: new Date(),
    network: {
      connected: true,
      strength: 85,
      type: 'wifi'
    },
    battery: {
      level: 78,
      charging: false
    }
  });

  useEffect(() => {
    // Update time every second
    const timeInterval = setInterval(() => {
      setStatus(prev => ({ ...prev, time: new Date() }));
    }, 1000);

    // Update network status
    const updateNetworkStatus = () => {
      setStatus(prev => ({
        ...prev,
        network: {
          ...prev.network,
          connected: navigator.onLine,
          strength: Math.floor(Math.random() * 30) + 70 // Simulate varying strength
        }
      }));
    };

    // Update battery status (if available)
    const updateBatteryStatus = async () => {
      if ('getBattery' in navigator) {
        try {
          const battery = await navigator.getBattery();
          setStatus(prev => ({
            ...prev,
            battery: {
              level: Math.floor(battery.level * 100),
              charging: battery.charging
            }
          }));
        } catch (error) {
          // Battery API not available, use mock data
          setStatus(prev => ({
            ...prev,
            battery: {
              level: Math.floor(Math.random() * 40) + 60,
              charging: Math.random() > 0.7
            }
          }));
        }
      }
    };

    // Initial updates
    updateNetworkStatus();
    updateBatteryStatus();

    // Set up intervals
    const networkInterval = setInterval(updateNetworkStatus, 5000);
    const batteryInterval = setInterval(updateBatteryStatus, 30000);

    // Listen for network changes
    window.addEventListener('online', updateNetworkStatus);
    window.addEventListener('offline', updateNetworkStatus);

    return () => {
      clearInterval(timeInterval);
      clearInterval(networkInterval);
      clearInterval(batteryInterval);
      window.removeEventListener('online', updateNetworkStatus);
      window.removeEventListener('offline', updateNetworkStatus);
    };
  }, []);

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getNetworkIcon = () => {
    if (!status.network.connected) {
      return <WifiOff size={16} />;
    }
    return <Wifi size={16} />;
  };

  const getNetworkStatus = () => {
    if (!status.network.connected) return 'error';
    if (status.network.strength > 70) return 'good';
    if (status.network.strength > 40) return 'warning';
    return 'error';
  };

  const getBatteryStatus = () => {
    if (status.battery.charging) return 'good';
    if (status.battery.level > 50) return 'good';
    if (status.battery.level > 20) return 'warning';
    return 'error';
  };

  return (
    <StatusBarContainer
      theme={theme}
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
    >
      {/* Network Status */}
      <StatusItem
        theme={theme}
        whileHover={{ scale: 1.05 }}
      >
        <StatusIcon status={getNetworkStatus()} theme={theme}>
          {getNetworkIcon()}
        </StatusIcon>
        <NetworkStrength>
          {[3, 6, 9, 12].map((height, index) => (
            <SignalBar
              key={index}
              height={height}
              active={status.network.strength > (index + 1) * 25}
              strength={status.network.strength}
              theme={theme}
            />
          ))}
        </NetworkStrength>
      </StatusItem>

      {/* Battery Status */}
      <StatusItem
        theme={theme}
        whileHover={{ scale: 1.05 }}
      >
        <StatusIcon status={getBatteryStatus()} theme={theme}>
          <BatteryIndicator theme={theme}>
            <BatteryFill
              level={status.battery.level}
              initial={{ width: 0 }}
              animate={{ width: `${status.battery.level}%` }}
              transition={{ duration: 0.5 }}
            />
          </BatteryIndicator>
        </StatusIcon>
        <span>{status.battery.level}%</span>
        {status.battery.charging && (
          <motion.div
            animate={{ opacity: [0.5, 1, 0.5] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          >
            ⚡
          </motion.div>
        )}
      </StatusItem>

      {/* Time */}
      <StatusItem
        theme={theme}
        whileHover={{ scale: 1.05 }}
      >
        <StatusIcon status="good" theme={theme}>
          <Clock size={16} />
        </StatusIcon>
        <TimeDisplay theme={theme}>
          {formatTime(status.time)}
        </TimeDisplay>
      </StatusItem>
    </StatusBarContainer>
  );
};

export default StatusBar;