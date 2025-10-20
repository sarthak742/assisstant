import React from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Minimize2 } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';

const PanelOverlay = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(5px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
`;

const PanelContainer = styled(motion.div)`
  background: ${props => props.theme.glass};
  backdrop-filter: blur(25px);
  border: 1px solid ${props => props.theme.border};
  border-radius: 20px;
  box-shadow: ${props => props.theme.shadow};
  width: 100%;
  max-width: ${props => props.maxWidth || '600px'};
  max-height: 80vh;
  overflow: hidden;
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, ${props => props.theme.accent}, transparent);
    opacity: 0.5;
  }
`;

const PanelHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid ${props => props.theme.border};
  background: ${props => props.theme.glass};
`;

const PanelTitle = styled.h2`
  color: ${props => props.theme.text};
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 12px;
`;

const PanelControls = styled.div`
  display: flex;
  gap: 8px;
`;

const ControlButton = styled(motion.button)`
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: transparent;
  border: 1px solid ${props => props.theme.border};
  color: ${props => props.theme.textSecondary};
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;

  &:hover {
    background: ${props => props.theme.glassHover};
    border-color: ${props => props.theme.primary};
    color: ${props => props.theme.text};
    box-shadow: 0 0 10px ${props => props.theme.glow};
  }
`;

const PanelContent = styled.div`
  padding: 24px;
  overflow-y: auto;
  max-height: calc(80vh - 80px);
  
  /* Custom scrollbar */
  &::-webkit-scrollbar {
    width: 6px;
  }
  
  &::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 3px;
  }
  
  &::-webkit-scrollbar-thumb {
    background: ${props => props.theme.primary};
    border-radius: 3px;
    
    &:hover {
      background: ${props => props.theme.secondary};
    }
  }
`;

const FloatingPanel = ({ 
  isVisible, 
  onClose, 
  onMinimize, 
  title, 
  icon: Icon, 
  children, 
  maxWidth 
}) => {
  const { theme } = useTheme();

  const overlayVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1 }
  };

  const panelVariants = {
    hidden: { 
      opacity: 0, 
      scale: 0.8, 
      y: 50,
      rotateX: -15
    },
    visible: { 
      opacity: 1, 
      scale: 1, 
      y: 0,
      rotateX: 0,
      transition: {
        type: "spring",
        stiffness: 300,
        damping: 30
      }
    },
    exit: { 
      opacity: 0, 
      scale: 0.8, 
      y: 50,
      rotateX: 15,
      transition: {
        duration: 0.2
      }
    }
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <PanelOverlay
          variants={overlayVariants}
          initial="hidden"
          animate="visible"
          exit="hidden"
          onClick={onClose}
        >
          <PanelContainer
            theme={theme}
            maxWidth={maxWidth}
            variants={panelVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            onClick={(e) => e.stopPropagation()}
          >
            <PanelHeader theme={theme}>
              <PanelTitle theme={theme}>
                {Icon && <Icon size={20} />}
                {title}
              </PanelTitle>
              
              <PanelControls>
                {onMinimize && (
                  <ControlButton
                    theme={theme}
                    onClick={onMinimize}
                    whileHover={{ scale: 1.1 }}
                    whileTap={{ scale: 0.9 }}
                  >
                    <Minimize2 size={16} />
                  </ControlButton>
                )}
                
                <ControlButton
                  theme={theme}
                  onClick={onClose}
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                >
                  <X size={16} />
                </ControlButton>
              </PanelControls>
            </PanelHeader>
            
            <PanelContent theme={theme}>
              {children}
            </PanelContent>
          </PanelContainer>
        </PanelOverlay>
      )}
    </AnimatePresence>
  );
};

export default FloatingPanel;