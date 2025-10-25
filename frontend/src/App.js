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
  registerJarvisListener,
} from "./services/socketService";

function App() {
  const [connectionStatus, setConnectionStatus] = useState("connecting");
  const [messages, setMessages] = useState([]);

  // Listen for socket connection/disconnection events
  useEffect(() => {
    // Status via global events
    const setOnline = () => setConnectionStatus("connected");
    const setOffline = () => setConnectionStatus("disconnected");
    window.addEventListener("jarvis-connected", setOnline);
    window.addEventListener("jarvis-disconnected", setOffline);

    // Listen for Jarvis responses
    registerJarvisListener((data) => {
      console.log("Jarvis:", data.reply || data.text);
      setMessages((prev) => [
        ...prev,
        { sender: "Jarvis", text: data.reply || data.text },
      ]);
    });

    // Cleanup listeners on unmount
    return () => {
      window.removeEventListener("jarvis-connected", setOnline);
      window.removeEventListener("jarvis-disconnected", setOffline);
    };
  }, []);

  const handleUserSubmit = (userInput) => {
    if (userInput && userInput.trim() !== "") {
      setMessages((prev) => [
        ...prev,
        { sender: "You", text: userInput },
      ]);
      sendMessageToJarvis(userInput);
    }
  };

  return (
    <ThemeProvider>
      <div className="app-container">
        <StatusBar connectionStatus={connectionStatus} />
        <Sidebar />
        <div className="main-content">
          <AIOrb />
          {/* Pass messages & handler to ChatPanel */}
          <ChatPanel
            messages={messages}
            onSubmit={handleUserSubmit}
            startVoiceRecognition={startVoiceRecognition}
            stopVoiceRecognition={stopVoiceRecognition}
          />
        </div>
      </div>
    </ThemeProvider>
  );
}

export default App;

