import React, { useState, useRef, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { addMessage, sendMessage, textToSpeech } from '../redux/slices/chatSlice';
import { setVoiceActive, setListening } from '../redux/slices/appSlice';
import VoiceService from '../services/voice';
import { fetchRecentInteractions } from '../redux/slices/memorySlice';

const ChatInterface = () => {
  const dispatch = useDispatch();
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  
  const { messages, isProcessing } = useSelector((state) => state.chat);
  const { isVoiceActive, isListening } = useSelector((state) => state.app);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load recent memory interactions into chat on mount
  useEffect(() => {
    dispatch(fetchRecentInteractions(15)).then((result) => {
      const interactions = result?.payload || [];
      interactions.forEach((it) => {
        dispatch(addMessage({
          content: it.content || it.text || '',
          sender: it.sender || (it.role === 'user' ? 'user' : 'jarvis'),
          type: 'text',
          timestamp: it.timestamp || new Date().toISOString(),
        }));
      });
    });
  }, [dispatch]);
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!inputText.trim() || isProcessing) return;

    // Add user message to chat
    dispatch(addMessage({
      content: inputText,
      sender: 'user',
      type: 'text'
    }));

    // Send to backend
    dispatch(sendMessage(inputText))
      .then((response) => {
        // If voice is active, speak the response via browser or backend
        const responseText = response?.payload?.response;
        if (isVoiceActive && responseText) {
          VoiceService.speak(responseText);
          // Also try backend TTS if available
          dispatch(textToSpeech(responseText));
        }
      });

    // Clear input
    setInputText('');
  };

  const toggleVoiceRecognition = () => {
    if (isListening) {
      dispatch(setListening(false));
      VoiceService.stopRecognition();
    } else {
      dispatch(setListening(true));
      VoiceService.startRecognition()
        .then((result) => {
          if (result?.text) {
            setInputText(result.text);
            // Auto-send if we got text
            handleSendMessage({ preventDefault: () => {} });
          }
        })
        .catch((error) => {
          console.error('Voice recognition error:', error);
          dispatch(setListening(false));
        });
    }
  };

  const renderMessage = (message) => {
    const isUser = message.sender === 'user';
    
    return (
      <div 
        key={message.id} 
        className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 animate-fade-in`}
      >
        <div 
          className={`max-w-3/4 rounded-lg px-4 py-2 ${
            isUser 
              ? 'bg-primary text-white rounded-tr-none' 
              : 'bg-surface border border-opacity-20 border-white rounded-tl-none'
          }`}
        >
          {message.content}
          <div className={`text-xs mt-1 opacity-70 ${isUser ? 'text-right' : ''}`}>
            {new Date(message.timestamp).toLocaleTimeString()}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="flex-1 flex flex-col h-full">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center opacity-50">
            <div className="text-6xl mb-4">👋</div>
            <h2 className="text-2xl mb-2">Welcome to Jarvis</h2>
            <p>How can I assist you today?</p>
          </div>
        ) : (
          messages.map(renderMessage)
        )}
        
        {/* Thinking indicator */}
        {isProcessing && (
          <div className="flex justify-start mb-4">
            <div className="bg-surface border border-opacity-20 border-white rounded-lg rounded-tl-none px-4 py-2">
              <div className="flex space-x-2">
                <div className="w-2 h-2 rounded-full bg-primary animate-pulse"></div>
                <div className="w-2 h-2 rounded-full bg-primary animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                <div className="w-2 h-2 rounded-full bg-primary animate-pulse" style={{ animationDelay: '0.4s' }}></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      {/* Input area */}
      <div className="border-t border-opacity-20 border-white p-4">
        <form onSubmit={handleSendMessage} className="flex items-center">
          <button
            type="button"
            onClick={toggleVoiceRecognition}
            className={`p-2 rounded-full mr-2 ${
              isListening 
                ? 'bg-red-500 animate-pulse' 
                : 'bg-primary hover:bg-opacity-80'
            }`}
          >
            <span role="img" aria-label="microphone">🎤</span>
          </button>
          
          <input
            ref={inputRef}
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder={isListening ? "Listening..." : "Type your message..."}
            className="jarvis-input flex-1 mr-2"
            disabled={isListening || isProcessing}
          />
          
          <button
            type="submit"
            disabled={!inputText.trim() || isProcessing}
            className={`jarvis-button ${
              !inputText.trim() || isProcessing ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatInterface;