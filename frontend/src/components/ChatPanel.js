import React, { useState, useEffect, useRef } from "react";
import ApiService from "../services/api";
import "./ChatPanel.css";

const ChatPanel = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [listening, setListening] = useState(false);
  const [loading, setLoading] = useState(false);
  const [connected, setConnected] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  useEffect(() => {
    // Check connection status
    const checkConnection = () => {
      setConnected(true);
    };
    
    ApiService.addEventListener("connect", checkConnection);
    
    return () => {
      ApiService.removeEventListener("connect", checkConnection);
    };
  }, []);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    
    const userMsg = { 
      sender: "user", 
      text: input, 
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const response = await ApiService.sendMessage(input);
      
      if (response && (response.reply || response.response || response.message)) {
        setMessages((prev) => [
          ...prev,
          { 
            sender: "jarvis", 
            text: response.reply || response.response || response.message, 
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }
        ]);
      }
    } catch (err) {
      console.error("Chat send error:", err);
      setMessages((prev) => [
        ...prev,
        { 
          sender: "jarvis", 
          text: "⚠️ Connection error. Please check if the backend is running.", 
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          isError: true
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const toggleMic = async () => {
    try {
      if (!listening) {
        setListening(true);
        await ApiService.startVoiceRecognition();
        setMessages((prev) => [
          ...prev,
          { 
            sender: "system", 
            text: "🎤 Listening for your voice...", 
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }
        ]);
      } else {
        await ApiService.stopVoiceRecognition();
        setListening(false);
        setMessages((prev) => [
          ...prev,
          { 
            sender: "system", 
            text: "⏹️ Voice recognition stopped.", 
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          }
        ]);
      }
    } catch (error) {
      console.error("Voice control failed:", error);
      setListening(false);
      setMessages((prev) => [
        ...prev,
        { 
          sender: "system", 
          text: "❌ Voice recognition unavailable. Check backend.", 
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          isError: true
        }
      ]);
    }
  };

  useEffect(() => {
    const handleResponse = (data) => {
      setMessages((prev) => [
        ...prev,
        { 
          sender: "jarvis", 
          text: data.reply || data.text || data.message || JSON.stringify(data), 
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ]);
      setListening(false);
    };

    ApiService.addEventListener("chat_response", handleResponse);
    ApiService.addEventListener("jarvis_response", handleResponse);

    return () => {
      ApiService.removeEventListener("chat_response", handleResponse);
      ApiService.removeEventListener("jarvis_response", handleResponse);
    };
  }, []);

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-panel">
      <div className="chat-header">
        <div className="chat-header-content">
          <h3>💬 Jarvis AI Assistant</h3>
          <span className="chat-subtitle">Hybrid Chat & Voice Interface</span>
        </div>
        <div className={`connection-indicator ${connected ? 'connected' : 'disconnected'}`}>
          <span className="indicator-dot"></span>
          {connected ? 'Connected' : 'Disconnected'}
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="welcome-message">
            <div className="wave">👋</div>
            <p className="welcome-title">Hello! I'm Jarvis.</p>
            <p className="welcome-subtitle">How can I assist you today?</p>
            <div className="quick-actions">
              <button className="quick-action" onClick={() => setInput("Tell me a joke")}>
                😄 Tell me a joke
              </button>
              <button className="quick-action" onClick={() => setInput("What can you do?")}>
                🤖 What can you do?
              </button>
            </div>
          </div>
        )}
        
        {messages.map((m, i) => (
          <div key={i} className={`message message-${m.sender} ${m.isError ? 'message-error' : ''}`}>
            <div className="message-content">
              <span className="message-text">{m.text}</span>
              {m.timestamp && <span className="message-time">{m.timestamp}</span>}
            </div>
          </div>
        ))}
        
        {loading && (
          <div className="message message-jarvis">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message or use voice..."
          className="chat-input"
          disabled={loading}
        />
        <button 
          onClick={handleSend} 
          className="send-button"
          disabled={loading || !input.trim()}
          title="Send message"
        >
          {loading ? "⏳" : "📤"}
        </button>
        <button 
          onClick={toggleMic} 
          className={`mic-button ${listening ? 'listening' : ''}`}
          title={listening ? "Stop listening" : "Start voice input"}
        >
          {listening ? "🔴" : "🎤"}
        </button>
      </div>
    </div>
  );
};

export default ChatPanel;


