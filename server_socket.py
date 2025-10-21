#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Jarvis Backend Socket.IO Server
Listens on ws://localhost:8765 for Socket.IO connections and emits events expected by frontend.
"""

import logging
from datetime import datetime

import socketio
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from modules.memory_manager import MemoryManager
from modules.ai_chat_module import AIChatModule

logger = logging.getLogger("Jarvis.Socket")
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# Core modules
memory = MemoryManager()
ai_chat = AIChatModule(memory)

# Socket.IO setup (ASGI)
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = socketio.ASGIApp(sio)

# Optional: mount CORS via FastAPI wrapper if needed
# Not strictly necessary for pure Socket.IO, but helpful if we add health route
fastapi_app = FastAPI()
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@fastapi_app.get("/health")
def health():
    return {"status": "ok"}

# Compose ASGI app that serves Socket.IO at root and a /health route
# Note: uvicorn can serve socketio.ASGIApp directly. If we need both, we can use routing.
# For simplicity, we expose only Socket.IO here.

@sio.event
async def connect(sid, environ):
    logger.info(f"Client connected: {sid}")
    # Send initial status update
    await sio.emit('status_update', { 'connected': True, 'socketId': sid })

@sio.event
async def disconnect(sid):
    logger.info(f"Client disconnected: {sid}")

@sio.event
async def chat_message(sid, data):
    try:
        message = (data or {}).get('message', '')
        timestamp = datetime.utcnow().isoformat()
        memory.store_interaction('user', message)
        response = ai_chat.generate_response(message)
        memory.store_interaction('jarvis', response)
        # Emit chat response
        await sio.emit('chat_response', { 'message': response, 'timestamp': timestamp })
        # Also emit memory update event
        await sio.emit('memory_update', { 'action': 'append', 'entry': {
            'speaker': 'jarvis', 'message': response, 'timestamp': timestamp
        }})
    except Exception as e:
        logger.exception('chat_message handler failed')
        await sio.emit('error', { 'message': str(e) })

# Alias for generic 'message' event
@sio.event
async def message(sid, data):
    # Simply forward to clients for demo
    await sio.emit('message', data)

if __name__ == "__main__":
    import uvicorn
    # Serve the Socket.IO ASGI app directly on port 8765
    uvicorn.run(app, host="0.0.0.0", port=8765, reload=False)