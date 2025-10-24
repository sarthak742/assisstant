// frontend/src/services/socketService.js
import { io } from "socket.io-client";

// connect to Flask backend
const socket = io("http://localhost:5000", {
  transports: ["websocket"],
  reconnectionAttempts: 5,
  timeout: 10000
});

// --- event handlers ---
socket.on("connect", () => console.log("[Jarvis] Connected to backend"));
socket.on("disconnect", () => console.log("[Jarvis] Disconnected from backend"));
socket.on("connect_error", (err) => console.error("[Jarvis] Socket error:", err.message));

// --- utility methods ---
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
  socket.on("jarvis_response", (data) => {
    if (callback) callback(data);
  });
}

export default socket;
