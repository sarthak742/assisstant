import React, { useState, useEffect } from "react";
import ApiService from "../services/api";

const ChatPanel = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [listening, setListening] = useState(false);

  // Handle text send
  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = { sender: "user", text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    try {
      const response = await ApiService.sendMessage(input);
      if (response && response.reply) {
        setMessages((prev) => [...prev, { sender: "jarvis", text: response.reply }]);
      }
    } catch (err) {
      console.error("Chat send error:", err);
    }
  };

  // Handle voice start/stop
  const toggleMic = async () => {
    try {
      if (!listening) {
        setListening(true);
        await ApiService.startVoiceRecognition();
      } else {
        await ApiService.stopVoiceRecognition();
        setListening(false);
      }
    } catch (error) {
      console.error("Voice control failed:", error);
    }
  };

  // Handle backend responses from recognition
  useEffect(() => {
    ApiService.addEventListener("chat_response", (data) => {
      setMessages((prev) => [...prev, { sender: "jarvis", text: data.reply || JSON.stringify(data) }]);
    });
    return () => ApiService.disconnectSocket();
  }, []);

  return (
    <div style={styles.container}>
      <div style={styles.chatBox}>
        {messages.map((m, i) => (
          <div key={i} style={{ ...styles.msg, alignSelf: m.sender === "user" ? "flex-end" : "flex-start" }}>
            <span>{m.text}</span>
          </div>
        ))}
      </div>

      <div style={styles.controls}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type something..."
          style={styles.input}
        />
        <button onClick={handleSend} style={styles.button}>Send</button>
        <button onClick={toggleMic} style={{ ...styles.button, background: listening ? "#d33" : "#0d6efd" }}>
          {listening ? "Stop 🎙️" : "Speak 🎤"}
        </button>
      </div>
    </div>
  );
};

const styles = {
  container: { display: "flex", flexDirection: "column", height: "100%" },
  chatBox: { flex: 1, overflowY: "auto", padding: "1rem", background: "#111", color: "#fff" },
  msg: { margin: "8px 0", padding: "10px", borderRadius: "8px", background: "#1f1f1f", maxWidth: "70%" },
  controls: { display: "flex", padding: "10px", background: "#222" },
  input: { flex: 1, marginRight: "8px", padding: "8px" },
  button: { padding: "8px 16px", cursor: "pointer", border: "none", borderRadius: "4px", color: "#fff" },
};

export default ChatPanel;
