#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Memory Manager Module for Jarvis AI Assistant
Responsible for storing and retrieving user interactions, preferences, and context.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger("Jarvis.MemoryManager")

class MemoryManager:
    """
    Memory Manager class that handles storage and retrieval of user interactions,
    preferences, and contextual information.
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the Memory Manager.
        
        Args:
            data_dir: Directory to store memory data. Defaults to 'data' in the project root.
        """
        if data_dir is None:
            # Default to 'data' directory in the project root
            self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
        else:
            self.data_dir = data_dir
            
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # File paths for different types of data
        self.interactions_file = os.path.join(self.data_dir, 'interactions.json')
        self.preferences_file = os.path.join(self.data_dir, 'preferences.json')
        self.context_file = os.path.join(self.data_dir, 'context.json')
        
        # Initialize data structures
        self.interactions = self._load_data(self.interactions_file, default=[])
        self.preferences = self._load_data(self.preferences_file, default={})
        self.context = self._load_data(self.context_file, default={})
        
        logger.info("Memory Manager initialized")
    
    def _load_data(self, file_path: str, default: Any = None) -> Any:
        """
        Load data from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            default: Default value if file doesn't exist or is invalid
            
        Returns:
            Loaded data or default value
        """
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return default
        except Exception as e:
            logger.error(f"Error loading data from {file_path}: {str(e)}")
            return default
    
    def _save_data(self, file_path: str, data: Any) -> bool:
        """
        Save data to a JSON file.
        
        Args:
            file_path: Path to the JSON file
            data: Data to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving data to {file_path}: {str(e)}")
            return False
    
    def store_interaction(self, speaker: str, message: str) -> bool:
        """
        Store a user or Jarvis interaction.
        
        Args:
            speaker: Who is speaking ('user' or 'jarvis')
            message: The message content
            
        Returns:
            True if successful, False otherwise
        """
        try:
            interaction = {
                'timestamp': datetime.now().isoformat(),
                'speaker': speaker,
                'message': message
            }
            self.interactions.append(interaction)
            
            # Keep only the last 100 interactions to avoid excessive memory usage
            if len(self.interactions) > 100:
                self.interactions = self.interactions[-100:]
                
            return self._save_data(self.interactions_file, self.interactions)
        except Exception as e:
            logger.error(f"Error storing interaction: {str(e)}")
            return False
    
    def get_recent_interactions(self, count: int = 10) -> List[Dict]:
        """
        Get the most recent interactions.
        
        Args:
            count: Number of recent interactions to retrieve
            
        Returns:
            List of recent interactions
        """
        return self.interactions[-count:] if self.interactions else []
    
    def store_preference(self, key: str, value: Any) -> bool:
        """
        Store a user preference.
        
        Args:
            key: Preference key
            value: Preference value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.preferences[key] = value
            return self._save_data(self.preferences_file, self.preferences)
        except Exception as e:
            logger.error(f"Error storing preference: {str(e)}")
            return False
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        Get a user preference.
        
        Args:
            key: Preference key
            default: Default value if preference doesn't exist
            
        Returns:
            Preference value or default
        """
        return self.preferences.get(key, default)
    
    def store_context(self, key: str, value: Any) -> bool:
        """
        Store contextual information.
        
        Args:
            key: Context key
            value: Context value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.context[key] = {
                'value': value,
                'timestamp': datetime.now().isoformat()
            }
            return self._save_data(self.context_file, self.context)
        except Exception as e:
            logger.error(f"Error storing context: {str(e)}")
            return False
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """
        Get contextual information.
        
        Args:
            key: Context key
            default: Default value if context doesn't exist
            
        Returns:
            Context value or default
        """
        context_data = self.context.get(key, {})
        return context_data.get('value', default) if context_data else default
    
    def clear_interactions(self) -> bool:
        """
        Clear all stored interactions.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.interactions = []
            return self._save_data(self.interactions_file, self.interactions)
        except Exception as e:
            logger.error(f"Error clearing interactions: {str(e)}")
            return False
    
    def clear_context(self) -> bool:
        """
        Clear all contextual information.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.context = {}
            return self._save_data(self.context_file, self.context)
        except Exception as e:
            logger.error(f"Error clearing context: {str(e)}")
            return False
    
    def get_conversation_history(self, as_text: bool = False) -> Any:
        """
        Get the full conversation history.
        
        Args:
            as_text: If True, return as formatted text, otherwise as a list of dictionaries
            
        Returns:
            Conversation history
        """
        if not as_text:
            return self.interactions
        
        # Format as text
        history = []
        for interaction in self.interactions:
            speaker = "You" if interaction['speaker'] == 'user' else "Jarvis"
            timestamp = datetime.fromisoformat(interaction['timestamp']).strftime("%H:%M:%S")
            history.append(f"[{timestamp}] {speaker}: {interaction['message']}")
        
        return "\n".join(history)