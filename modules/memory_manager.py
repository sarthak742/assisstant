#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Memory Manager Module for Jarvis AI Assistant (Improved)
Manages persistent and contextual memory with short-term and long-term separation.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger("Jarvis.MemoryManager")

class MemoryManager:
    """
    Memory Manager for Jarvis. Handles:
    - Short-term/session context
    - Long-term interactions
    - Preferences
    - Secure/extendible storage
    """

    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data'
        )
        os.makedirs(self.data_dir, exist_ok=True)

        # File paths
        self.interactions_file = os.path.join(self.data_dir, 'interactions.json')
        self.preferences_file  = os.path.join(self.data_dir, 'preferences.json')
        self.context_file      = os.path.join(self.data_dir, 'context.json')

        # Load structures
        self.interactions = self._load_data(self.interactions_file, [])
        self.preferences  = self._load_data(self.preferences_file, {})
        self.context      = self._load_data(self.context_file, {})

        # Session-specific short-term context (not persisted)
        self.session_context = {}

        logger.info("Memory Manager initialized")

    def _load_data(self, file_path: str, default: Any = None) -> Any:
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return default
        except Exception as e:
            logger.error(f"Error loading {file_path}: {str(e)}")
            return default

    def _save_data(self, file_path: str, data: Any) -> bool:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving {file_path}: {str(e)}")
            return False

    # === Interactions and Long-Term History ===
    def store_interaction(self, speaker: str, message: str) -> bool:
        try:
            interaction = {
                'timestamp': datetime.now().isoformat(),
                'speaker': speaker,
                'message': message
            }
            self.interactions.append(interaction)
            if len(self.interactions) > 500:
                self.interactions = self.interactions[-500:]
            return self._save_data(self.interactions_file, self.interactions)
        except Exception as e:
            logger.error(f"Error storing interaction: {str(e)}")
            return False

    def get_recent_interactions(self, count: int = 10) -> List[Dict]:
        return self.interactions[-count:]

    def clear_interactions(self) -> bool:
        try:
            self.interactions = []
            return self._save_data(self.interactions_file, self.interactions)
        except Exception as e:
            logger.error(f"Error clearing interactions: {str(e)}")
            return False

    def get_conversation_history(self, as_text: bool = False) -> Any:
        if not as_text:
            return self.interactions
        history = []
        for interaction in self.interactions:
            speaker = "You" if interaction['speaker'] == 'user' else "Jarvis"
            timestamp = datetime.fromisoformat(interaction['timestamp']).strftime("%H:%M:%S")
            history.append(f"[{timestamp}] {speaker}: {interaction['message']}")
        return "\n".join(history)

    # === Preferences (Persistent) ===
    def store_preference(self, key: str, value: Any) -> bool:
        try:
            self.preferences[key] = value
            return self._save_data(self.preferences_file, self.preferences)
        except Exception as e:
            logger.error(f"Error storing preference: {str(e)}")
            return False

    def get_preference(self, key: str, default: Any = None) -> Any:
        return self.preferences.get(key, default)

    # === Context Management ===
    def store_context(self, key: str, value: Any, persist: bool = False) -> bool:
        """
        Store context.
        If persist=True, saves to disk; otherwise, temporary for session only.
        """
        try:
            if persist:
                self.context[key] = {'value': value, 'timestamp': datetime.now().isoformat()}
                return self._save_data(self.context_file, self.context)
            else:
                self.session_context[key] = {'value': value, 'timestamp': datetime.now().isoformat()}
                return True
        except Exception as e:
            logger.error(f"Error storing context: {str(e)}")
            return False

    def get_context(self, key: str, default: Any = None, use_session: bool = True) -> Any:
        """
        Get context.
        If use_session=True, checks temp session context first, then persistent.
        """
        context_data = self.session_context.get(key) if use_session else None
        if not context_data:
            context_data = self.context.get(key)
        return context_data.get('value', default) if context_data else default

    def clear_context(self, persistent: bool = False) -> bool:
        try:
            if persistent:
                self.context = {}
                return self._save_data(self.context_file, self.context)
            else:
                self.session_context = {}
                return True
        except Exception as e:
            logger.error(f"Error clearing context: {str(e)}")
            return False

    # === Security Placeholder ===
    def encrypt_data(self, text: str) -> str:
        # Stub: Future implementation for encrypted local memory
        return text

    def decrypt_data(self, text: str) -> str:
        # Stub: Future implementation for encrypted local memory
        return text
