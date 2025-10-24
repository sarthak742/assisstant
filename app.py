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
import logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# Initialize SocketIO with CORS support
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize modules in correct order (memory first, then reasoner)
memory = MemoryManager()
voice = VoiceModule()
reasoner = ReasoningEngine(memory)  # ✅ FIXED: Pass memory_manager
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
    """Handle incoming chat messages from frontend"""
    try:
        user_text = data.get('text', '')
        print(f"[Chat] Received: {user_text}")
        
        if not user_text.strip():
            emit('jarvis_response', {
                'reply': 'I did not catch that. Could you say something?',
                'type': 'error'
            })
            return
        
        # Process with reasoning engine
        # Process with reasoning engine
response = reasoner.process(user_text)

# If reasoning engine doesn't produce a valid response, use OpenAI
if not response or response.strip() in ["I'm still learning about that.", ""]:
    import openai
    import os
    from dotenv import load_dotenv
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_text}]
        )
        response = completion["choices"][0]["message"]["content"].strip()
        print(f"[OpenAI Response] {response}")
    except Exception as e:
        print(f"[OpenAI Error] {e}")
        response = "Sorry, I couldn't reach OpenAI right now."

        
        # Send response back
        emit('jarvis_response', {
            'reply': response,
            'type': 'text'
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
    """Start voice recognition"""
    try:
        print("[Voice] Starting voice recognition...")
        
        # Start listening
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
        print(f"[Error] handle_start_voice: {e}")
        emit('jarvis_response', {
            'reply': f'Voice error: {str(e)}',
            'type': 'error'
        })

@socketio.on('stop_voice_recognition')
def handle_stop_voice():
    """Stop voice recognition"""
    try:
        print("[Voice] Stopping voice recognition...")
        
        # Stop listening and get transcription
        result = voice.stop_listening()
        
        if result and result.get('success') and result.get('text'):
            transcribed_text = result.get('text')
            print(f"[Voice] Heard: {transcribed_text}")
            
            # Process the transcribed text
            response = reasoner.process(transcribed_text)
            
            # Send back the transcription and response
            emit('jarvis_response', {
                'reply': response,
                'type': 'voice',
                'transcription': transcribed_text
            })
        else:
            emit('jarvis_response', {
                'reply': 'Voice recognition stopped.',
                'type': 'system'
            })
            
    except Exception as e:
        print(f"[Error] handle_stop_voice: {e}")
        emit('jarvis_response', {
            'reply': f'Voice stop error: {str(e)}',
            'type': 'error'
        })

@socketio.on('task_request')
def handle_task_request(data):
    """Handle task execution requests"""
    try:
        task_type = data.get('task_type')
        task_data = data.get('data', {})
        
        print(f"[Task] Executing: {task_type}")
        
        result = task_engine.execute_task(task_type, task_data)
        
        emit('task_update', {
            'task_type': task_type,
            'result': result,
            'status': 'completed'
        })
        
    except Exception as e:
        print(f"[Error] handle_task_request: {e}")
        emit('task_update', {
            'task_type': task_type,
            'error': str(e),
            'status': 'failed'
        })

# ============================================
# RUN SERVER
# ============================================

if __name__ == '__main__':
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=False,
        allow_unsafe_werkzeug=True
    )
