import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Mic, MicOff, Volume2, VolumeX } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';
import { GlassInput, GlassButton } from '../Glass/GlassComponents';
import useVoiceInteraction from '../../hooks/useVoiceInteraction';

const MessageBubble = styled(motion.div)`
  display: flex;
  flex-direction: column;
  padding: 16px 20px;
  background: ${props => props.theme.glass};
  backdrop-filter: blur(15px);
  border: 1px solid ${props => props.theme.border};
  border-radius: 20px;
  max-width: 80%;
  align-self: ${props => props.$isUser ? 'flex-end' : 'flex-start'};
  position: relative;
  transform-style: preserve-3d;
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
  
  &:hover {
    transform: translateY(-2px) scale(1.01);
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  }
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    border-radius: inherit;
    background: linear-gradient(
      135deg,
      rgba(255, 255, 255, 0.2) 0%,
      rgba(255, 255, 255, 0.05) 50%,
      rgba(255, 255, 255, 0) 100%
    );
    z-index: -1;
    opacity: 0.5;
    transition: opacity 0.3s ease;
  }
  
  &:hover::before {
    opacity: 0.8;
  }
  
  ${props => props.$isUser ? `
    border-bottom-right-radius: 4px;
    border-color: ${props.theme.primary};
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1), 0 0 0 1px ${props.theme.primary}40;
    
    &::after {
      content: '';
      position: absolute;
      bottom: -5px;
      right: 10px;
      width: 10px;
      height: 10px;
      background: ${props.theme.glass};
      border-right: 1px solid ${props.theme.primary};
      border-bottom: 1px solid ${props.theme.primary};
      transform: rotate(45deg);
      z-index: -1;
    }
  ` : `
    border-bottom-left-radius: 4px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    
    &::after {
      content: '';
      position: absolute;
      bottom: -5px;
      left: 10px;
      width: 10px;
      height: 10px;
      background: ${props.theme.glass};
      border-left: 1px solid ${props.theme.border};
      border-bottom: 1px solid ${props.theme.border};
      transform: rotate(45deg);
      z-index: -1;
    }
  `}
`;

const ChatContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  position: relative;
`;

const MessagesContainer = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
  
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

const InputContainer = styled.div`
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 20px 0;
`;

const InputWrapper = styled.div`
  flex: 1;
  position: relative;
`;

const VoiceIndicator = styled(motion.div)`
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: ${props => props.$isActive ? props.theme.primary : 'transparent'};
  box-shadow: ${props => props.$isActive ? `0 0 10px ${props.theme.glow}, 0 0 20px ${props.theme.primary}40` : 'none'};
  transition: background 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease;
  
  &::before {
    content: '';
    position: absolute;
    top: -4px;
    left: -4px;
    right: -4px;
    bottom: -4px;
    border-radius: 50%;
    background: radial-gradient(
      circle,
      ${props => props.theme.primary}40 0%,
      transparent 70%
    );
    opacity: ${props => props.$isActive ? 0.8 : 0};
    transition: opacity 0.3s ease;
    filter: blur(2px);
  }
`;

const ControlButton = styled(GlassButton)`
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  
  ${props => props.isActive && `
    background: ${props.theme.glass};
    border-color: ${props.theme.primary};
    box-shadow: 0 0 20px ${props.theme.glow};
  `}
`;

const TypingIndicator = styled(motion.div)`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 16px 20px;
  background: ${props => props.theme.glass};
  backdrop-filter: blur(15px);
  border: 1px solid ${props => props.theme.border};
  border-radius: 20px;
  align-self: flex-start;
  margin: 8px 0;
  position: relative;
  overflow: hidden;
  
  &::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(
      135deg,
      rgba(255, 255, 255, 0.1) 0%,
      rgba(255, 255, 255, 0.05) 50%,
      rgba(255, 255, 255, 0) 100%
    );
    z-index: -1;
  }
  
  &::after {
    content: '';
    position: absolute;
    width: 100%;
    height: 100%;
    background: linear-gradient(
      90deg,
      transparent,
      rgba(255, 255, 255, 0.1),
      transparent
    );
    transform: translateX(-100%);
    animation: shimmer 2s infinite;
  }
  
  @keyframes shimmer {
    100% {
      transform: translateX(100%);
    }
  }
`;

const TypingDot = styled(motion.div)`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: ${props => props.theme.primary};
  filter: drop-shadow(0 0 2px ${props => props.theme.primary});
  position: relative;
  
  &::before {
    content: '';
    position: absolute;
    top: -2px;
    left: -2px;
    right: -2px;
    bottom: -2px;
    border-radius: 50%;
    background: ${props => props.theme.primary}40;
    filter: blur(2px);
    opacity: 0.7;
  }
`;

const MessageText = styled.div`
  color: ${props => props.theme.text};
  font-size: 14px;
  line-height: 1.5;
  word-wrap: break-word;
`;

const MessageTime = styled.div`
  color: ${props => props.theme.textSecondary};
  font-size: 12px;
  margin-top: 8px;
  opacity: 0.7;
`;

const VoiceModeToggle = styled(motion.div)`
  position: absolute;
  top: -40px;
  right: 0;
  background: ${props => props.theme.glass};
  backdrop-filter: blur(15px);
  border: 1px solid ${props => props.theme.border};
  border-radius: 20px;
  padding: 8px 16px;
  font-size: 12px;
  color: ${props => props.theme.textSecondary};
  cursor: pointer;
  
  &:hover {
    background: ${props => props.theme.glassHover};
    border-color: ${props => props.theme.primary};
  }
`;

const ChatInterface = ({ onSendMessage, messages = [], isTyping = false }) => {
  const { theme } = useTheme();
  const [inputValue, setInputValue] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  
  const {
    isListening,
    isSpeaking,
    isSupported,
    transcript,
    voiceMode,
    startListening,
    stopListening,
    speak,
    stopSpeaking,
    toggleVoiceMode,
    clearTranscript,
    setWakeWordHandler
  } = useVoiceInteraction();

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  // Handle voice transcript
  useEffect(() => {
    if (transcript && !isListening) {
      const text = (transcript || '').trim();
      setInputValue(text);
      if (text && onSendMessage) {
        onSendMessage(text);
      }
      clearTranscript();
    }
  }, [transcript, isListening, clearTranscript, onSendMessage]);

  // Wire wake word command handler to send message automatically
  useEffect(() => {
    setWakeWordHandler((command) => {
      const text = (command || '').trim();
      if (text && onSendMessage) {
        onSendMessage(text);
      }
    });
    return () => setWakeWordHandler(null);
  }, [setWakeWordHandler, onSendMessage]);

  // Auto speak latest assistant message (if voice mode is not text)
  useEffect(() => {
    if (!isSupported || voiceMode === 'text') return;
    const lastAI = messages.filter(m => !m.isUser).pop();
    if (lastAI && lastAI.text) {
      try { speak(lastAI.text); } catch (e) { /* noop */ }
    }
  }, [messages, isSupported, voiceMode, speak]);

  const handleSendMessage = () => {
    if (inputValue.trim() && onSendMessage) {
      onSendMessage(inputValue.trim());
      setInputValue('');
      
      // Focus back to input
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleVoiceToggle = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  const handleSpeakToggle = () => {
    if (isSpeaking) {
      stopSpeaking();
    } else {
      // Speak the last AI message
      const lastAIMessage = messages.filter(m => !m.isUser).pop();
      if (lastAIMessage) {
        speak(lastAIMessage.text);
      }
    }
  };

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const messageVariants = {
    hidden: { opacity: 0, y: 20, scale: 0.8 },
    visible: { 
      opacity: 1, 
      y: 0, 
      scale: 1,
      transition: { 
        type: "spring", 
        stiffness: 500, 
        damping: 30 
      }
    },
    exit: { 
      opacity: 0, 
      y: -20, 
      scale: 0.8,
      transition: { duration: 0.2 }
    }
  };

  const typingVariants = {
    hidden: { opacity: 0 },
    visible: { opacity: 1 },
    exit: { opacity: 0 }
  };

  const dotVariants = {
    start: { y: 0 },
    end: { y: -10 }
  };

  return (
    <ChatContainer>
      <MessagesContainer theme={theme}>
        <AnimatePresence>
          {messages.map((message, index) => (
            <MessageBubble
              key={message.id || index}
              theme={theme}
              $isUser={message.isUser}
              variants={messageVariants}
              initial="hidden"
              animate="visible"
              exit="exit"
              layout
            >
              <MessageText theme={theme}>
                {message.text}
              </MessageText>
              {message.timestamp && (
                <MessageTime theme={theme}>
                  {formatTime(message.timestamp)}
                </MessageTime>
              )}
            </MessageBubble>
          ))}
        </AnimatePresence>

        {/* Typing indicator */}
        <AnimatePresence>
          {isTyping && (
            <TypingIndicator
              theme={theme}
              variants={typingVariants}
              initial="hidden"
              animate="visible"
              exit="exit"
            >
              <span style={{ color: theme.textSecondary, fontSize: '14px' }}>
                Jarvis is thinking
              </span>
              {[0, 1, 2].map((i) => (
                <TypingDot
                  key={i}
                  theme={theme}
                  variants={dotVariants}
                  animate="end"
                  transition={{
                    duration: 0.6,
                    repeat: Infinity,
                    repeatType: "reverse",
                    delay: i * 0.2
                  }}
                />
              ))}
            </TypingIndicator>
          )}
        </AnimatePresence>

        <div ref={messagesEndRef} />
      </MessagesContainer>

      <InputContainer>
        <InputWrapper>
          {/* Voice mode indicator */}
          {voiceMode !== 'text' && (
            <VoiceModeToggle
              theme={theme}
              onClick={toggleVoiceMode}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              Mode: {voiceMode}
            </VoiceModeToggle>
          )}

          <GlassInput
            ref={inputRef}
            theme={theme}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={
              isListening 
                ? "Listening..." 
                : voiceMode === 'full' 
                  ? 'Say "Hey Jarvis" or type here...'
                  : "Type your message..."
            }
            disabled={isListening}
          />

          <VoiceIndicator
            theme={theme}
            $isActive={isListening}
            animate={{ scale: isListening ? [1, 1.2, 1] : 1 }}
            transition={{ duration: 1, repeat: isListening ? Infinity : 0 }}
          />
        </InputWrapper>

        {/* Voice controls */}
        {isSupported && voiceMode !== 'text' && (
          <ControlButton
            theme={theme}
            onClick={handleVoiceToggle}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {isListening ? <MicOff size={20} /> : <Mic size={20} />}
          </ControlButton>
        )}

        {/* Speak toggle */}
        {isSupported && (
          <ControlButton
            theme={theme}
            onClick={handleSpeakToggle}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            {isSpeaking ? <VolumeX size={20} /> : <Volume2 size={20} />}
          </ControlButton>
        )}

        {/* Send button */}
        <ControlButton
          theme={theme}
          onClick={handleSendMessage}
          disabled={!inputValue.trim()}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          <Send size={20} />
        </ControlButton>
      </InputContainer>
    </ChatContainer>
  );
};

export default ChatInterface;