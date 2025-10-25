import React, { useState, useEffect, useRef } from "react";
import {
  sendMessageToJarvis,
  startVoiceRecognition,
  stopVoiceRecognition,
  registerJarvisListener,
} from "../services/socketService";

const ChatPanel = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [listening, setListening] = useState(false);
  const chatEndRef = useRef(null);

  // Scroll to newest message on update
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  // Handle sending a message
  const handleSend = () => {
    const text = input.trim();
    if (!text) return;
    setMessages((prev) => [...prev, { sender: "You", text }]);
    sendMessageToJarvis(text);
    setInput("");
  };

  // Listen for backend (Jarvis) responses
  useEffect(() => {
    registerJarvisListener((data) => {
      setMessages((prev) => [
        ...prev,
        {
          sender: "Jarvis",
          text: data.reply || data.text || JSON.stringify(data),
        },
      ]);
    });
  }, []);

  // Voice control
  const handleMic = () => {
    if (!listening) {
      setListening(true);
      startVoiceRecognition();
    } else {
      setListening(false);
      stopVoiceRecognition();
    }
  };

  // Enter key triggers send
  const handleInputKey = (e) => {
    if (e.key === "Enter") handleSend();
  };

  return (
    <div style={styles.container}>
      <div style={styles.chatBox}>
        {messages.map((m, i) => (
          <div
            key={i}
            style={{
              ...styles.msg,
              alignSelf: m.sender === "You" ? "flex-end" : "flex-start",
              background: m.sender === "You" ? "#215cff" : "#1f1f1f",
            }}
          >
            <span>{m.text}</span>
          </div>
        ))}
        <div ref={chatEndRef} />
      </div>

      <div style={styles.controls}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleInputKey}
          placeholder="Type something..."
          style={styles.input}
        />
        <button onClick={handleSend} style={styles.button}>
          Send
        </button>
        <button
          onClick={handleMic}
          style={{
            ...styles.button,
            background: listening ? "#d33" : "#0d6efd",
            marginLeft: "8px",
          }}
        >
          {listening ? "Stop 🎙️" : "Speak 🎤"}
        </button>
      </div>
    </div>
  );
};

const styles = {
  container: { display: "flex", flexDirection: "column", height: "100%" },
  chatBox: {
    flex: 1,
    overflowY: "auto",
    padding: "1rem",
    background: "#111",
    color: "#fff",
  },
  msg: {
    margin: "8px 0",
    padding: "10px",
    borderRadius: "8px",
    maxWidth: "70%",
    color: "#fff",
    wordBreak: "break-word",
  },
  controls: {
    display: "flex",
    padding: "10px",
    background: "#222",
    alignItems: "center",
  },
  input: { flex: 1, marginRight: "8px", padding: "8px" },
  button: {
    padding: "8px 16px",
    cursor: "pointer",
    border: "none",
    borderRadius: "4px",
    color: "#fff",
  },
};

export default ChatPanel;
