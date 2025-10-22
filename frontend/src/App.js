import React, { useEffect, useState } from "react";
import StatusBar from "./components/StatusBar/StatusBar";
import Sidebar from "./components/Navigation/Sidebar";
import AIOrb from "./components/AIOrb/AIOrb";
import ChatPanel from "./components/ChatPanel";
import ApiService from "./services/api";
import { ThemeProvider } from "./contexts/ThemeContext";

function App() {
  const [connectionStatus, setConnectionStatus] = useState("connecting");

  useEffect(() => {
    let isMounted = true;

    const init = async () => {
      const result = await ApiService.initializeSocket();
      if (!isMounted) return;

      if (result.success) {
        setConnectionStatus("connected");
      } else {
        setConnectionStatus("disconnected");
      }
    };

    init();

    const onConnect = () => {
      if (!isMounted) return;
      setConnectionStatus("connected");
    };

    const onDisconnect = (info) => {
      if (!isMounted) return;
      const { reason } = info || {};
      setConnectionStatus(reason === "io client disconnect" ? "disconnected" : "reconnecting");
    };

    const onConnectError = () => {
      if (!isMounted) return;
      setConnectionStatus("disconnected");
    };

    const onReconnectAttempt = () => {
      if (!isMounted) return;
      setConnectionStatus("reconnecting");
    };

    const onReconnect = () => {
      if (!isMounted) return;
      setConnectionStatus("connected");
    };

    ApiService.addEventListener("connect", onConnect);
    ApiService.addEventListener("disconnect", onDisconnect);
    ApiService.addEventListener("connect_error", onConnectError);
    ApiService.addEventListener("reconnect_attempt", onReconnectAttempt);
    ApiService.addEventListener("reconnect", onReconnect);

    return () => {
      isMounted = false;
      ApiService.removeEventListener("connect", onConnect);
      ApiService.removeEventListener("disconnect", onDisconnect);
      ApiService.removeEventListener("connect_error", onConnectError);
      ApiService.removeEventListener("reconnect_attempt", onReconnectAttempt);
      ApiService.removeEventListener("reconnect", onReconnect);
      ApiService.disconnectSocket();
    };
  }, []);

  return (
    <ThemeProvider>
      <div className="app-container">
        <StatusBar connectionStatus={connectionStatus} />
        <Sidebar />
        <div style={{ display: "flex", flexDirection: "column", flex: 1 }}>
          <AIOrb />
          {/* Hybrid chat + voice interaction panel */}
          <ChatPanel />
        </div>
      </div>
    </ThemeProvider>
  );
}

export default App;
