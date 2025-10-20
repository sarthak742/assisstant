#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI & Chat Module for Jarvis AI Assistant
Handles natural language conversation, question answering, and task assistance.
"""

import os
import logging
import json
import re
import time
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger("Jarvis.AIChatModule")

class AIChatModule:
    """
    AI & Chat Module class that handles natural language conversation,
    question answering, and task assistance.
    """
    
    def __init__(self, memory_manager):
        """
        Initialize the AI & Chat Module.
        
        Args:
            memory_manager: Reference to the Memory Manager module
        """
        self.memory = memory_manager
        self.responses = self._load_responses()
        self.context = {}
        
        logger.info("AI & Chat Module initialized")
    
    def _load_responses(self) -> Dict[str, List[str]]:
        """
        Load predefined responses from a JSON file.
        
        Returns:
            Dictionary of response categories and their templates
        """
        responses_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data',
            'responses.json'
        )
        
        default_responses = {
            "greeting": [
                "Hello! How can I help you today?",
                "Hi there! What can I do for you?",
                "Greetings! How may I assist you?"
            ],
            "farewell": [
                "Goodbye! Have a great day!",
                "See you later!",
                "Until next time!"
            ],
            "thanks": [
                "You're welcome!",
                "Happy to help!",
                "My pleasure!"
            ],
            "unknown": [
                "I'm not sure I understand. Could you rephrase that?",
                "I don't have an answer for that yet.",
                "I'm still learning about that."
            ],
            "fallback": [
                "I'm sorry, I couldn't process that request.",
                "I encountered an issue with that request.",
                "I'm having trouble with that right now."
            ]
        }
        
        try:
            if os.path.exists(responses_file):
                with open(responses_file, 'r', encoding='utf-8') as f:
                    loaded_responses = json.load(f)
                    # Merge with default responses, keeping custom ones if they exist
                    for category, templates in default_responses.items():
                        if category not in loaded_responses:
                            loaded_responses[category] = templates
                    return loaded_responses
            else:
                # Create the default responses file
                os.makedirs(os.path.dirname(responses_file), exist_ok=True)
                with open(responses_file, 'w', encoding='utf-8') as f:
                    json.dump(default_responses, f, ensure_ascii=False, indent=2)
                return default_responses
        except Exception as e:
            logger.error(f"Error loading responses: {str(e)}")
            return default_responses
    
    def generate_response(self, query: str) -> str:
        """
        Generate a response to a user query.
        
        Args:
            query: User query string
            
        Returns:
            Response string
        """
        try:
            logger.info(f"Generating response for: {query}")
            
            # Update context with the current query
            self.context['last_query'] = query
            self.context['last_query_time'] = datetime.now().isoformat()
            
            # Check for special query types
            if self._is_greeting(query):
                return self._get_response("greeting")
            
            if self._is_farewell(query):
                return self._get_response("farewell")
            
            if self._is_thanks(query):
                return self._get_response("thanks")
            
            # Check for task assistance queries
            if self._is_reminder_request(query):
                return self._handle_reminder(query)
            
            if self._is_alarm_request(query):
                return self._handle_alarm(query)
            
            if self._is_note_request(query):
                return self._handle_note(query)
            
            # Check for question answering
            if self._is_question(query):
                return self._answer_question(query)
            
            # Default to a general response
            return self._generate_general_response(query)
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return self._get_response("fallback")
    
    def _get_response(self, category: str) -> str:
        """
        Get a random response from a category.
        
        Args:
            category: Response category
            
        Returns:
            Response string
        """
        import random
        
        if category in self.responses and self.responses[category]:
            return random.choice(self.responses[category])
        else:
            return "I'm not sure what to say about that."
    
    def _is_greeting(self, query: str) -> bool:
        """Check if the query is a greeting."""
        greetings = ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening']
        return any(greeting in query.lower() for greeting in greetings)
    
    def _is_farewell(self, query: str) -> bool:
        """Check if the query is a farewell."""
        farewells = ['goodbye', 'bye', 'see you', 'farewell', 'good night', 'later']
        return any(farewell in query.lower() for farewell in farewells)
    
    def _is_thanks(self, query: str) -> bool:
        """Check if the query is an expression of gratitude."""
        thanks = ['thank you', 'thanks', 'appreciate it', 'grateful']
        return any(thank in query.lower() for thank in thanks)
    
    def _is_reminder_request(self, query: str) -> bool:
        """Check if the query is a reminder request."""
        reminder_patterns = [
            r'remind me (to|about)',
            r'set a reminder',
            r'don\'t let me forget'
        ]
        return any(re.search(pattern, query.lower()) for pattern in reminder_patterns)
    
    def _is_alarm_request(self, query: str) -> bool:
        """Check if the query is an alarm request."""
        alarm_patterns = [
            r'set (an|a) alarm',
            r'wake me up at',
            r'alarm for'
        ]
        return any(re.search(pattern, query.lower()) for pattern in alarm_patterns)
    
    def _is_note_request(self, query: str) -> bool:
        """Check if the query is a note request."""
        note_patterns = [
            r'take a note',
            r'write (this|that) down',
            r'make a note',
            r'save this'
        ]
        return any(re.search(pattern, query.lower()) for pattern in note_patterns)
    
    def _is_question(self, query: str) -> bool:
        """Check if the query is a question."""
        # Check for question words or question marks
        question_indicators = ['what', 'who', 'where', 'when', 'why', 'how', 'can', 'could', 'would', 'should', 'is', 'are', 'do', 'does', '?']
        return any(indicator in query.lower().split() for indicator in question_indicators) or '?' in query
    
    def _handle_reminder(self, query: str) -> str:
        """
        Handle a reminder request.
        
        Args:
            query: User query string
            
        Returns:
            Response string
        """
        # Extract reminder details (this is a simplified implementation)
        # In a real implementation, you would use NLP to extract the task and time
        
        # Store the reminder in memory
        reminder = {
            'type': 'reminder',
            'content': query,
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        self.memory.store_context('reminders', 
                                 self.memory.get_context('reminders', []) + [reminder])
        
        return "I've set a reminder for you. I'll remind you about that."
    
    def _handle_alarm(self, query: str) -> str:
        """
        Handle an alarm request.
        
        Args:
            query: User query string
            
        Returns:
            Response string
        """
        # Extract alarm details (this is a simplified implementation)
        # In a real implementation, you would use NLP to extract the time
        
        # Store the alarm in memory
        alarm = {
            'type': 'alarm',
            'content': query,
            'created_at': datetime.now().isoformat(),
            'status': 'active'
        }
        
        self.memory.store_context('alarms', 
                                self.memory.get_context('alarms', []) + [alarm])
        
        return "I've set an alarm for you."
    
    def _handle_note(self, query: str) -> str:
        """
        Handle a note request.
        
        Args:
            query: User query string
            
        Returns:
            Response string
        """
        # Extract note content (this is a simplified implementation)
        # In a real implementation, you would use NLP to extract the note content
        
        # Remove the command part to get the note content
        note_content = re.sub(r'^(take a note|write this down|make a note|save this)[\s:]*', '', query, flags=re.IGNORECASE).strip()
        
        if not note_content:
            note_content = "Empty note"
        
        # Store the note in memory
        note = {
            'type': 'note',
            'content': note_content,
            'created_at': datetime.now().isoformat()
        }
        
        self.memory.store_context('notes', 
                                self.memory.get_context('notes', []) + [note])
        
        return f"I've saved your note: '{note_content}'"
    
    def _answer_question(self, query: str) -> str:
        """
        Answer a question.
        
        Args:
            query: User question string
            
        Returns:
            Answer string
        """
        # This is a simplified implementation
        # In a real implementation, you would use an LLM or knowledge base
        
        # Check for time-related questions
        if re.search(r'what (time|day|date) is it', query.lower()):
            now = datetime.now()
            return f"It's {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d, %Y')}."
        
        # Check for personal questions about Jarvis
        if re.search(r'who are you', query.lower()):
            return "I'm Jarvis, your personal AI assistant. I'm here to help you with various tasks."
        
        if re.search(r'what can you do', query.lower()):
            return ("I can help you with various tasks including answering questions, setting reminders and alarms, "
                   "taking notes, controlling your system, searching the web, and more.")
        
        # For other questions, return a generic response
        return "I don't have a specific answer for that question yet. Would you like me to search the web for you?"
    
    def _generate_general_response(self, query: str) -> str:
        """
        Generate a general response for queries that don't match specific patterns.
        
        Args:
            query: User query string
            
        Returns:
            Response string
        """
        # Check recent conversation history for context
        recent_interactions = self.memory.get_recent_interactions(5)
        
        # If we have context, try to generate a more relevant response
        if recent_interactions:
            # This is where you would integrate with a more sophisticated language model
            # For now, we'll just return a simple response
            return "I understand you're asking about that. How can I help you further?"
        
        # Default response if we can't generate a contextual one
        return self._get_response("unknown")
    
    def summarize_text(self, text: str, max_length: int = 100) -> str:
        """
        Summarize a text.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of the summary
            
        Returns:
            Summarized text
        """
        # This is a simplified implementation
        # In a real implementation, you would use an NLP model for summarization
        
        # Simple extractive summarization by taking the first few sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        summary = ""
        for sentence in sentences:
            if len(summary) + len(sentence) <= max_length:
                summary += sentence + " "
            else:
                break
        
        return summary.strip()
    
    def get_active_reminders(self) -> List[Dict[str, Any]]:
        """
        Get all active reminders.
        
        Returns:
            List of active reminders
        """
        reminders = self.memory.get_context('reminders', [])
        return [r for r in reminders if r.get('status') == 'active']
    
    def get_active_alarms(self) -> List[Dict[str, Any]]:
        """
        Get all active alarms.
        
        Returns:
            List of active alarms
        """
        alarms = self.memory.get_context('alarms', [])
        return [a for a in alarms if a.get('status') == 'active']
    
    def get_notes(self) -> List[Dict[str, Any]]:
        """
        Get all notes.
        
        Returns:
            List of notes
        """
        return self.memory.get_context('notes', [])