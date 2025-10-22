#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Jarvis AI — Hybrid Memory Manager (Final Enhanced)
Features:
- Semantic embeddings for conceptual recall.
- Auto context injection for reasoning pipeline.
- Encrypted local memory with Fernet symmetric key.
- LLM-based summarization for long-term knowledge retention.
"""

import os
import json
import logging
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional

# ---------------- Dependencies ----------------
try:
    from cryptography.fernet import Fernet
    from sentence_transformers import SentenceTransformer, util
    import openai
    ENHANCED_MEMORY_READY = True
except ImportError:
    ENHANCED_MEMORY_READY = False
    logging.warning("Missing dependencies. Run: pip install cryptography sentence-transformers openai")

logger = logging.getLogger("Jarvis.MemoryManager")

class MemoryManager:
    """Advanced hybrid memory system managing contextual, semantic, and secure recall."""

    def __init__(self, data_dir: Optional[str] = None):
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = data_dir or os.path.join(base, "data")
        os.makedirs(self.data_dir, exist_ok=True)

        # File references
        self.files = {
            "interactions": os.path.join(self.data_dir, "interactions.json"),
            "preferences": os.path.join(self.data_dir, "preferences.json"),
            "context": os.path.join(self.data_dir, "context.json"),
            "embeddings": os.path.join(self.data_dir, "embeddings.npy"),
            "key": os.path.join(self.data_dir, "secret.key"),
        }

        # Loaders
        self.interactions = self._load_json("interactions", [])
        self.preferences = self._load_json("preferences", {})
        self.context = self._load_json("context", {})
        self.embeddings = self._load_embeddings()

        # Encryption key
        self.cipher = self._init_cipher()

        # Semantic & model setup
        if ENHANCED_MEMORY_READY:
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
        else:
            self.model = None

        # Runtime session context
        self.session_context: Dict[str, Any] = {}
        logger.info("Hybrid Memory Manager initialized (final build).")

    # ------------------------------------------------------------
    # UTILS
    # ------------------------------------------------------------
    def _load_json(self, key: str, default: Any) -> Any:
        path = self.files[key]
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    data = f.read()
                    return json.loads(self.decrypt_data(data))
            return default
        except Exception as e:
            logger.error(f"Error loading {path}: {e}")
            return default

    def _save_json(self, key: str, data: Any):
        path = self.files[key]
        try:
            payload = self.encrypt_data(json.dumps(data, ensure_ascii=False, indent=2))
            with open(path, "w", encoding="utf-8") as f:
                f.write(payload)
        except Exception as e:
            logger.error(f"Error saving {path}: {e}")

    def _init_cipher(self):
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
            logger.error(f"Failed to init encryption key: {e}")
            return None

    def _load_embeddings(self):
        path = self.files["embeddings"]
        try:
            return np.load(path) if os.path.exists(path) else np.zeros((0, 384))
        except Exception:
            return np.zeros((0, 384))

    def _save_embeddings(self):
        path = self.files["embeddings"]
        try:
            np.save(path, self.embeddings)
        except Exception as e:
            logger.error(f"Embedding save failed: {e}")

    # ------------------------------------------------------------
    # ENCRYPTION UTILITIES
    # ------------------------------------------------------------
    def encrypt_data(self, text: str) -> str:
        if self.cipher:
            return self.cipher.encrypt(text.encode()).decode()
        return text

    def decrypt_data(self, text: str) -> str:
        if self.cipher:
            try:
                return self.cipher.decrypt(text.encode()).decode()
            except:
                pass
        return text

    # ------------------------------------------------------------
    # MEMORY LAYERS: INTERACTION + SEMANTIC ENCODING
    # ------------------------------------------------------------
    def store_interaction(self, speaker: str, message: str) -> bool:
        """Store a conversation turn and semantic vector for meaning recall."""
        try:
            record = {"time": datetime.now().isoformat(), "speaker": speaker, "message": message}
            self.interactions.append(record)

            if ENHANCED_MEMORY_READY:
                embed = self.model.encode([message], convert_to_numpy=True)
                self.embeddings = np.vstack([self.embeddings, embed]) if self.embeddings.size else embed
                self._save_embeddings()

            # Auto summarization trigger every 250 entries
            if len(self.interactions) % 250 == 0:
                self._summarize_memory()

            if len(self.interactions) > 1000:
                self.interactions = self.interactions[-1000:]
                self.embeddings = self.embeddings[-1000:]
                self._save_embeddings()

            self._save_json("interactions", self.interactions)
            return True
        except Exception as e:
            logger.error(f"Interaction save failed: {e}")
            return False

    def _summarize_memory(self):
        """LLM-powered summarization for long-term recall."""
        key = self.preferences.get("openai_api", "")
        if not key:
            return
        try:
            openai.api_key = key
            text_entries = [i["message"] for i in self.interactions[-50:]]
            combined = "\n".join(text_entries)
            prompt = f"Summarize these 50 recent conversation entries briefly and factually:\n{combined}"
            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": "You are an AI summarizer."},
                          {"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=250
            )
            summary = resp.choices[0].message["content"].strip()
            self.context["summary_" + datetime.now().strftime("%H%M%S")] = {"value": summary}
            self._save_json("context", self.context)
            logger.info("LLM memory summarization completed.")
        except Exception as e:
            logger.error(f"Summarization failed: {e}")

    # ------------------------------------------------------------
    # SEMANTIC RECALL
    # ------------------------------------------------------------
    def recall_similar(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Returns past interactions semantically similar to the query."""
        if not ENHANCED_MEMORY_READY or self.embeddings.size == 0:
            return []
        try:
            q_emb = self.model.encode([query], convert_to_numpy=True)
            scores = util.cos_sim(q_emb, self.embeddings)[0]
            top_indices = np.argsort(-scores)[:top_k]
            return [{
                "message": self.interactions[i]["message"],
                "score": round(float(scores[i]), 3),
                "time": self.interactions[i]["time"]
            } for i in top_indices]
        except Exception as e:
            logger.error(f"Semantic recall failed: {e}")
            return []

    # ------------------------------------------------------------
    # CONTEXTUAL + AUTOMATIC INJECTION MODE
    # ------------------------------------------------------------
    def inject_context_into_prompt(self, query: str) -> str:
        """
        Builds an LLM-ready augmented prompt combining:
        - Last few interactions
        - Top semantic recalls
        - Persistent summaries
        """
        recents = [i["message"] for i in self.interactions[-5:]]
        recalls = [r["message"] for r in self.recall_similar(query, 3)]
        summaries = [v["value"] for k, v in self.context.items() if k.startswith("summary_")]
        prompt_context = " ".join(recents + recalls + summaries[-2:])
        return f"Previous context: {prompt_context}\nUser query: {query}"

    # ------------------------------------------------------------
    # PREFERENCES + CONTEXT STORAGE
    # ------------------------------------------------------------
    def store_preference(self, key: str, value: Any): 
        self.preferences[key] = value
        self._save_json("preferences", self.preferences)

    def get_preference(self, key: str, default: Any = None):
        return self.preferences.get(key, default)

    def store_context(self, key: str, value: Any, persist: bool = True):
        store = {"value": value, "timestamp": datetime.now().isoformat()}
        (self.context if persist else self.session_context)[key] = store
        if persist:
            self._save_json("context", self.context)

    def get_context(self, key: str, default: Any=None):
        val = self.session_context.get(key) or self.context.get(key)
        return val.get("value", default) if val else default

    # ------------------------------------------------------------
    # CLEAR
    # ------------------------------------------------------------
    def clear_all(self):
        self.interactions, self.context, self.preferences = [], {}, {}
        self.embeddings = np.zeros((0, 384))
        for key in ["interactions", "context", "preferences"]:
            self._save_json(key, {})
        self._save_embeddings()
        logger.info("Memory cleared successfully.")



