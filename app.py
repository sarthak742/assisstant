#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Jarvis AI Realtime Backend Bridge
Connects Electron frontend <-> Python backend modules
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
app.config['SECRET_KEY'] = os.urandom(24)

# Initialize SocketIO with CORS support
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize modules
memory = MemoryManager()
voice = VoiceModule()
reasoner = ReasoningEngine()
task_engine = HybridTaskManager()

print("Jarvis backend starting on port 5000...")

# ============================================
# SOCKET.IO EVENT HANDLERS
# ============================================

@socketio.on('connect')
def on_connect():
    """Handle new client connection"""
    print(f"Client connected: {request.sid}")
    emit('jarvis_response', {
        'text': 'Jarvis backend connected successfully.',
        'type': 'system'
    })

@socketio.on('disconnect')
def on_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {request.sid}")

@socketio.on('user_message')
def handle_user_message(data):
    """
    Handle incoming chat messages from frontend
    
    Expected data format:
    {
        "text": "user message here"
    }
    """
    try:
        user_text = data.get('text', '')
        print(f"[Chat] Received: {user_text}")
        
        if not user_text.strip():
            emit('jarvis_response', {
                'reply': 'I didn\'t catch that. Could you say something?',
                'type': 'error'
            })
            return
        
        # Process with reasoning engine
        response = reasoner.process(user_text)
        
        # Store in memory
        memory.store_interaction(user_text, response)
        
        # Send response back
        emit('jarvis_response', {
            'reply': response,
            'type': 'text',
            'timestamp': memory.get_timestamp()
        })
        
        print(f"[Chat] Response sent: {response}")
        
    except Exception as e:
        print(f"[Error] handle_user_message: {e}")
        emit('jarvis_response', {
            'reply': 'Sorry, I encountered an error processing your message.',
            'type': 'error'
        })

@socketio.on('start_voice_recognition')
def handle_start_voice():
    """
    Start voice recognition
    Frontend calls this when user clicks the
