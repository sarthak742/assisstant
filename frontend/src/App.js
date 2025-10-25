import React, { useEffect, useState, useCallback } from "react";
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

  // --- Socket Connection & Event Handling ---
  useEffect(() => {
    const handleOnline = () => setConnectionStatus("connected");
    const handleOffline = () => setConnectionStatus("disconnected");

    window.addEventListener("jarvis-connected", handleOnline);
    window.addEventListener("jarvis-disconnected", handleOffline);

    // Handle Jarvis responses
    const unregister = registerJarvisListener((data) => {
      const jarvisReply = data.reply || data.text;
      console.log("Jarvis:", jarvisReply);

      setMessages((prev) => [
        ...prev,
        { sender: "Jarvis", text: jarvisReply },
      ]);
    });

    // Cleanup listeners
    return () => {
      window.removeEventListener("jarvis-connected", handleOnline);
      window.removeEventListener("jarvis-disconnected", handleOffline);
      if (unregister) unregister();
    };
  }, []);

  // --- Handle User Messages ---
  const handleUserSubmit = useCallback((userInput) => {
    const trimmed = userInput?.trim();
    if (!trimmed) return;

    setMessages((prev) => [
      ...prev,
      { sender: "You", text: trimmed },
    ]);

    sendMessageToJarvis(trimmed);
  }, []);

  // --- Dynamic Status Text ---
  const connectionLabel =
    connectionStatus === "connecting"
      ? "Connecting to Jarvis..."
      : connectionStatus === "connected"
      ? "Connected"
      : "Disconnected";

  return (
    <ThemeProvider>
      <div className="app-container">
        <StatusBar connectionStatus={connectionLabel} />
        <Sidebar />
        <main className="main-content">
          <AIOrb status={connectionStatus} />
          <ChatPanel
            messages={messages}
            onSubmit={handleUserSubmit}
            startVoiceRecognition={startVoiceRecognition}
            stopVoiceRecognition={stopVoiceRecognition}
          />
        </main>
      </div>
    </ThemeProvider>
  );
}

export default App;
