#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Jarvis AI Realtime Backend Bridge
Connects Electron frontend <--> Python backend modules
via Flask-SocketIO for bidirectional communication.
"""

import os
import json
from flask import Flask, request
from flask_socketio import SocketIO, emit
from modules.reasoning_engine import ReasoningEngine
from modules.voice_module import VoiceModule
from modules.memory_manager import MemoryManager
from modules.hybrid_task_manager import HybridTaskManager

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'change_this_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Load core systems
memory = MemoryManager()
voice = VoiceModule()
reasoner = ReasoningEngine(memory_manager=memory)
task_engine = HybridTaskManager(memory_manager=memory, voice_module=voice)

# ---------------- SOCKET EVENTS ----------------
@socketio.on('connect')
def on_connect():
    print("[Socket] Electron frontend connected.")
    emit('status', {'state': 'connected', 'message': 'Jarvis backend online.'})

@socketio.on('disconnect')
def on_disconnect():
    print("[Socket] Electron frontend disconnected.")

@socketio.on('user_message')
def handle_user_message(msg):
    """Receive text/voice command from frontend."""
    print(f"[User] {msg}")
    memory.store_interaction("user", msg)

    # Reasoning + response
    try:
        response = reasoner.process(msg)
        voice.speak(response)
        memory.store_interaction("jarvis", response)
        emit('jarvis_response', {'text': response})
    except Exception as e:
        emit('jarvis_response', {'text': f"Error: {e}"})

@socketio.on('execute_task')
def handle_task_request(data):
    """Execute structured command forwarded from ReasoningEngine."""
    result = task_engine.execute_from_reasoning(data)
    emit('task_update', {'result': result})

@socketio.on('get_memory')
def send_memory_snapshot(_):
    """Send a memory snapshot to frontend dashboard."""
    emit('memory_snapshot', {
        'context': memory.context,
        'recent': memory.get_recent_interactions(5)
    })

# ---------------- REST FALLBACK API ----------------
@app.route('/api/ping')
def ping():
    return {'status': 'ok', 'message': 'Flask backend running'}

if __name__ == "__main__":
    port = 5000
    print(f"Jarvis backend starting on port {port}...")
    socketio.run(app, host='127.0.0.1', port=port)
