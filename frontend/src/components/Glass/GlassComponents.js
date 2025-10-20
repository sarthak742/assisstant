import styled, { keyframes, css } from 'styled-components';
import { motion } from 'framer-motion';

// Keyframe animations
const breathe = keyframes`
  0%, 100% { transform: scale(1); opacity: 0.8; }
  50% { transform: scale(1.05); opacity: 1; }
`;

const pulse = keyframes`
  0%, 100% { box-shadow: 0 0 20px var(--theme-glow); }
  50% { box-shadow: 0 0 40px var(--theme-glow), 0 0 60px var(--theme-glow); }
`;

const ripple = keyframes`
  0% { transform: scale(0); opacity: 1; }
  100% { transform: scale(4); opacity: 0; }
`;

const float = keyframes`
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
`;

const shimmer = keyframes`
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
`;

// Base glass container
export const GlassContainer = styled(motion.div)`
  background: ${props => props.theme?.glass || 'rgba(255, 255, 255, 0.1)'};
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid ${props => props.theme?.border || 'rgba(255, 255, 255, 0.2)'};
  border-radius: 20px;
  box-shadow: ${props => props.theme?.shadow || '0 8px 32px rgba(0, 0, 0, 0.3)'};
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;

  /* Enhanced glass reflection effect */
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 200%;
    height: 100%;
    background: linear-gradient(
      120deg,
      transparent 20%,
      rgba(255, 255, 255, 0.1) 25%,
      rgba(255, 255, 255, 0.15) 27%,
      transparent 30%
    );
    transform: rotate(-45deg);
    animation: ${shimmer} 8s infinite linear;
    pointer-events: none;
  }

  /* Top edge highlight */
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, ${props => props.theme?.accent || '#fff'}, transparent);
    opacity: 0.5;
  }

  &:hover {
    background: ${props => props.theme?.glassHover || 'rgba(255, 255, 255, 0.15)'};
    border-color: ${props => props.theme?.primary || '#fff'};
    transform: translateY(-2px);
    box-shadow: ${props => `0 10px 40px ${props.theme?.glow || 'rgba(0, 0, 0, 0.4)'}30`};
  }
`;

// Floating panel with enhanced glass effect
export const FloatingPanel = styled(GlassContainer)`
  position: fixed;
  z-index: 1000;
  min-width: 300px;
  max-width: 500px;
  padding: 24px;
  animation: ${float} 6s ease-in-out infinite;
  transform-style: preserve-3d;
  perspective: 1000px;

  ${props => props.isVisible && css`
    animation: ${float} 6s ease-in-out infinite;
  `}
  
  /* Enhanced 3D lighting effect */
  &::before {
    animation: ${shimmer} 10s infinite linear;
  }
  
  /* Subtle inner shadow for depth */
  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    box-shadow: inset 0 0 30px rgba(0, 0, 0, 0.1);
    border-radius: inherit;
    pointer-events: none;
  }
`;

// Main interface container
export const MainContainer = styled.div`
  width: 100vw;
  height: 100vh;
  background: ${props => props.theme?.background || '#0A0F1C'};
  background-image: 
    radial-gradient(circle at 20% 80%, ${props => props.theme?.primary || '#00D4FF'}15 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, ${props => props.theme?.secondary || '#0099CC'}15 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, ${props => props.theme?.accent || '#66E5FF'}10 0%, transparent 50%);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: background 0.5s ease-in-out, background-image 0.8s ease-in-out;
`;

// AI Orb container
export const OrbContainer = styled(motion.div)`
  position: relative;
  width: 120px;
  height: 120px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
`;

export const AIOrb = styled(motion.div)`
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: ${props => props.theme?.orbGradient || 'radial-gradient(circle, #00D4FF 0%, #0099CC 50%, #003D52 100%)'};
  box-shadow: 
    0 0 40px ${props => props.theme?.glow || '#00D4FF'},
    inset 0 0 40px rgba(255, 255, 255, 0.1);
  position: relative;
  
  ${props => props.isIdle && css`
    animation: ${breathe} 4s ease-in-out infinite;
  `}
  
  ${props => props.isActive && css`
    animation: ${pulse} 2s ease-in-out infinite;
  `}

  &::before {
    content: '';
    position: absolute;
    top: 10%;
    left: 10%;
    width: 30%;
    height: 30%;
    background: rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    filter: blur(10px);
  }
`;

// Ripple effect for wake word activation
export const RippleEffect = styled(motion.div)`
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100px;
  height: 100px;
  border: 2px solid ${props => props.theme?.primary || '#00D4FF'};
  border-radius: 50%;
  transform: translate(-50%, -50%);
  animation: ${ripple} 1.5s ease-out;
  pointer-events: none;
`;

// Chat message bubble
export const MessageBubble = styled(motion.div)`
  background: ${props => props.theme?.glass || 'rgba(255, 255, 255, 0.1)'};
  backdrop-filter: blur(15px);
  border: 1px solid ${props => props.theme?.border || 'rgba(255, 255, 255, 0.2)'};
  border-radius: 20px;
  padding: 16px 20px;
  margin: 8px 0;
  max-width: 70%;
  position: relative;
  transform-style: preserve-3d;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  
  ${props => props.isUser ? css`
    align-self: flex-end;
    background: linear-gradient(135deg, ${props.theme?.primary || '#00D4FF'}20, ${props.theme?.secondary || '#0099CC'}10);
    border-color: ${props.theme?.primary || '#00D4FF'};
    box-shadow: 0 5px 15px ${props.theme?.primary || '#00D4FF'}20;
    
    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: linear-gradient(135deg, transparent, rgba(255, 255, 255, 0.2), transparent);
      border-radius: inherit;
      opacity: 0.5;
      pointer-events: none;
    }
  ` : css`
    align-self: flex-start;
    background: ${props.theme?.glass || 'rgba(255, 255, 255, 0.1)'};
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    
    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: linear-gradient(135deg, transparent, rgba(255, 255, 255, 0.1), transparent);
      border-radius: inherit;
      opacity: 0.3;
      pointer-events: none;
    }
  `}

  &::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(45deg, transparent 30%, ${props => props.theme?.accent || '#fff'}50, transparent 70%);
    background-size: 200% 200%;
    border-radius: inherit;
    opacity: 0;
    animation: ${shimmer} 3s ease-in-out infinite;
    pointer-events: none;
    transition: opacity 0.3s ease;
  }

  &:hover::after {
    opacity: 0.15;
  }
  
  &:hover {
    transform: translateY(-2px) scale(1.01);
  }
`;

// Navigation sidebar
export const Sidebar = styled(motion.div)`
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  width: 80px;
  background: ${props => props.theme?.glass || 'rgba(255, 255, 255, 0.05)'};
  backdrop-filter: blur(20px);
  border-right: 1px solid ${props => props.theme?.border || 'rgba(255, 255, 255, 0.1)'};
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px 0;
  z-index: 100;
  transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    width: 200px;
  }
`;

// Navigation item
export const NavItem = styled(motion.div)`
  width: 50px;
  height: 50px;
  border-radius: 15px;
  background: ${props => props.isActive ? props.theme?.glass : 'transparent'};
  border: 1px solid ${props => props.isActive ? props.theme?.primary : 'transparent'};
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 10px 0;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &:hover {
    background: ${props => props.theme?.glassHover || 'rgba(255, 255, 255, 0.1)'};
    border-color: ${props => props.theme?.primary || '#fff'};
    box-shadow: 0 0 20px ${props => props.theme?.glow || '#fff'};
  }

  svg {
    color: ${props => props.isActive ? props.theme?.primary : props.theme?.textSecondary};
    transition: color 0.3s ease;
  }
`;

// Status bar
export const StatusBar = styled.div`
  position: fixed;
  top: 20px;
  right: 20px;
  display: flex;
  gap: 15px;
  z-index: 100;
`;

export const StatusIndicator = styled.div`
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: ${props => props.isActive ? props.theme?.primary : props.theme?.textSecondary};
  box-shadow: ${props => props.isActive ? `0 0 10px ${props.theme?.glow}` : 'none'};
  transition: all 0.3s ease;
`;

// Input field
export const GlassInput = styled.input`
  background: ${props => props.theme?.glass || 'rgba(255, 255, 255, 0.1)'};
  backdrop-filter: blur(15px);
  border: 1px solid ${props => props.theme?.border || 'rgba(255, 255, 255, 0.2)'};
  border-radius: 15px;
  padding: 12px 16px;
  color: ${props => props.theme?.text || '#fff'};
  font-size: 14px;
  outline: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &::placeholder {
    color: ${props => props.theme?.textSecondary || 'rgba(255, 255, 255, 0.5)'};
  }

  &:focus {
    border-color: ${props => props.theme?.primary || '#fff'};
    box-shadow: 0 0 20px ${props => props.theme?.glow || '#fff'};
    background: ${props => props.theme?.glassHover || 'rgba(255, 255, 255, 0.15)'};
  }
`;

// Button
export const GlassButton = styled(motion.button)`
  background: ${props => props.theme?.glass || 'rgba(255, 255, 255, 0.1)'};
  backdrop-filter: blur(15px);
  border: 1px solid ${props => props.theme?.border || 'rgba(255, 255, 255, 0.2)'};
  border-radius: 12px;
  padding: 10px 20px;
  color: ${props => props.theme?.text || '#fff'};
  font-size: 14px;
  cursor: pointer;
  outline: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;

  &:hover {
    background: ${props => props.theme?.glassHover || 'rgba(255, 255, 255, 0.15)'};
    border-color: ${props => props.theme?.primary || '#fff'};
    box-shadow: 0 0 20px ${props => props.theme?.glow || '#fff'};
    transform: translateY(-1px);
  }

  &:active {
    transform: translateY(0);
  }
`;