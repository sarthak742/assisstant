#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Jarvis AI Realtime Backend Bridge
Connects Electron frontend <-> Python backend modules
via Flask-SocketIO for bidirectional communication.
"""

import os
import json
import logging
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from modules.reasoning_engine import ReasoningEngine
from modules.voice_module import VoiceModule
from modules.memory_manager import MemoryManager
from modules.hybrid_task_manager import HybridTaskManager
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
logging.basicConfig(level=logging.DEBUG)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class SimpleAIChat:
    def generate_response(self, command: str) -> str:
        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": command}]
            )
            response = completion.choices[0].message.content.strip()
            print(f"[OpenAI Response] {response}")
            return response
        except Exception as e:
            print(f"[OpenAI Error] {e}")
            return "Sorry, I couldn't reach OpenAI right now."


# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize SocketIO with CORS support
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize modules in correct order (memory first, then reasoner)
memory = MemoryManager()
voice = VoiceModule()
reasoner = ReasoningEngine(memory)
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
    try:
        user_text = data.get('text', '')
        print(f"[Chat] Received: {user_text}")

        if not user_text.strip():
            emit('jarvis_response', {'reply': 'I did not catch that. Could you say something?', 'type': 'error'})
            return

        # First try ReasoningEngine
        response = reasoner.process(user_text)

        # Then OpenAI fallback if response is empty or generic
        if not response or response.strip() in ["I'm still learning about that.", "", "I don't have an answer for that yet."]:
            try:
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": user_text}]
                )
                response = completion.choices[0].message.content.strip()
                print(f"[OpenAI Response] {response}")
            except Exception as e:
                print(f"[OpenAI Error] {e}")
                response = "Sorry, I couldn't reach OpenAI right now."

        emit('jarvis_response', {'reply': response, 'type': 'text'})
        print(f"[Chat] Response sent: {response}")

    except Exception as e:
        print(f"[Error] handle_user_message: {e}")
        emit('jarvis_response', {'reply': 'Sorry, I encountered an error processing your message.', 'type': 'error'})


@socketio.on('start_voice_recognition')
def handle_start_voice():
    """Start voice recognition"""
    try:
        print("[Voice] Starting voice recognition...")
        result = voice.start_listening()

        if result and result.get('success'):
            emit('jarvis_response', {'reply': 'Listening... Speak now.', 'type': 'system'})
        else:
            emit('jarvis_response', {'reply': 'Voice recognition unavailable.', 'type': 'error'})
    except Exception as e:
        print(f"[Error] handle_start_voice: {e}")
        emit('jarvis_response', {'reply': f'Voice error: {str(e)}', 'type': 'error'})


@socketio.on('stop_voice_recognition')
def handle_stop_voice():
    """Stop voice recognition"""
    try:
        print("[Voice] Stopping voice recognition...")
        result = voice.stop_listening()

        if result and result.get('success') and result.get('text'):
            transcribed = result.get('text')
            print(f"[Voice] Heard: {transcribed}")
            response = reasoner.process(transcribed)
            emit('jarvis_response', {'reply': response, 'type': 'voice', 'transcription': transcribed})
        else:
            emit('jarvis_response', {'reply': 'Voice recognition stopped.', 'type': 'system'})
    except Exception as e:
        print(f"[Error] handle_stop_voice
