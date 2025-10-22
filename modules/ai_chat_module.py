#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AI & Chat Module for Jarvis AI Assistant (Enhanced)
Handles natural conversation, task dialogue, reasoning-based answers, and memory-reflective chat.
"""

import os
import logging
import json
import re
import openai
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger("Jarvis.AIChatModule")

class AIChatModule:
    """
    Conversational intelligence engine for Jarvis.
    Uses contextual reasoning, memory reflection, and LLM fallback for natural responses.
    """

    def __init__(self, memory_manager):
        self.memory = memory_manager
        self.responses = self._load_responses()
        self.context = {}
        self.api_keys = self.memory.get_preference("api_keys") or {}
        logger.info("AI & Chat Module initialized")

    # ------------------- LOADERS -------------------
    def _load_responses(self) -> Dict[str, List[str]]:
        path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "responses.json")
        defaults = {
            "greeting": ["Hello! How can I help?", "Hi there!", "Greetings! What can I do for you?"],
            "farewell": ["Goodbye!", "See you later!", "Until next time!"],
            "thanks": ["You're welcome!", "Glad to help!", "My pleasure!"],
            "unknown": ["I'm not sure I understand.", "Can you rephrase that?"],
            "fallback": ["I encountered a problem with that request."]
        }
        if not os.path.exists(path):
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(defaults, f, indent=2)
        try:
            with open(path, "r", encoding="utf-8") as f:
                custom = json.load(f)
                for key, val in defaults.items():
                    if key not in custom:
                        custom[key] = val
                return custom
        except Exception as e:
            logger.error(f"Error loading responses: {e}")
            return defaults

    # ------------------- MAIN INTERACTION -------------------
    def generate_response(self, query: str) -> str:
        try:
            logger.info(f"Generating response for: {query}")
            self.context["last_query"] = query
            self.context["last_query_time"] = datetime.now().isoformat()
            q = query.lower()

            if self._is_greeting(q):
                return self._get_response("greeting")
            if self._is_farewell(q):
                return self._get_response("farewell")
            if self._is_thanks(q):
                return self._get_response("thanks")
            if self._is_reminder_request(q):
                return self._handle_reminder(query)
            if self._is_alarm_request(q):
                return self._handle_alarm(query)
            if self._is_note_request(q):
                return self._handle_note(query)
            if self._is_question(q):
                return self._answer_question(query)

            # LLM reasoning fallback for open-ended conversation
            return self._generate_reasoning_response(query)
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self._get_response("fallback")

    # ------------------- CATEGORICAL DETECTION -------------------
    def _get_response(self, cat: str) -> str:
        import random
        return random.choice(self.responses.get(cat, ["I’m not sure what to say."]))

    def _is_greeting(self, q): return any(x in q for x in ["hello", "hi", "hey", "good morning", "good evening"])
    def _is_farewell(self, q): return any(x in q for x in ["bye", "goodbye", "see you", "later"])
    def _is_thanks(self, q): return any(x in q for x in ["thank you", "thanks", "appreciate"])
    def _is_reminder_request(self, q): return bool(re.search(r"(remind|reminder)", q))
    def _is_alarm_request(self, q): return bool(re.search(r"(alarm|wake up)", q))
    def _is_note_request(self, q): return bool(re.search(r"(note|remember this|write down|save this)", q))
    def _is_question(self, q): return "?" in q or re.search(r"\b(what|who|why|how|where|when)\b", q)

    # ------------------- TASK HANDLERS -------------------
    def _handle_reminder(self, q): return self._store_task("reminder", q, "I've set a reminder.")
    def _handle_alarm(self, q): return self._store_task("alarm", q, "Alarm scheduled.")
    def _handle_note(self, q): return self._store_task("note", q, "Note saved.")

    def _store_task(self, kind: str, content: str, msg: str) -> str:
        data = self.memory.get_context(f"{kind}s", [])
        data.append({"type": kind, "content": content, "created_at": datetime.now().isoformat(), "status": "active"})
        self.memory.store_context(f"{kind}s", data)
        return msg

    # ------------------- KNOWLEDGE & QUESTION HANDLING -------------------
    def _answer_question(self, query: str) -> str:
        q = query.lower()
        if "time" in q or "date" in q:
            now = datetime.now()
            return f"It is {now.strftime('%I:%M %p')} on {now.strftime('%A, %B %d, %Y')}."
        if "who are you" in q:
            return "I'm Jarvis, your personal assistant connected to your local and online systems."
        if "what can you do" in q:
            return "I can chat, run system tasks, fetch data, or reason through questions using AI integration."

        # Default reasoning fallback
        return self._generate_reasoning_response(query)

    # ------------------- MEMORY-AWARE LLM INTEGRATION -------------------
    def _generate_reasoning_response(self, query: str) -> str:
        """
        Uses OpenAI GPT (or compatible model) for contextual responses, incorporating memory and query.
        """
        llm_key = self.api_keys.get("openai", "")
        if not llm_key:
            return self._get_response("unknown")

        try:
            import openai
            openai.api_key = llm_key

            # Combine memory context with user query
            history = self.memory.get_recent_interactions(3)
            summary_context = " | ".join([i.get("message", "") for i in history]) if history else ""
            prompt = (
                f"You are Jarvis, an intelligent conversational assistant. "
                f"Context: {summary_context}. User query: {query}. "
                f"Provide a natural, friendly, and informative answer."
            )

            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an intelligent AI chat assistant named Jarvis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=300
            )
            message = response.choices[0].message["content"].strip()

            # Log and store interaction in memory
            self.memory.store_interaction("user", query)
            self.memory.store_interaction("jarvis", message)
            return message
        except Exception as e:
            logger.error(f"LLM reasoning error: {e}")
            return self._get_response("fallback")

    # ------------------- DATA RETRIEVAL -------------------
    def get_active_reminders(self) -> List[Dict[str, Any]]:
        return [r for r in self.memory.get_context("reminders", []) if r.get("status") == "active"]

    def get_active_alarms(self) -> List[Dict[str, Any]]:
        return [a for a in self.memory.get_context("alarms", []) if a.get("status") == "active"]

    def get_notes(self) -> List[Dict[str, Any]]:
        return self.memory.get_context("notes", [])
