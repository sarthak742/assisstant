import React, { useState, useEffect, useRef } from 'react';
import styled, { keyframes, css } from 'styled-components';
import { motion, AnimatePresence, useSpring, useTransform } from 'framer-motion';
import { useTheme } from '../../contexts/ThemeContext';

const breathe = keyframes`
  0%, 100% { transform: scale(1); filter: brightness(1); }
  50% { transform: scale(1.1); filter: brightness(1.2); }
`;

const pulse = keyframes`
  0%, 100% { 
    box-shadow: 0 0 40px var(--theme-glow);
    filter: brightness(1);
  }
  50% { 
    box-shadow: 0 0 80px var(--theme-glow), 0 0 120px var(--theme-glow);
    filter: brightness(1.3);
  }
`;

const rotate = keyframes`
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
`;

const ripple = keyframes`
  0% { 
    transform: scale(0); 
    opacity: 1; 
    border-width: 3px;
  }
  50% {
    border-width: 1px;
  }
  100% { 
    transform: scale(4); 
    opacity: 0; 
    border-width: 0.5px;
  }
`;

const float = keyframes`
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
`;

const OrbContainer = styled(motion.div)`
  position: relative;
  width: 200px;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  animation: ${float} 8s ease-in-out infinite;
  perspective: 1000px;
`;

const GlowLayer = styled(motion.div)`
  position: absolute;
  width: 140px;
  height: 140px;
  border-radius: 50%;
  background: radial-gradient(circle, ${props => props.theme.glow}30 0%, transparent 70%);
  filter: blur(15px);
  opacity: 0.8;
  z-index: -1;
`;

const MainOrb = styled(motion.div)`
  width: 120px;
  height: 120px;
  border-radius: 50%;
  background: ${props => props.theme.orbGradient};
  position: relative;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(5px);
  transform-style: preserve-3d;
  
  ${props => props.$state === 'idle' && css`
    animation: ${breathe} 4s ease-in-out infinite;
    box-shadow: 0 0 40px ${props.theme.glow}, inset 0 0 20px rgba(255, 255, 255, 0.2);
  `}
  
  ${props => props.$state === 'listening' && css`
    animation: ${pulse} 1.5s ease-in-out infinite;
    box-shadow: 0 0 60px ${props.theme.glow}, 0 0 100px ${props.theme.glow}, inset 0 0 30px rgba(255, 255, 255, 0.3);
  `}
  
  ${props => props.$state === 'speaking' && css`
    animation: ${pulse} 1s ease-in-out infinite;
    box-shadow: 0 0 80px ${props.theme.secondary}, 0 0 120px ${props.theme.secondary}, inset 0 0 40px rgba(255, 255, 255, 0.4);
  `}
  
  ${props => props.$state === 'thinking' && css`
    animation: ${rotate} 3s linear infinite, ${pulse} 2s ease-in-out infinite;
    box-shadow: 0 0 60px ${props.theme.accent}, 0 0 100px ${props.theme.accent}, inset 0 0 35px rgba(255, 255, 255, 0.3);
  `}

  &::before {
    content: '';
    position: absolute;
    top: 15%;
    left: 15%;
    width: 25%;
    height: 25%;
    background: rgba(255, 255, 255, 0.6);
    border-radius: 50%;
    filter: blur(8px);
    transition: all 0.5s ease;
  }

  &::after {
    content: '';
    position: absolute;
    top: 60%;
    right: 20%;
    width: 15%;
    height: 15%;
    background: rgba(255, 255, 255, 0.4);
    border-radius: 50%;
    filter: blur(4px);
    transition: all 0.5s ease;
  }
`;

const WaveformContainer = styled.div`
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 160px;
  height: 160px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
`;

const WaveBar = styled(motion.div)`
  width: 3px;
  background: ${props => props.theme.primary};
  border-radius: 2px;
  margin: 0 1px;
  box-shadow: 0 0 10px ${props => props.theme.glow};
  transform-origin: bottom;
  filter: saturate(1.5) brightness(1.2);
  opacity: 0.8;
`;

const RippleRing = styled(motion.div)`
  position: absolute;
  top: 50%;
  left: 50%;
  border: 2px solid ${props => props.theme.primary};
  border-radius: 50%;
  transform: translate(-50%, -50%);
  pointer-events: none;
  box-shadow: 0 0 15px ${props => props.theme.glow};
`;

const StatusText = styled(motion.div)`
  position: absolute;
  bottom: -40px;
  left: 50%;
  transform: translateX(-50%);
  color: ${props => props.theme.textSecondary};
  font-size: 14px;
  font-weight: 300;
  text-align: center;
  opacity: 0.8;
  text-shadow: 0 0 10px ${props => props.theme.glow}80;
`;

const AIOrb = ({ 
  state = 'idle', 
  onActivate, 
  audioData = [], 
  isListening = false,
  isSpeaking = false,
  isThinking = false 
}) => {
  const { theme } = useTheme();
  const [ripples, setRipples] = useState([]);
  const [waveformData, setWaveformData] = useState(Array(20).fill(0));
  const rippleIdRef = useRef(0);
  const audioRef = useRef(audioData);
  
  // Update audio reference when props change
  useEffect(() => {
    audioRef.current = audioData;
  }, [audioData]);

  // Generate waveform animation based on audio data or simulation
  useEffect(() => {
    if (isListening || isSpeaking) {
      const interval = setInterval(() => {
        if (audioRef.current && audioRef.current.length > 0) {
          // Use real audio data if available
          const normalizedData = audioRef.current.map(val => 
            Math.min(Math.abs(val) * 100, 50) + 5
          );
          setWaveformData(normalizedData.slice(0, 20).concat(Array(Math.max(0, 20 - normalizedData.length)).fill(0)));
        } else {
          // Simulate audio data with organic movement
          setWaveformData(prev => 
            prev.map((val, i) => {
              const target = Math.random() * 40 + 10;
              const speed = 0.3; // Smoother transition
              return val + (target - val) * speed;
            })
          );
        }
      }, 50); // More frequent updates for smoother animation
      return () => clearInterval(interval);
    } else {
      // Gradually reduce heights to zero for smooth transition
      const interval = setInterval(() => {
        setWaveformData(prev => 
          prev.map(val => val > 0.5 ? val * 0.9 : 0)
        );
      }, 50);
      return () => clearInterval(interval);
    }
  }, [isListening, isSpeaking]);

  // Handle orb activation
  const handleOrbClick = () => {
    // Create ripple effect with enhanced animation
    const newRipple = {
      id: rippleIdRef.current++,
      size: 120,
      color: theme.primary
    };
    setRipples(prev => [...prev, newRipple]);
    
    // Remove ripple after animation
    setTimeout(() => {
      setRipples(prev => prev.filter(r => r.id !== newRipple.id));
    }, 1500);

    if (onActivate) {
      onActivate();
    }
  };

  const getStatusText = () => {
    switch (state) {
      case 'listening': return 'Listening...';
      case 'speaking': return 'Speaking...';
      case 'thinking': return 'Thinking...';
      case 'idle': return 'Say "Hey Jarvis" to activate';
      default: return '';
    }
  };

  const orbVariants = {
    idle: { scale: 1, rotateY: 0 },
    hover: { scale: 1.05, rotateY: 10 },
    active: { scale: 0.95, rotateY: -5 }
  };

  return (
    <OrbContainer
      animate={{ y: [0, -5, 0] }}
      transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
    >
      {/* Glow layer */}
      <GlowLayer 
        theme={theme}
        animate={{ 
          scale: state === 'idle' ? [1, 1.1, 1] : [1, 1.2, 1],
          opacity: state === 'idle' ? [0.6, 0.8, 0.6] : [0.7, 0.9, 0.7]
        }}
        transition={{ 
          duration: state === 'idle' ? 4 : 2, 
          repeat: Infinity,
          ease: "easeInOut"
        }}
      />

      {/* Ripple effects */}
      <AnimatePresence>
        {ripples.map(ripple => (
          <RippleRing
            key={ripple.id}
            theme={theme}
            initial={{ width: ripple.size, height: ripple.size, opacity: 1, borderColor: ripple.color }}
            animate={{ width: ripple.size * 4, height: ripple.size * 4, opacity: 0, borderColor: theme.accent }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1.5, ease: "easeOut" }}
          />
        ))}
      </AnimatePresence>

      {/* Waveform visualization */}
      {(isListening || isSpeaking) && (
        <WaveformContainer>
          {waveformData.map((height, index) => (
            <WaveBar
              key={index}
              theme={theme}
              animate={{ 
                height: `${height}px`,
                backgroundColor: isSpeaking 
                  ? theme.secondary 
                  : theme.primary,
                opacity: height > 20 ? 1 : 0.7
              }}
              transition={{ 
                duration: 0.1,
                ease: "easeOut"
              }}
            />
          ))}
        </WaveformContainer>
      )}

      {/* Main orb */}
      <MainOrb
        theme={theme}
        $state={state}
        variants={orbVariants}
        initial="idle"
        whileHover="hover"
        whileTap="active"
        onClick={handleOrbClick}
        animate={{ 
          rotateY: isThinking ? [0, 180, 360] : 0,
          rotateZ: isThinking ? [0, 180, 360] : 0
        }}
        transition={{ 
          duration: 8, 
          repeat: isThinking ? Infinity : 0,
          ease: "linear"
        }}
      />

      {/* Status text */}
      <StatusText
        theme={theme}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 0.8, y: 0 }}
        transition={{ duration: 0.3 }}
      >
        {getStatusText()}
      </StatusText>
    </OrbContainer>
  );
};

export default AIOrb;