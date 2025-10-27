#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Jarvis AI Realtime Backend Bridge (v2.2 - Context Aware)
--------------------------------------------------------
Adds context tracking to avoid repeating identical results
(e.g., jokes, facts, suggestions). Works globally in app.py.
"""

import os
import json
import random
import logging
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

# ============================================================
# Core Jarvis Modules
# ============================================================
from modules.memory_manager import MemoryManager
from modules.reasoning_engine import ReasoningEngine

# ============================================================
# Initialization & Logging
# ============================================================
load_dotenv()
logging.basicConfig(level=logging.INFO)
logging.getLogger("werkzeug").setLevel(logging.WARNING)

if not os.getenv("OPENAI_API_KEY"):
    print("[WARNING] No OpenAI API key found. Please configure your .env file.")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ============================================================
# Global Context Memory for Outputs
# ============================================================
last_results = {}  # {(category, user_id): last_value}

def get_non_repeating_response(category, responses, user_id='default'):
    """
    Return a non-repeating response for the given category.
    """
    key = (category, user_id)
    previous = last_results.get(key)
    pool = [r for r in responses if r != previous]
    if not pool:
        pool = responses
    new_choice = random.choice(pool)
    last_results[key] = new_choice
    return new_choice


# ============================================================
# Simple OpenAI Fallback for General Chat
# ============================================================
class SimpleAIChat:
    """Fallback model when a local reasoning module has no response."""

    def generate_response(self, text: str) -> str:
        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": text}]
            )
            reply = completion.choices[0].message.content.strip()
            print(f"[OpenAI Response] {reply}")
            return reply
        except Exception as e:
            print(f"[OpenAI Error] {e}")
            return "Sorry, I couldn't reach OpenAI right now."


# ============================================================
# Flask + SocketIO Setup
# ============================================================
app = Flask(__name__)
app.config["SECRET_KEY"] = os.urandom(24)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# ============================================================
# Initialize Core Systems
# ============================================================
memory = MemoryManager()
reasoner = ReasoningEngine(memory)
voice = reasoner.voice
task_engine = reasoner.task_manager
ai_fallback = SimpleAIChat()

print("[Jarvis] Backend starting on http://localhost:5000 🚀")
voice.speak("Jarvis backend online and ready for automation.")


# ============================================================
# Routes
# ============================================================
@app.route("/")
def home():
    return "Jarvis Flask backend is running successfully!", 200


# ============================================================
# SocketIO Handlers
# ============================================================
@socketio.on("connect")
def on_connect():
    print(f"[SocketIO] Client connected: {request.sid}")
    emit("jarvis_response", {"text": "Jarvis backend connected successfully.", "type": "system"})


@socketio.on("disconnect")
def on_disconnect():
    print(f"[SocketIO] Client disconnected: {request.sid}")


@socketio.on("user_message")
def on_user_message(data):
    """Handle main chat and automation commands with context awareness."""
    try:
        user_text = data.get("text", "").strip()
        print(f"[Frontend] Message received: {user_text}")

        if not user_text:
            emit("jarvis_response", {"reply": "I didn’t catch that. Could you repeat?", "type": "error"})
            return

        # Process through reasoning engine
        response = reasoner.process(user_text)

        # Apply no-repeat logic for simple content categories
        response_category = None
        simple_categories = {
            "joke": ["Why did the scarecrow win an award? Because he was outstanding in his field!",
                     "Why don’t scientists trust atoms? Because they make up everything!",
                     "Why did the math book look sad? Because it had too many problems!"],
            "fact": ["The Eiffel Tower can grow over 6 inches during summer.",
                     "Bananas are berries, but strawberries are not.",
                     "Honey never spoils — archaeologists have found edible honey in ancient tombs."]
        }

        # Auto-detect category keywords
        for cat in simple_categories.keys():
            if cat in user_text.lower():
                response_category = cat
                response = get_non_repeating_response(cat, simple_categories[cat])
                break

        # Fallback to OpenAI if no local logic yields a result
        if not response or response.strip() in [
            "", "Unknown or unsupported task type.", "I’m sorry, I don’t understand that yet."
        ]:
            response = ai_fallback.generate_response(user_text)

        emit("jarvis_response", {"reply": response, "type": "text"})
        print(f"[Jarvis Reply] {response}")

    except Exception as e:
        print(f"[Error] on_user_message: {e}")
        emit("jarvis_response", {"reply": f"Error processing message: {e}", "type": "error"})


# ============================================================
# Voice Control Events
# ============================================================
@socketio.on("start_voice_recognition")
def start_voice():
    try:
        print("[Voice] Activating recognition mode…")
        success = voice.start_listening()
        if success:
            emit("jarvis_response", {"reply": "Listening… Speak now.", "type": "system"})
        else:
            emit("jarvis_response", {"reply": "Voice engine unavailable.", "type": "error"})
    except Exception as e:
        print(f"[Error] start_voice_recognition: {e}")
        emit("jarvis_response", {"reply": f"Voice error: {e}", "type": "error"})


@socketio.on("stop_voice_recognition")
def stop_voice():
    try:
        print("[Voice] Stopping recognition loop…")
        voice.stop_listening()
        emit("jarvis_response", {"reply": "Voice recognition stopped.", "type": "system"})
    except Exception as e:
        print(f"[Error] stop_voice_recognition: {e}")
        emit("jarvis_response", {"reply": f"Stop voice error: {e}", "type": "error"})


# ============================================================
# Task Request Handler
# ============================================================
@socketio.on("task_request")
def on_task_request(data):
    try:
        task_type = data.get("task_type")
        task_data = data.get("data", {})
        print(f"[Automation] Running task: {task_type}")
        result = task_engine.execute_system_command(task_type)
        emit("task_update", {"task_type": task_type, "result": result})
    except Exception as e:
        print(f"[Error] on_task_request: {e}")
        emit("task_update", {"task_type": task_type, "error": str(e)})


# ============================================================
# REST Chat Endpoint (w/ context awareness)
# ============================================================
@app.route("/ai/chat", methods=["POST"])
def ai_chat():
    try:
        data = request.get_json()
        message = data.get("message", "").strip()
        if not message:
            return jsonify({"error": "No message provided."}), 400
        reply = ai_fallback.generate_response(message)
        print(f"[REST Response] {reply}")
        return jsonify({"reply": reply}), 200
    except Exception as e:
        print(f"[Error] /ai/chat: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================
# Launch Server
# ============================================================
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=False, allow_unsafe_werkzeug=True)
