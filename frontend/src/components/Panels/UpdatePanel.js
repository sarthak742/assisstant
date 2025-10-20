import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { Download, RefreshCw, CheckCircle, AlertCircle, Info } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';
import FloatingPanel from './FloatingPanel';
import { GlassButton } from '../Glass/GlassComponents';
import ApiService from '../../services/api';

const UpdateContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const VersionCard = styled(motion.div)`
  background: ${props => props.theme.glass};
  border: 1px solid ${props => props.theme.border};
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
`;

const VersionIcon = styled.div`
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: ${props => props.current ? props.theme.primary : props.theme.secondary}20;
  color: ${props => props.current ? props.theme.primary : props.theme.secondary};
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid ${props => props.current ? props.theme.primary : props.theme.secondary}40;
`;

const VersionInfo = styled.div`
  flex: 1;
`;

const VersionNumber = styled.div`
  font-size: 18px;
  font-weight: 600;
  color: ${props => props.theme.text};
  margin-bottom: 4px;
`;

const VersionLabel = styled.div`
  font-size: 14px;
  color: ${props => props.theme.textSecondary};
`;

const VersionDate = styled.div`
  font-size: 12px;
  color: ${props => props.theme.textSecondary};
  margin-top: 4px;
`;

const UpdateStatus = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: ${props => props.theme.glass};
  border: 1px solid ${props => props.theme.border};
  border-radius: 12px;
  margin-bottom: 20px;
`;

const StatusIcon = styled.div`
  color: ${props => {
    if (props.status === 'available') return props.theme.secondary;
    if (props.status === 'downloading') return props.theme.primary;
    if (props.status === 'ready') return '#10B981';
    return props.theme.textSecondary;
  }};
`;

const StatusText = styled.div`
  flex: 1;
  color: ${props => props.theme.text};
  font-weight: 500;
`;

const ProgressContainer = styled.div`
  margin: 20px 0;
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background: ${props => props.theme.glass};
  border-radius: 4px;
  overflow: hidden;
  border: 1px solid ${props => props.theme.border};
`;

const ProgressFill = styled(motion.div)`
  height: 100%;
  background: linear-gradient(90deg, ${props => props.theme.primary}, ${props => props.theme.secondary});
  border-radius: 4px;
  box-shadow: 0 0 10px ${props => props.theme.glow};
`;

const ProgressText = styled.div`
  text-align: center;
  margin-top: 8px;
  font-size: 14px;
  color: ${props => props.theme.textSecondary};
`;

const UpdateActions = styled.div`
  display: flex;
  gap: 12px;
  justify-content: flex-end;
`;

const ChangelogSection = styled.div`
  margin-top: 24px;
`;

const ChangelogTitle = styled.h3`
  color: ${props => props.theme.text};
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ChangelogList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
`;

const ChangelogItem = styled.li`
  color: ${props => props.theme.textSecondary};
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 8px;
  padding-left: 20px;
  position: relative;
  
  &::before {
    content: '•';
    color: ${props => props.theme.primary};
    position: absolute;
    left: 0;
  }
`;

const UpdatePanel = ({ isVisible, onClose }) => {
  const { theme } = useTheme();
  const [updateInfo, setUpdateInfo] = useState({
    currentVersion: '1.0.0',
    latestVersion: '1.0.0',
    hasUpdate: false,
    status: 'up-to-date', // 'up-to-date', 'available', 'downloading', 'ready'
    progress: 0,
    changelog: []
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isVisible) {
      checkForUpdates();
    }
  }, [isVisible]);

  const checkForUpdates = async () => {
    setLoading(true);
    try {
      const data = await ApiService.checkForUpdates();
      setUpdateInfo(data);
    } catch (error) {
      // Fallback to mock data for development
      setUpdateInfo({
        currentVersion: '1.0.0',
        latestVersion: '1.1.0',
        hasUpdate: true,
        status: 'available',
        progress: 0,
        changelog: [
          'Added voice interaction system',
          'Improved glassmorphism UI effects',
          'Enhanced memory management',
          'Fixed various bugs and performance issues'
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  const downloadUpdate = async () => {
    try {
      setUpdateInfo(prev => ({ ...prev, status: 'downloading', progress: 0 }));
      
      // Backend should stream progress; for now simulate
      await ApiService.sendSocketMessage?.('updates_download', {});
      
      const progressInterval = setInterval(() => {
        setUpdateInfo(prev => {
          const newProgress = Math.min(prev.progress + 10, 100);
          if (newProgress === 100) {
            clearInterval(progressInterval);
            return { ...prev, progress: newProgress, status: 'ready' };
          }
          return { ...prev, progress: newProgress };
        });
      }, 500);
    } catch (error) {
      console.error('Failed to download update:', error);
      setUpdateInfo(prev => ({ ...prev, status: 'available', progress: 0 }));
    }
  };

  const applyUpdate = async () => {
    try {
      await ApiService.sendSocketMessage?.('updates_apply', {});
      alert('Update will be applied on next restart');
    } catch (error) {
      console.error('Failed to apply update:', error);
    }
  };

  const getStatusInfo = () => {
    switch (updateInfo.status) {
      case 'available':
        return {
          icon: <Download size={20} />,
          text: 'Update available',
          color: theme.secondary
        };
      case 'downloading':
        return {
          icon: <RefreshCw size={20} className="animate-spin" />,
          text: 'Downloading update...',
          color: theme.primary
        };
      case 'ready':
        return {
          icon: <CheckCircle size={20} />,
          text: 'Update ready to install',
          color: '#10B981'
        };
      default:
        return {
          icon: <CheckCircle size={20} />,
          text: 'You are up to date',
          color: '#10B981'
        };
    }
  };

  const statusInfo = getStatusInfo();

  return (
    <FloatingPanel
      isVisible={isVisible}
      onClose={onClose}
      title="System Updates"
      icon={RefreshCw}
      maxWidth="600px"
    >
      <UpdateContainer>
        <UpdateStatus theme={theme}>
          <StatusIcon status={updateInfo.status} theme={theme}>
            {statusInfo.icon}
          </StatusIcon>
          <StatusText theme={theme}>
            {statusInfo.text}
          </StatusText>
          <GlassButton
            theme={theme}
            onClick={checkForUpdates}
            disabled={loading}
            style={{ padding: '8px 12px', fontSize: '12px' }}
          >
            {loading ? <RefreshCw size={14} className="animate-spin" /> : 'Check'}
          </GlassButton>
        </UpdateStatus>

        <VersionCard theme={theme}>
          <VersionIcon current theme={theme}>
            <CheckCircle size={24} />
          </VersionIcon>
          <VersionInfo>
            <VersionNumber theme={theme}>
              v{updateInfo.currentVersion}
            </VersionNumber>
            <VersionLabel theme={theme}>
              Current Version
            </VersionLabel>
            <VersionDate theme={theme}>
              Installed on {new Date().toLocaleDateString()}
            </VersionDate>
          </VersionInfo>
        </VersionCard>

        {updateInfo.hasUpdate && (
          <VersionCard theme={theme}>
            <VersionIcon theme={theme}>
              <Download size={24} />
            </VersionIcon>
            <VersionInfo>
              <VersionNumber theme={theme}>
                v{updateInfo.latestVersion}
              </VersionNumber>
              <VersionLabel theme={theme}>
                Latest Version
              </VersionLabel>
              <VersionDate theme={theme}>
                Released recently
              </VersionDate>
            </VersionInfo>
          </VersionCard>
        )}

        {updateInfo.status === 'downloading' && (
          <ProgressContainer>
            <ProgressBar theme={theme}>
              <ProgressFill
                theme={theme}
                initial={{ width: 0 }}
                animate={{ width: `${updateInfo.progress}%` }}
                transition={{ duration: 0.3 }}
              />
            </ProgressBar>
            <ProgressText theme={theme}>
              {updateInfo.progress}% complete
            </ProgressText>
          </ProgressContainer>
        )}

        <UpdateActions>
          {updateInfo.status === 'available' && (
            <GlassButton
              theme={theme}
              onClick={downloadUpdate}
            >
              <Download size={16} />
              Download Update
            </GlassButton>
          )}
          
          {updateInfo.status === 'ready' && (
            <GlassButton
              theme={theme}
              onClick={applyUpdate}
              style={{
                background: `linear-gradient(135deg, ${theme.primary}20, ${theme.secondary}20)`,
                borderColor: theme.primary
              }}
            >
              <RefreshCw size={16} />
              Restart to Apply Update
            </GlassButton>
          )}
        </UpdateActions>

        {updateInfo.changelog.length > 0 && (
          <ChangelogSection>
            <ChangelogTitle theme={theme}>
              <Info size={16} />
              What's New
            </ChangelogTitle>
            <ChangelogList>
              {updateInfo.changelog.map((item, index) => (
                <ChangelogItem key={index} theme={theme}>
                  {item}
                </ChangelogItem>
              ))}
            </ChangelogList>
          </ChangelogSection>
        )}
      </UpdateContainer>
    </FloatingPanel>
  );
};

export default UpdatePanel;