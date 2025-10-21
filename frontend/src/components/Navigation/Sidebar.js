import React, { useState } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  MessageCircle, 
  Brain, 
  Database, 
  Download, 
  Shield, 
  FileText, 
  Settings,
  ChevronRight
} from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';

const SidebarContainer = styled(motion.div)`
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  width: ${props => props.$isExpanded ? '220px' : '80px'};
  background: ${props => props.theme.glass};
  backdrop-filter: blur(20px);
  border-right: 1px solid ${props => props.theme.border};
  display: flex;
  flex-direction: column;
  align-items: ${props => props.$isExpanded ? 'flex-start' : 'center'};
  padding: 20px 0;
  z-index: 100;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  overflow: hidden;

  &:hover {
    width: 220px;
  }
`;

const Logo = styled(motion.div)`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 20px;
  margin-bottom: 40px;
  width: 100%;
`;

const LogoIcon = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 12px;
  background: ${props => props.theme.orbGradient};
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 20px ${props => props.theme.glow};
  font-weight: bold;
  color: white;
  font-size: 18px;
`;

const LogoText = styled(motion.span)`
  color: ${props => props.theme.text};
  font-size: 20px;
  font-weight: 600;
  white-space: nowrap;
`;

const NavList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
  flex: 1;
`;

const NavItem = styled(motion.div)`
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 20px;
  margin: 0 10px;
  border-radius: 12px;
  cursor: pointer;
  position: relative;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  
  ${props => props.$isActive && `
    background: ${props.theme.glass};
    border: 1px solid ${props.theme.primary};
    box-shadow: 0 0 20px ${props.theme.glow};
  `}

  &:hover {
    background: ${props => props.theme.glassHover};
    border: 1px solid ${props => props.theme.border};
    
    ${props => !props.$isActive && `
      box-shadow: 0 0 15px ${props.theme.glow};
    `}
  }

  svg {
    color: ${props => props.$isActive ? props.theme.primary : props.theme.textSecondary};
    transition: color 0.3s ease;
    min-width: 20px;
  }
`;

const NavLabel = styled(motion.span)`
  color: ${props => props.$isActive ? props.theme.text : props.theme.textSecondary};
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
  transition: color 0.3s ease;
`;

const NotificationBadge = styled(motion.div)`
  position: absolute;
  top: 8px;
  right: 8px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: ${props => props.theme.accent};
  box-shadow: 0 0 10px ${props => props.theme.accent};
`;

const ExpandButton = styled(motion.div)`
  position: absolute;
  right: -12px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: ${props => props.theme.glass};
  backdrop-filter: blur(10px);
  border: 1px solid ${props => props.theme.border};
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0;
  transition: all 0.3s ease;

  ${SidebarContainer}:hover & {
    opacity: 1;
  }

  &:hover {
    background: ${props => props.theme.glassHover};
    border-color: ${props => props.theme.primary};
  }

  svg {
    color: ${props => props.theme.textSecondary};
    transition: transform 0.3s ease;
    transform: ${props => props.$isExpanded ? 'rotate(180deg)' : 'rotate(0deg)'};
  }
`;

const navigationItems = [
  { id: 'chat', icon: MessageCircle, label: 'Chat', hasNotification: false },
  { id: 'memory', icon: Brain, label: 'Memory', hasNotification: true },
  { id: 'context', icon: Database, label: 'Context', hasNotification: false },
  { id: 'updates', icon: Download, label: 'Updates', hasNotification: true },
  { id: 'security', icon: Shield, label: 'Security', hasNotification: false },
  { id: 'logs', icon: FileText, label: 'Logs', hasNotification: false },
  { id: 'settings', icon: Settings, label: 'Settings', hasNotification: false }
];

const Sidebar = ({ activePanel, onPanelChange }) => {
  const { theme } = useTheme();
  const [isExpanded, setIsExpanded] = useState(false);
  const [isHovered, setIsHovered] = useState(false);

  const handleItemClick = (itemId) => {
    if (onPanelChange) {
      onPanelChange(itemId);
    }
  };

  const sidebarVariants = {
    collapsed: { width: 80 },
    expanded: { width: 220 }
  };

  const labelVariants = {
    hidden: { opacity: 0, x: -10 },
    visible: { opacity: 1, x: 0 }
  };

  const showLabels = isExpanded || isHovered;

  return (
    <SidebarContainer
      theme={theme}
      $isExpanded={showLabels}
      variants={sidebarVariants}
      animate={showLabels ? "expanded" : "collapsed"}
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
    >
      {/* Logo */}
      <Logo>
        <LogoIcon theme={theme}>J</LogoIcon>
        <AnimatePresence>
          {showLabels && (
            <LogoText
              theme={theme}
              variants={labelVariants}
              initial="hidden"
              animate="visible"
              exit="hidden"
              transition={{ duration: 0.2 }}
            >
              JARVIS
            </LogoText>
          )}
        </AnimatePresence>
      </Logo>

      {/* Navigation Items */}
      <NavList>
        {navigationItems.map((item) => {
          const Icon = item.icon;
          const isActive = activePanel === item.id;

          return (
            <NavItem
              key={item.id}
              theme={theme}
              $isActive={isActive}
              onClick={() => handleItemClick(item.id)}
              whileHover={{ x: 2 }}
              whileTap={{ scale: 0.98 }}
            >
              <Icon size={20} />
              
              <AnimatePresence>
                {showLabels && (
                  <NavLabel
                    theme={theme}
                    $isActive={isActive}
                    variants={labelVariants}
                    initial="hidden"
                    animate="visible"
                    exit="hidden"
                    transition={{ duration: 0.2, delay: 0.05 }}
                  >
                    {item.label}
                  </NavLabel>
                )}
              </AnimatePresence>

              {item.hasNotification && (
                <NotificationBadge theme={theme} />
              )}
            </NavItem>
          );
        })}
      </NavList>

      {/* Expand toggle */}
      <ExpandButton theme={theme} $isExpanded={showLabels} onClick={() => setIsExpanded(!isExpanded)}>
        <ChevronRight size={16} />
      </ExpandButton>
    </SidebarContainer>
  );
};

export default Sidebar;