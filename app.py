#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Jarvis AI Realtime Backend Bridge (Jarvis 2.0)
----------------------------------------------
Connects Electron / React frontend ↔ Python automation backend
via Flask-SocketIO for bidirectional real-time execution.
"""

import os
import json
import logging
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI

# Core Jarvis modules
from modules.reasoning_engine import ReasoningEngine
from modules.voice_module import VoiceModule
from modules.memory_manager import MemoryManager
from modules.hybrid_task_manager import HybridTaskManager

# ============================================
# INIT ENVIRONMENT AND LOGGING
# ============================================
load_dotenv()
logging.basicConfig(level=logging.INFO)
logging.getLogger('werkzeug').setLevel(logging.WARNING)

if not os.getenv("OPENAI_API_KEY"):
    print("[WARNING] No OpenAI API key found. Please set it in your .env file.")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ============================================
# SIMPLE OPENAI CHAT FALLBACK
# ============================================
class SimpleAIChat:
    def generate_response(self, command: str) -> str:
        try:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": command}]
            )
            reply = completion.choices[0].message.content.strip()
            print(f"[OpenAI Response] {reply}")
            return reply
        except Exception as e:
            print(f"[OpenAI Error] {e}")
            return "Sorry, I couldn't reach OpenAI right now."


# ============================================
# APP INITIALIZATION
# ============================================
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# ============================================
# INITIALIZE CORE MODULES
# ============================================
memory = MemoryManager()
voice = VoiceModule()
reasoner = ReasoningEngine(memory)
task_manager = HybridTaskManager(memory_manager=memory, voice_module=voice)
ai_fallback = SimpleAIChat()

print("[Jarvis] Backend starting on http://localhost:5000 🚀")
voice.speak("Jarvis backend online and ready for automation.")

# ============================================
# HEALTHCHECK
# ============================================
@app.route('/')
def home():
    return "Jarvis Flask backend is running successfully!", 200

# ============================================
# SOCKET.IO HANDLERS
# ============================================

@socketio.on('connect')
def handle_connect():
    print(f"[SocketIO] Client connected: {request.sid}")
    emit('jarvis_response', {
        'text': 'Jarvis backend connected successfully.',
        'type': 'system'
    })


@socketio.on('disconnect')
def handle_disconnect():
    print(f"[SocketIO] Client disconnected: {request.sid}")


@socketio.on('user_message')
def handle_user_message(data):
    """
    Central handler for chat and automation commands.
    """
    try:
        user_text = data.get('text', '').strip()
        print(f"[Frontend] Received: {user_text}")

        if not user_text:
            emit('jarvis_response', {'reply': "I didn't catch that, please repeat.", 'type': 'error'})
            return

        # Process through Reasoning Engine
        response = reasoner.process(user_text)

        # Fallback to OpenAI if nothing custom handled
        if not response or response.strip() in ["", "Unknown or unsupported task type.", "I'm sorry, I don't understand that command."]:
            response = ai_fallback.generate_response(user_text)

        emit('jarvis_response', {'reply': response, 'type': 'text'})
        print(f"[Jarvis Response] {response}")

    except Exception as e:
        print(f"[Error] handle_user_message: {str(e)}")
        emit('jarvis_response', {
            'reply': f"Error processing message: {str(e)}",
            'type': 'error'
        })


# ============================================
# VOICE HANDLERS
# ============================================

@socketio.on('start_voice_recognition')
def handle_voice_start():
    try:
        print("[Voice] Starting recognition...")
        result = voice.start_listening()

        if result and result.get('success'):
            emit('jarvis_response', {
                'reply': 'Listening... Speak now.',
                'type': 'system'
            })
        else:
            emit('jarvis_response', {
                'reply': 'Voice recognition unavailable.',
                'type': 'error'
            })
    except Exception as e:
        print(f"[Error] handle_voice_start: {e}")
        emit('jarvis_response', {
            'reply': f"Voice start error: {str(e)}",
            'type': 'error'
        })


@socketio.on('stop_voice_recognition')
def handle_voice_stop():
    try:
        print("[Voice] Stopping recognition...")
        result = voice.stop_listening()

        if result and result.get('success') and result.get('text'):
            transcribed = result['text']
            print(f"[Voice Heard] {transcribed}")
            reply = reasoner.process(transcribed)
            emit('jarvis_response', {
                'reply': reply,
                'type': 'voice',
                'transcription': transcribed
            })
        else:
            emit('jarvis_response', {'reply': 'Voice recognition stopped.', 'type': 'system'})
    except Exception as e:
        print(f"[Error] handle_voice_stop: {e}")
        emit('jarvis_response', {'reply': str(e), 'type': 'error'})


# ============================================
# TASK / AUTOMATION API
# ============================================

@socketio.on('task_request')
def handle_task_request(data):
    try:
        task_type = data.get('task_type')
        task_data = data.get('data', {})
        print(f"[Task] Requested: {task_type}")
        result = task_manager.execute_system_command(task_type)
        emit('task_update', {'task_type': task_type, 'result': result})
    except Exception as e:
        print(f"[Error] handle_task_request: {e}")
        emit('task_update', {'task_type': task_type, 'error': str(e)})


# ============================================
# REST ENDPOINT FOR CHAT
# ============================================

@app.route('/ai/chat', methods=['POST'])
def ai_chat():
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        if not message:
            return jsonify({'error': 'No message given.'}), 400

        reply = ai_fallback.generate_response(message)
        print(f"[REST Chat] {reply}")
        return jsonify({'reply': reply}), 200
    except Exception as e:
        print(f"[Error /ai/chat] {e}")
        return jsonify({'error': str(e)}), 500

# ============================================
# RUN FLASK-SOCKETIO SERVER
# ============================================

if __name__ == '__main__':
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=False,
        allow_unsafe_werkzeug=True
    )
