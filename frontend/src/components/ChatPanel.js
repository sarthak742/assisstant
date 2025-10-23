import React, { useState, useEffect, useRef } from "react";
import ApiService from "../services/api";
import "./ChatPanel.css";

const ChatPanel = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [listening, setListening] = useState(false);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  // Handle text send
  const handleSend = async () => {
    if (!input.trim() || loading) return;
    
    const userMsg = { sender: "user", text: input, timestamp: new Date().toLocaleTimeString() };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const response = await ApiService.sendMessage(input);
      if (response && (response.reply || response.response)) {
        setMessages((prev) => [
          ...prev,
          { 
            sender: "jarvis", 
            text: response.reply || response.response, 
            timestamp: new Date().toLocaleTimeString() 
          }
        ]);
      }
    } catch (err) {
      console.error("Chat send error:", err);
      setMessages((prev) => [
        ...prev,
        { 
          sender: "jarvis", 
          text: "I'm having trouble connecting. Please check the backend.", 
          timestamp: new Date().toLocaleTimeString(),
          isError: true
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  // Handle voice start/stop
  const toggleMic = async () => {
    try {
      if (!listening) {
        setListening(true);
        await ApiService.startVoiceRecognition();
        setMessages((prev) => [
          ...prev,
          { 
            sender: "system", 
            text: "🎤 Listening...", 
            timestamp: new Date().toLocaleTimeString() 
          }
        ]);
      } else {
        await ApiService.stopVoiceRecognition();
        setListening(false);
      }
    } catch (error) {
      console.error("Voice control failed:", error);
      setListening(false);
    }
  };

  // Handle backend responses
  useEffect(() => {
    const handleResponse = (data) => {
      setMessages((prev) => [
        ...prev,
        { 
          sender: "jarvis", 
          text: data.reply || data.text || JSON.stringify(data), 
          timestamp: new Date().toLocaleTimeString() 
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
        <h3>💬 Jarvis AI Assistant</h3>
        <span className="chat-subtitle">Chat or speak with me</span>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="welcome-message">
            <span className="wave">👋</span>
            <p>Hello! I'm Jarvis. How can I help you today?</p>
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
          placeholder="Type your message..."
          className="chat-input"
          disabled={loading}
        />
        <button 
          onClick={handleSend} 
          className="send-button"
          disabled={loading || !input.trim()}
        >
          📤
        </button>
        <button 
          onClick={toggleMic} 
          className={`mic-button ${listening ? 'listening' : ''}`}
        >
          {listening ? "🔴" : "🎤"}
        </button>
      </div>
    </div>
  );
};

export default ChatPanel;

