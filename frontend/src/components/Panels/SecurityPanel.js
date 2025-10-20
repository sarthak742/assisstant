import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { Shield, Lock, Unlock, Eye, EyeOff, Fingerprint, Key, Settings } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';
import FloatingPanel from './FloatingPanel';
import { GlassButton, GlassInput } from '../Glass/GlassComponents';
import ApiService from '../../services/api';

const SecurityContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const SecuritySection = styled.div`
  background: ${props => props.theme.glass};
  border: 1px solid ${props => props.theme.border};
  border-radius: 12px;
  padding: 20px;
`;

const SectionTitle = styled.h3`
  color: ${props => props.theme.text};
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const SecurityOption = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid ${props => props.theme.border}40;
  
  &:last-child {
    border-bottom: none;
  }
`;

const OptionInfo = styled.div`
  flex: 1;
`;

const OptionTitle = styled.div`
  color: ${props => props.theme.text};
  font-weight: 500;
  margin-bottom: 4px;
`;

const OptionDescription = styled.div`
  color: ${props => props.theme.textSecondary};
  font-size: 14px;
`;

const Toggle = styled(motion.button)`
  width: 48px;
  height: 24px;
  border-radius: 12px;
  background: ${props => props.active ? props.theme.primary : props.theme.glass};
  border: 1px solid ${props => props.active ? props.theme.primary : props.theme.border};
  cursor: pointer;
  position: relative;
  transition: all 0.3s ease;
  
  &::after {
    content: '';
    position: absolute;
    top: 2px;
    left: ${props => props.active ? '26px' : '2px'};
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: ${props => props.active ? '#fff' : props.theme.textSecondary};
    transition: all 0.3s ease;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  }
`;

const LockStatus = styled(motion.div)`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 20px;
  background: ${props => props.locked ? 
    `linear-gradient(135deg, #EF444420, #DC262620)` : 
    `linear-gradient(135deg, ${props.theme.primary}20, ${props.theme.secondary}20)`
  };
  border: 1px solid ${props => props.locked ? '#EF4444' : props.theme.primary};
  border-radius: 12px;
  margin-bottom: 20px;
`;

const LockIcon = styled(motion.div)`
  color: ${props => props.locked ? '#EF4444' : props.theme.primary};
  font-size: 24px;
`;

const LockText = styled.div`
  color: ${props => props.theme.text};
  font-weight: 600;
  font-size: 16px;
`;

const PinInput = styled.div`
  display: flex;
  gap: 8px;
  justify-content: center;
  margin: 20px 0;
`;

const PinDot = styled(motion.div)`
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: ${props => props.filled ? props.theme.primary : 'transparent'};
  border: 2px solid ${props => props.filled ? props.theme.primary : props.theme.border};
  transition: all 0.3s ease;
`;

const PinKeypad = styled.div`
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  max-width: 200px;
  margin: 0 auto;
`;

const PinKey = styled(motion.button)`
  width: 50px;
  height: 50px;
  border-radius: 12px;
  background: ${props => props.theme.glass};
  border: 1px solid ${props => props.theme.border};
  color: ${props => props.theme.text};
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  
  &:hover {
    background: ${props => props.theme.glassHover};
    border-color: ${props => props.theme.primary};
    box-shadow: 0 0 10px ${props => props.theme.glow};
  }
`;

const BiometricButton = styled(GlassButton)`
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 16px auto 0;
`;

const SecurityPanel = ({ isVisible, onClose }) => {
  const { theme } = useTheme();
  const [securitySettings, setSecuritySettings] = useState({
    pinEnabled: false,
    biometricEnabled: false,
    autoLock: true,
    encryptMemory: true,
    requireAuthForSettings: true
  });
  const [isLocked, setIsLocked] = useState(false);
  const [pin, setPin] = useState('');
  const [showPinSetup, setShowPinSetup] = useState(false);

  useEffect(() => {
    if (isVisible) {
      fetchSecuritySettings();
    }
  }, [isVisible]);

  const fetchSecuritySettings = async () => {
    try {
      const data = await ApiService.getSecuritySettings();
      setSecuritySettings(data);
      setIsLocked(data.isLocked || false);
    } catch (error) {
      console.error('Failed to fetch security settings:', error);
    }
  };

  const updateSecuritySetting = async (key, value) => {
    try {
      await ApiService.updateSecuritySettings({ [key]: value });
      setSecuritySettings(prev => ({ ...prev, [key]: value }));
    } catch (error) {
      console.error('Failed to update security setting:', error);
    }
  };

  const handlePinInput = (digit) => {
    if (pin.length < 4) {
      setPin(prev => prev + digit);
    }
  };

  const clearPin = () => {
    setPin('');
  };

  const verifyPin = async () => {
    try {
      const result = await ApiService.verifyPin(pin);
      if (result?.success) {
        setIsLocked(false);
      } else {
        alert(result?.message || 'Incorrect PIN');
        clearPin();
      }
    } catch (error) {
      console.error('Failed to verify PIN:', error);
    }
  };

  const toggleLock = async () => {
    try {
      const result = await ApiService.executeCommand('security:toggle_lock');
      if (result?.success) {
        setIsLocked(!isLocked);
      }
    } catch (error) {
      console.error('Failed to toggle lock:', error);
    }
  };

  const authenticateWithBiometric = async () => {
    try {
      // Simulate biometric authentication
      if (navigator.credentials) {
        const credential = await navigator.credentials.create({
          publicKey: {
            challenge: new Uint8Array(32),
            rp: { name: "Jarvis AI" },
            user: {
              id: new Uint8Array(16),
              name: "user@jarvis.ai",
              displayName: "Jarvis User"
            },
            pubKeyCredParams: [{ alg: -7, type: "public-key" }]
          }
        });
        
        if (credential) {
          setIsLocked(false);
        }
      }
    } catch (error) {
      console.error('Biometric authentication failed:', error);
    }
  };

  useEffect(() => {
    if (pin.length === 4) {
      verifyPin();
    }
  }, [pin]);

  if (isLocked) {
    return (
      <FloatingPanel
        isVisible={isVisible}
        onClose={onClose}
        title="Security"
        icon={Shield}
        maxWidth="400px"
      >
        <SecurityContainer>
          <LockStatus theme={theme} locked={isLocked}>
            <LockIcon theme={theme} locked={isLocked}>
              <Lock size={24} />
            </LockIcon>
            <LockText theme={theme}>
              System Locked
            </LockText>
          </LockStatus>

          <PinInput>
            {[0, 1, 2, 3].map(index => (
              <PinDot
                key={index}
                theme={theme}
                filled={index < pin.length}
                animate={{ scale: index === pin.length - 1 ? [1, 1.2, 1] : 1 }}
                transition={{ duration: 0.2 }}
              />
            ))}
          </PinInput>

          <PinKeypad>
            {[1, 2, 3, 4, 5, 6, 7, 8, 9].map(digit => (
              <PinKey
                key={digit}
                theme={theme}
                onClick={() => handlePinInput(digit.toString())}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                {digit}
              </PinKey>
            ))}
            <PinKey
              theme={theme}
              onClick={clearPin}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              ←
            </PinKey>
            <PinKey
              theme={theme}
              onClick={() => handlePinInput('0')}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              0
            </PinKey>
            <div /> {/* Empty space */}
          </PinKeypad>

          {securitySettings.biometricEnabled && (
            <BiometricButton
              theme={theme}
              onClick={authenticateWithBiometric}
            >
              <Fingerprint size={16} />
              Use Biometric
            </BiometricButton>
          )}
        </SecurityContainer>
      </FloatingPanel>
    );
  }

  return (
    <FloatingPanel
      isVisible={isVisible}
      onClose={onClose}
      title="Security Settings"
      icon={Shield}
      maxWidth="600px"
    >
      <SecurityContainer>
        <LockStatus theme={theme} locked={false}>
          <LockIcon theme={theme} locked={false}>
            <Unlock size={24} />
          </LockIcon>
          <LockText theme={theme}>
            System Unlocked
          </LockText>
          <GlassButton
            theme={theme}
            onClick={toggleLock}
            style={{ marginLeft: 'auto' }}
          >
            <Lock size={16} />
            Lock Now
          </GlassButton>
        </LockStatus>

        <SecuritySection theme={theme}>
          <SectionTitle theme={theme}>
            <Key size={16} />
            Authentication
          </SectionTitle>
          
          <SecurityOption theme={theme}>
            <OptionInfo>
              <OptionTitle theme={theme}>PIN Protection</OptionTitle>
              <OptionDescription theme={theme}>
                Require 4-digit PIN to unlock
              </OptionDescription>
            </OptionInfo>
            <Toggle
              theme={theme}
              active={securitySettings.pinEnabled}
              onClick={() => updateSecuritySetting('pinEnabled', !securitySettings.pinEnabled)}
              whileTap={{ scale: 0.95 }}
            />
          </SecurityOption>

          <SecurityOption theme={theme}>
            <OptionInfo>
              <OptionTitle theme={theme}>Biometric Authentication</OptionTitle>
              <OptionDescription theme={theme}>
                Use fingerprint or face recognition
              </OptionDescription>
            </OptionInfo>
            <Toggle
              theme={theme}
              active={securitySettings.biometricEnabled}
              onClick={() => updateSecuritySetting('biometricEnabled', !securitySettings.biometricEnabled)}
              whileTap={{ scale: 0.95 }}
            />
          </SecurityOption>
        </SecuritySection>

        <SecuritySection theme={theme}>
          <SectionTitle theme={theme}>
            <Settings size={16} />
            Privacy & Security
          </SectionTitle>
          
          <SecurityOption theme={theme}>
            <OptionInfo>
              <OptionTitle theme={theme}>Auto Lock</OptionTitle>
              <OptionDescription theme={theme}>
                Automatically lock after inactivity
              </OptionDescription>
            </OptionInfo>
            <Toggle
              theme={theme}
              active={securitySettings.autoLock}
              onClick={() => updateSecuritySetting('autoLock', !securitySettings.autoLock)}
              whileTap={{ scale: 0.95 }}
            />
          </SecurityOption>

          <SecurityOption theme={theme}>
            <OptionInfo>
              <OptionTitle theme={theme}>Encrypt Memory</OptionTitle>
              <OptionDescription theme={theme}>
                Encrypt stored conversations and data
              </OptionDescription>
            </OptionInfo>
            <Toggle
              theme={theme}
              active={securitySettings.encryptMemory}
              onClick={() => updateSecuritySetting('encryptMemory', !securitySettings.encryptMemory)}
              whileTap={{ scale: 0.95 }}
            />
          </SecurityOption>

          <SecurityOption theme={theme}>
            <OptionInfo>
              <OptionTitle theme={theme}>Require Auth for Settings</OptionTitle>
              <OptionDescription theme={theme}>
                Require authentication to change settings
              </OptionDescription>
            </OptionInfo>
            <Toggle
              theme={theme}
              active={securitySettings.requireAuthForSettings}
              onClick={() => updateSecuritySetting('requireAuthForSettings', !securitySettings.requireAuthForSettings)}
              whileTap={{ scale: 0.95 }}
            />
          </SecurityOption>
        </SecuritySection>
      </SecurityContainer>
    </FloatingPanel>
  );
};

export default SecurityPanel;