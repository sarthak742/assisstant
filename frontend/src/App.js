import React, { useEffect, useState } from "react";
import StatusBar from "./components/StatusBar/StatusBar";
import Sidebar from "./components/Navigation/Sidebar";
import AIOrb from "./components/AIOrb/AIOrb";
import ChatPanel from "./components/ChatPanel";
import ApiService from "./services/api";
import { ThemeProvider } from "./contexts/ThemeContext";
import "./App.css";
import { io } from "socket.io-client";

// --------------------------------------------------
// SOCKET CONNECTION SETUP (Jarvis Flask backend)
// --------------------------------------------------
const socket = io("http://localhost:5000");

// Send user message to backend
export function sendMessageToJarvis(userText) {
  if (userText && userText.trim() !== "") {
    socket.emit("user_message", { text: userText });
  }
}

// Listen for backend responses
socket.on("jarvis_response", (data) => {
  console.log("Jarvis:", data.reply || data.text);

  // Optional: link this to your chat UI
  if (window.addMessageToChat)
    window.addMessageToChat("Jarvis", data.reply || data.text);
});

// Handle connection errors gracefully
socket.on("connect_error", (err) => {
  console.error("Connection error:", err.message);
});

// --------------------------------------------------
// MAIN APP COMPONENT
// --------------------------------------------------
function App() {
  const [connectionStatus, setConnectionStatus] = useState("connecting");

  useEffect(() => {
    let isMounted = true;

    const init = async () => {
      try {
        const result = await ApiService.initializeSocket();
        if (!isMounted) return;
        if (result.success) setConnectionStatus("connected");
        else setConnectionStatus("disconnected");
      } catch {
        setConnectionStatus("disconnected");
      }
    };

    init();

    // SocketIO event listeners
    const onConnect = () => isMounted && setConnectionStatus("connected");
    const onDisconnect = (info) => {
      if (!isMounted) return;
      const { reason } = info || {};
      setConnectionStatus(reason === "io client disconnect" ? "disconnected" : "reconnecting");
    };
    const onConnectError = () => isMounted && setConnectionStatus("disconnected");
    const onReconnectAttempt = () => isMounted && setConnectionStatus("reconnecting");
    const onReconnect = () => isMounted && setConnectionStatus("connected");

    ApiService.addEventListener("connect", onConnect);
    ApiService.addEventListener("disconnect", onDisconnect);
    ApiService.addEventListener("connect_error", onConnectError);
    ApiService.addEventListener("reconnect_attempt", onReconnectAttempt);
    ApiService.addEventListener("reconnect", onReconnect);

    // Cleanup when unmounting
    return () => {
      isMounted = false;
      ApiService.removeEventListener("connect", onConnect);
      ApiService.removeEventListener("disconnect", onDisconnect);
      ApiService.removeEventListener("connect_error", onConnectError);
      ApiService.removeEventListener("reconnect_attempt", onReconnectAttempt);
      ApiService.removeEventListener("reconnect", onReconnect);
      ApiService.disconnectSocket();
      socket.disconnect();
      console.log("Jarvis frontend socket disconnected.");
    };
  }, []);

  return (
    <ThemeProvider>
      <div className="app-container">
        <StatusBar connectionStatus={connectionStatus} />
        <Sidebar />
        <div className="main-content">
          <AIOrb />
          <ChatPanel />
        </div>
      </div>
    </ThemeProvider>
  );
}

export default App;

