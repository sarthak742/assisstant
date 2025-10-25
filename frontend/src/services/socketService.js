// frontend/src/services/socketService.js
import { io } from "socket.io-client";

// Connect to Flask SocketIO backend
const socket = io("http://localhost:5000", {
  transports: ["websocket"], // ensures upgrade to websocket if possible
  reconnectionAttempts: 10,
  timeout: 15000,
});

// --- Window/global event bridge for status bar integration ---
socket.on("connect", () => {
  console.log("[Jarvis] Connected to backend");
  window.dispatchEvent(new CustomEvent("jarvis-connected"));
});
socket.on("disconnect", () => {
  console.log("[Jarvis] Disconnected from backend");
  window.dispatchEvent(new CustomEvent("jarvis-disconnected"));
});
socket.on("connect_error", (err) => {
  console.error("[Jarvis] Socket error:", err.message);
  window.dispatchEvent(new CustomEvent("jarvis-disconnected"));
});

// --- Core socket user message/voice functions ---
export function sendMessageToJarvis(userText) {
  if (userText && userText.trim() !== "") {
    socket.emit("user_message", { text: userText });
  }
}

export function startVoiceRecognition() {
  socket.emit("start_voice_recognition");
}

export function stopVoiceRecognition() {
  socket.emit("stop_voice_recognition");
}

export function registerJarvisListener(callback) {
  // This ensures only one listener attaches
  socket.off("jarvis_response"); // remove old, if any
  socket.on("jarvis_response", (data) => {
    if (callback) callback(data);
  });
}

// (Optional) Add event for backend task updates
export function registerTaskUpdateListener(callback) {
  socket.off("task_update");
  socket.on("task_update", (data) => {
    if (callback) callback(data);
  });
}

// Expose raw socket for advanced or debug needs
export default socket;
