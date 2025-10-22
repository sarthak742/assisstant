#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Memory Manager Module for Jarvis AI Assistant (Enhanced v2)
Manages persistent and contextual memory with smart separation:
- Short-term (session context)
- Long-term (summarized historical data)
- Persistent preferences
Adds: auto-trim, contextual recall, and future semantic embedding hooks.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger("Jarvis.MemoryManager")

class MemoryManager:
    """
    Adaptive Memory Manager for Jarvis.
    Handles short-term context (per session), long-term memory (stored + summarized),
    and persistent user preferences.
    """

    def __init__(self, data_dir: Optional[str] = None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.data_dir = data_dir or os.path.join(base_dir, 'data')
        os.makedirs(self.data_dir, exist_ok=True)

        # File paths
        self.memory_files = {
            "interactions": os.path.join(self.data_dir, "interactions.json"),
            "preferences": os.path.join(self.data_dir, "preferences.json"),
            "context": os.path.join(self.data_dir, "context.json"),
            "summaries": os.path.join(self.data_dir, "summaries.json")
        }

        # Load persisted states
        self.interactions = self._load_data("interactions", [])
        self.preferences  = self._load_data("preferences", {})
        self.context      = self._load_data("context", {})
        self.summaries    = self._load_data("summaries", [])

        # Volatile session memory (short-term)
        self.session_context: Dict[str, Any] = {}

        logger.info("Enhanced Memory Manager initialized.")

    # ------------------- Persistence Utilities -------------------
    def _load_data(self, key: str, default: Any) -> Any:
        path = self.memory_files[key]
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
            return default
        except Exception as e:
            logger.error(f"Error loading {path}: {e}")
            return default

    def _save_data(self, key: str, data: Any) -> bool:
        path = self.memory_files[key]
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving {path}: {e}")
            return False

    # ------------------- Interaction Memory -------------------
    def store_interaction(self, speaker: str, message: str) -> bool:
        """Stores single interaction and maintains rolling window."""
        try:
            interaction = {
                "time": datetime.now().isoformat(),
                "speaker": speaker,
                "message": message
            }
            self.interactions.append(interaction)

            # Keep manageable window
            if len(self.interactions) > 1000:
                self._archive_old_interactions()

            return self._save_data("interactions", self.interactions)
        except Exception as e:
            logger.error(f"Interaction store failed: {e}")
            return False

    def _archive_old_interactions(self):
        """Summarizes old interactions before trimming (for long-term context)."""
        try:
            old_block = self.interactions[:-500]
            summary_text = self._generate_summary_text(old_block)
            self.summaries.append({
                "summary": summary_text,
                "timestamp": datetime.now().isoformat()
            })
            self.interactions = self.interactions[-500:]
            self._save_data("summaries", self.summaries)
            logger.info("Archived and summarized old interactions.")
        except Exception as e:
            logger.error(f"Archiving error: {e}")

    def get_recent_interactions(self, count: int = 10) -> List[Dict[str, str]]:
        return self.interactions[-count:]

    def get_conversation_history(self, as_text: bool = False) -> Any:
        if not as_text:
            return self.interactions
        formatted = []
        for inter in self.interactions[-50:]:
            t = datetime.fromisoformat(inter["time"]).strftime("%H:%M:%S")
            speaker = "You" if inter["speaker"] == "user" else "Jarvis"
            formatted.append(f"[{t}] {speaker}: {inter['message']}")
        return "\n".join(formatted)

    def clear_interactions(self) -> bool:
        self.interactions = []
        return self._save_data("interactions", self.interactions)

    # ------------------- Context Memory -------------------
    def store_context(self, key: str, value: Any, persist: bool = False):
        try:
            context_obj = {"value": value, "timestamp": datetime.now().isoformat()}
            if persist:
                self.context[key] = context_obj
                return self._save_data("context", self.context)
            else:
                self.session_context[key] = context_obj
                return True
        except Exception as e:
            logger.error(f"Context store error: {e}")
            return False

    def get_context(self, key: str, default: Any = None, use_session: bool = True) -> Any:
        source = self.session_context.get(key) if use_session else None
        if not source:
            source = self.context.get(key)
        return source.get("value", default) if source else default

    def clear_context(self, persistent: bool = False) -> bool:
        try:
            if persistent:
                self.context = {}
                self._save_data("context", self.context)
            self.session_context = {}
            return True
        except Exception as e:
            logger.error(f"Context clear error: {e}")
            return False

    # ------------------- Preferences -------------------
    def store_preference(self, key: str, value: Any):
        try:
            self.preferences[key] = value
            return self._save_data("preferences", self.preferences)
        except Exception as e:
            logger.error(f"Preference storage error: {e}")
            return False

    def get_preference(self, key: str, default: Any = None):
        return self.preferences.get(key, default)

    # ------------------- Smart Recall -------------------
    def recall_contextual_summary(self) -> str:
        """
        Returns a summarized form of long-term memory for reasoning or LLM prompt injection.
        """
        try:
            summaries = [s["summary"] for s in self.summaries[-3:]]
            combined = " ".join(summaries)
            if not combined:
                recent = " ".join([i["message"] for i in self.interactions[-10:]])
                return f"Recent memory: {recent}"
            return f"Historical context: {combined}"
        except Exception as e:
            logger.error(f"Recall error: {e}")
            return ""

    def _generate_summary_text(self, interactions: List[Dict]) -> str:
        """
        Summarizes a batch of old interactions (extractive-style).
        Simple heuristic placeholder for future LLM summarization.
        """
        try:
            user_messages = [i["message"] for i in interactions if i["speaker"] == "user"]
            joined = " ".join(user_messages)
            if len(joined) > 500:
                return "Summary: " + joined[:500] + "..."
            return "Summary: " + joined
        except Exception as e:
            logger.error(f"Summary generation failed: {e}")
            return ""

    # ------------------- Security (Placeholder) -------------------
    def encrypt_data(self, text: str) -> str:
        # Future AES/fernet encryption integration
        return text

    def decrypt_data(self, text: str) -> str:
        return text

