import React, { useEffect, useState } from "react";
import StatusBar from "./components/StatusBar/StatusBar";
import Sidebar from "./components/Navigation/Sidebar";
import AIOrb from "./components/AIOrb/AIOrb";
import ChatPanel from "./components/ChatPanel";
import { ThemeProvider } from "./contexts/ThemeContext";
import "./App.css";

import {
  sendMessageToJarvis,
  startVoiceRecognition,
  stopVoiceRecognition,
  registerJarvisListener
} from "./services/socketService";

function App() {
  const [connectionStatus, setConnectionStatus] = useState("connecting");
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    registerJarvisListener((data) => {
      console.log("Jarvis:", data.reply);
      setMessages((prev) => [...prev, { sender: "Jarvis", text: data.reply }]);
    });

    setConnectionStatus("connected"); // If socket connects successfully
  }, []);

  // Example UI action trigger
  const handleUserSubmit = (userInput) => {
    sendMessageToJarvis(userInput);
    setMessages((prev) => [...prev, { sender: "You", text: userInput }]);
  };

  return (
    <ThemeProvider>
      <div className="app-container">
        <StatusBar connectionStatus={connectionStatus} />
        <Sidebar />
        <div className="main-content">
          <AIOrb />
          <ChatPanel messages={messages} onSubmit={handleUserSubmit} />
        </div>
      </div>
    </ThemeProvider>
  );
}

export default App;
