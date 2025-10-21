#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Jarvis Backend HTTP Server (FastAPI)
Exposes REST endpoints expected by the frontend ApiService at http://localhost:8000
"""

import logging
from typing import List, Dict, Any

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from modules.memory_manager import MemoryManager
from modules.ai_chat_module import AIChatModule

logger = logging.getLogger("Jarvis.HTTP")
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

app = FastAPI(title="Jarvis Backend", version="1.0.0")

# CORS for local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modules
memory = MemoryManager()
ai_chat = AIChatModule(memory)

# Helpers to transform memory entries to UI-friendly shape

def transform_interaction(entry: Dict[str, Any], idx: int) -> Dict[str, Any]:
    return {
        "id": f"{idx}-{entry.get('timestamp','')}",
        "content": entry.get("message", ""),
        "timestamp": entry.get("timestamp", ""),
        "type": "user" if entry.get("speaker") == "user" else "assistant",
    }

class ChatRequest(BaseModel):
    message: str

class UpdateMemoryPayload(BaseModel):
    content: str

class AuthPayload(BaseModel):
    username: str | None = None
    password: str | None = None

class VerifyPinPayload(BaseModel):
    pin: str

class ExecuteCommandPayload(BaseModel):
    command: str

class TextToSpeechPayload(BaseModel):
    text: str

# Routes
@app.get("/memory/interactions")
def get_recent_interactions(count: int = Query(10, ge=1, le=100)):
    try:
        interactions = memory.get_recent_interactions(count)
        transformed = [transform_interaction(entry, i) for i, entry in enumerate(interactions)]
        return {"interactions": transformed}
    except Exception as e:
        logger.exception("get_recent_interactions failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/memory/log")
def log_interaction(payload: Dict[str, Any]):
    try:
        speaker = payload.get("speaker", "user")
        message = payload.get("message", "")
        ok = memory.store_interaction(speaker, message)
        return {"success": bool(ok)}
    except Exception as e:
        logger.exception("log_interaction failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory/context")
def get_context():
    try:
        # Return the raw context dict stored by MemoryManager
        return memory.context
    except Exception as e:
        logger.exception("get_context failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/memory/list")
def list_memories():
    try:
        interactions = memory.get_recent_interactions(100)
        transformed = [transform_interaction(entry, i) for i, entry in enumerate(interactions)]
        return {"memories": transformed}
    except Exception as e:
        logger.exception("list_memories failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/memory/{memory_id}")
def delete_memory(memory_id: str):
    try:
        # Parse index from our id format "{idx}-{timestamp}"
        idx_part = str(memory_id).split("-")[0]
        idx = int(idx_part)
        interactions = memory.get_recent_interactions(100)
        if idx < 0 or idx >= len(interactions):
            raise HTTPException(status_code=404, detail="Memory not found")
        # Remove from in-memory list and persist
        interactions.pop(idx)
        memory.interactions = interactions
        ok = memory._save_data(memory.interactions_file, interactions)
        return {"success": bool(ok)}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("delete_memory failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/memory/{memory_id}")
def update_memory(memory_id: str, payload: UpdateMemoryPayload):
    try:
        idx_part = str(memory_id).split("-")[0]
        idx = int(idx_part)
        interactions = memory.get_recent_interactions(100)
        if idx < 0 or idx >= len(interactions):
            raise HTTPException(status_code=404, detail="Memory not found")
        interactions[idx]["message"] = payload.content
        memory.interactions = interactions
        ok = memory._save_data(memory.interactions_file, interactions)
        return {"success": bool(ok)}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("update_memory failed")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ai/chat")
async def ai_chat_endpoint(req: ChatRequest):
    try:
        # Store user message
        memory.store_interaction("user", req.message)
        # Generate response
        response = ai_chat.generate_response(req.message)
        # Store assistant response
        memory.store_interaction("jarvis", response)
        return {"response": response, "success": True}
    except Exception as e:
        logger.exception("ai_chat failed")
        raise HTTPException(status_code=500, detail=str(e))

# Voice endpoints (stubs)
@app.post("/voice/start")
def voice_start():
    return {"success": True}

@app.post("/voice/stop")
def voice_stop():
    return {"success": True}

@app.post("/voice/speak")
def voice_speak(payload: TextToSpeechPayload):
    # Stub: in real impl, call TTS engine
    return {"success": True}

# Updates endpoints (stubs)
@app.get("/api/updates/check")
def updates_check():
    return {"current": "1.0.0", "latest": "1.0.0", "available": False}

@app.get("/api/updates/version")
def updates_version():
    return {"current": "1.0.0", "latest": "1.0.0"}

# Security endpoints (stubs)
@app.post("/api/security/auth")
def security_auth(payload: AuthPayload):
    return {"success": True}

@app.get("/api/security/settings")
def security_settings():
    return {"voice_authentication": False, "pin_required": False, "location_tracking": False}

@app.patch("/api/security/settings")
def update_security_settings(payload: Dict[str, Any]):
    # Accept updates into context for demo purposes
    memory.store_context("security_settings", payload)
    return {"success": True}

@app.post("/api/security/verify-pin")
def verify_pin(payload: VerifyPinPayload):
    # Demo: accept any 4+ digit PIN
    valid = payload.pin and payload.pin.isdigit() and len(payload.pin) >= 4
    return {"success": bool(valid)}

# System endpoints (stubs)
@app.get("/api/system/logs")
def system_logs(count: int = Query(50, ge=1, le=200)):
    # Convert recent interactions into simple log entries
    interactions = memory.get_recent_interactions(count)
    logs = [
        {"level": "info", "message": f"{e.get('speaker')}: {e.get('message')}", "timestamp": e.get('timestamp')}
        for e in interactions
    ]
    return {"logs": logs}

@app.post("/api/system/execute")
def system_execute(payload: ExecuteCommandPayload):
    # For safety, do not actually execute system commands in this demo
    return {"success": True, "output": f"Executed (mock): {payload.command}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server_http:app", host="0.0.0.0", port=8000, reload=False)