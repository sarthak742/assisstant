#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Jarvis AI — Memory Manager (Stable Hybrid Build 2.1)
----------------------------------------------------
Features:
- Semantic embeddings for recall via SentenceTransformer
- Encrypted local storage with Fernet (fallback-safe)
- Auto context injection for ReasoningEngine
- LLM summarization for long-term contextual learning
"""

import os
import json
import logging
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger("Jarvis.MemoryManager")

# -------------------------------------------------
# Dependency Setup
# -------------------------------------------------
try:
    from cryptography.fernet import Fernet
    from sentence_transformers import SentenceTransformer, util
    import openai
    ENHANCED_MEMORY_READY = True
except ImportError:
    ENHANCED_MEMORY_READY = False
    logger.warning("Missing ML/encryption libs. Run: pip install cryptography sentence-transformers openai")

# -------------------------------------------------
# Core Memory Manager
# -------------------------------------------------
class MemoryManager:
    """Advanced hybrid memory system with robust fallback and safe initialization."""

    def __init__(self, data_dir: Optional[str] = None):
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = data_dir or os.path.join(base, "data")
        os.makedirs(self.data_dir, exist_ok=True)

        # File paths
        self.files = {
            "interactions": os.path.join(self.data_dir, "interactions.json"),
            "preferences": os.path.join(self.data_dir, "preferences.json"),
            "context": os.path.join(self.data_dir, "context.json"),
            "embeddings": os.path.join(self.data_dir, "embeddings.npy"),
            "key": os.path.join(self.data_dir, "secret.key"),
        }

        # Initialize encryption
        self.cipher = self._init_cipher()

        # Load memory sets
        self.interactions = self._load_json("interactions", [])
        self.preferences = self._load_json("preferences", {})
        self.context = self._load_json("context", {})
        self.embeddings = self._load_embeddings()

        # Setup semantic model
        if ENHANCED_MEMORY_READY:
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
        else:
            self.model = None

        # Runtime (non-persistent) memory
        self.session_context: Dict[str, Any] = {}

        logger.info("MemoryManager initialized successfully (v2.1).")

    # -------------------------------------------------
    # Encryption Utilities
    # -------------------------------------------------
    def _init_cipher(self):
        """Initialize encryption cipher, or fallback to None for plaintext."""
        try:
            if not os.path.exists(self.files["key"]):
                key = Fernet.generate_key()
                with open(self.files["key"], "wb") as f:
                    f.write(key)
            else:
                with open(self.files["key"], "rb") as f:
                    key = f.read()
            return Fernet(key)
        except Exception as e:
            logger.warning(f"Encryption key unavailable, fallback to plaintext. ({e})")
            return None

    def encrypt_data(self, text: str) -> str:
        if not self.cipher:
            return text
        try:
            return self.cipher.encrypt(text.encode()).decode()
        except Exception as e:
            logger.error(f"Encrypt failed: {e}")
            return text

    def decrypt_data(self, text: str) -> str:
        if not self.cipher:
            return text
        try:
            return self.cipher.decrypt(text.encode()).decode()
        except Exception:
            # fallback silently
            return text

    # -------------------------------------------------
    # File Load/Save Helpers
    # -------------------------------------------------
    def _load_json(self, key: str, default: Any) -> Any:
        """Safely load from JSON file, decrypting if applicable."""
        path = self.files[key]
        try:
            if os.path.exists(path) and os.path.getsize(path) > 0:
                with open(path, "r", encoding="utf-8") as f:
                    raw = f.read()
                    content = self.decrypt_data(raw)
                    return json.loads(content)
            else:
                return default
        except Exception as e:
            logger.warning(f"Error reading {key}: {e}")
            return default

    def _save_json(self, key: str, data: Any):
        """Save dictionary or list to encrypted JSON."""
        path = self.files[key]
        try:
            text = json.dumps(data, ensure_ascii=False, indent=2)
            encrypted = self.encrypt_data(text)
            with open(path, "w", encoding="utf-8") as f:
                f.write(encrypted)
        except Exception as e:
            logger.error(f"Failed saving {key}: {e}")

    # -------------------------------------------------
    # Embeddings
    # -------------------------------------------------
    def _load_embeddings(self):
        path = self.files["embeddings"]
        if os.path.exists(path):
            try:
                return np.load(path, allow_pickle=True)
            except Exception:
                logger.warning("Embeddings corrupted, resetting.")
        return np.zeros((0, 384))

    def _save_embeddings(self):
        try:
            np.save(self.files["embeddings"], self.embeddings)
        except Exception as e:
            logger.error(f"Failed saving embeddings: {e}")

    # -------------------------------------------------
    # Interaction / Semantic Storage
    # -------------------------------------------------
    def store_interaction(self, speaker: str, message: str) -> bool:
        """Stores chat interactions with semantic embeddings."""
        try:
            entry = {"time": datetime.now().isoformat(), "speaker": speaker, "message": message}
            self.interactions.append(entry)

            if ENHANCED_MEMORY_READY:
                vector = self.model.encode([message], convert_to_numpy=True)
                self.embeddings = np.vstack([self.embeddings, vector]) if self.embeddings.size else vector
                self._save_embeddings()

            # Keep memory trimmed
            if len(self.interactions) > 1000:
                self.interactions = self.interactions[-1000:]
                self.embeddings = self.embeddings[-1000:]
                self._save_embeddings()

            self._save_json("interactions", self.interactions)
            return True
        except Exception as e:
            logger.error(f"Store interaction failed: {e}")
            return False

    # -------------------------------------------------
    # Semantic Recall
    # -------------------------------------------------
    def recall_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Find semantically related past entries."""
        if not ENHANCED_MEMORY_READY or self.embeddings.size == 0:
            return []
        try:
            query_vec = self.model.encode([query], convert_to_numpy=True)
            scores = util.cos_sim(query_vec, self.embeddings)[0]
            top_index = np.argsort(-scores)[:top_k]
            return [{
                "message": self.interactions[i]["message"],
                "score": round(float(scores[i]), 3),
                "time": self.interactions[i]["time"]
            } for i in top_index]
        except Exception as e:
            logger.error(f"Recall failed: {e}")
            return []

    # -------------------------------------------------
    # Summarization (if OpenAI key set)
    # -------------------------------------------------
    def summarize_recent(self):
        """Compact summary of last ~50 messages."""
        key = self.get_preference("openai_api")
        if not key:
            return False
        try:
            openai.api_key = key
            recent_texts = "\n".join(i["message"] for i in self.interactions[-50:])
            prompt = f"Summarize the following recent messages briefly:\n{recent_texts}"
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a memory summarizer for a personal AI."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            summary = response.choices[0].message["content"].strip()
            self.context[f"summary_{datetime.now().strftime('%H%M%S')}"] = {"value": summary}
            self._save_json("context", self.context)
            return True
        except Exception as e:
            logger.error(f"Summarization error: {e}")
            return False

    # -------------------------------------------------
    # Context / Preferences
    # -------------------------------------------------
    def store_context(self, key: str, value: Any, persist: bool = True):
        obj = {"value": value, "timestamp": datetime.now().isoformat()}
        (self.context if persist else self.session_context)[key] = obj
        if persist:
            self._save_json("context", self.context)

    def get_context(self, key: str, default: Any = None):
        val = self.session_context.get(key) or self.context.get(key)
        return val.get("value", default) if val else default

    def store_preference(self, key: str, value: Any):
        self.preferences[key] = value
        self._save_json("preferences", self.preferences)

    def get_preference(self, key: str, default: Any = None):
        return self.preferences.get(key, default)

    # -------------------------------------------------
    # Utility / Cleanups
    # -------------------------------------------------
    def clear_all(self):
        """Reset all stored memory safely."""
        self.interactions, self.preferences, self.context = [], {}, {}
        self.embeddings = np.zeros((0, 384))
        for key in ["interactions", "preferences", "context"]:
            self._save_json(key, {})
        self._save_embeddings()
        logger.info("All memory cleared successfully.")
