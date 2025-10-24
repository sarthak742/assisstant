#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Reasoning Engine Module for Jarvis AI Assistant (Final v2.1)
------------------------------------------------------------
- Handles command understanding and action routing
- Integrates with HybridTaskManager, VoiceModule, and MemoryManager
- Avoids circular imports & startup conflicts
"""

import logging
import re
from typing import Dict, List, Any, Optional

from modules.memory_manager import MemoryManager
from modules.voice_module import VoiceModule
from modules.hybrid_task_manager import HybridTaskManager

logger = logging.getLogger("Jarvis.ReasoningEngine")


class ReasoningEngine:
    """Drives reasoning and intelligent action execution in Jarvis."""

    def __init__(self, memory_manager: MemoryManager):
        self.memory = memory_manager
        self.voice = VoiceModule(reasoning_engine=self)
        self.task_manager = HybridTaskManager(memory_manager=self.memory, voice_module=self.voice)
        self.modules: Dict[str, Any] = {}
        self.session_history: List[str] = []

        # Intent patterns for smart command routing
        self.command_patterns = {
            "voice": [
                r"speak (louder|softer|faster|slower)",
                r"(stop|start) (speaking|listening)",
                r"change (your|the) voice",
                r"adjust (volume|speed|pitch)"
            ],
            "ai_chat": [
                r"(tell|ask|answer|explain|summarize|help)",
                r"what (is|are|was|were|do|does|did)",
                r"how (to|do|can|would|should)",
                r"why (is|are|do|does|did)",
                r"who (is|are|was|were)",
                r"when (is|are|was|were)",
                r"where (is|are|was|were)"
            ],
            "system": [
                r"(open|close|launch|run|start|stop) (file|folder|app|application|program)",
                r"(shutdown|restart|lock|sleep) (computer|pc|system)",
                r"(show|hide|minimize|maximize) (window|app|application)",
                r"(adjust|change) (brightness|volume|settings)"
            ],
            "internet": [
                r"search (for|about)",
                r"(check|get|show) (weather|news|email|calendar)",
                r"(play|find) (music|video|song)",
                r"(send|read) (email|message)"
            ],
            "automation": [
                r"(schedule|automate|create) (task|reminder|alarm)",
                r"(run|execute) (script|program|task)",
                r"(set|create|delete) (timer|alarm|reminder)"
            ],
            "security": [
                r"(lock|unlock|secure) (system|computer|pc)",
                r"(change|update) (password|security settings)",
                r"(enable|disable) (privacy mode|security feature)"
            ],
            "updater": [
                r"(update|upgrade) (yourself|system|feature)",
                r"(add|install|remove) (feature|module|capability)",
                r"(learn|improve) (new skill|ability)"
            ]
        }
        logger.info("Reasoning Engine initialized successfully.")

    # -------------------------------------------------
    # Module Registration
    # -------------------------------------------------
    def register_modules(self, modules: Dict[str, Any]) -> None:
        """Registers external modules (AI chat, internet, etc.)"""
        self.modules = modules
        logger.info(f"Registered {len(modules)} modules with Reasoning Engine.")

    # -------------------------------------------------
    # Command Processing Core
    # -------------------------------------------------
    def process(self, command: str) -> str:
        """Core logic for interpreting and executing commands."""
        try:
            logger.info(f"Processing command: {command}")
            self.session_history.append(command)
            self.memory.store_context("current_command", command)
            self.memory.store_context("session_history", self.session_history[-25:])

            command_lower = command.lower().strip()

            # ---- Route automation / system commands ----
            if command_lower.startswith((
                "open", "launch", "start", "run", "create",
                "delete", "move", "send", "close", "shutdown",
                "restart", "lock", "sleep"
            )):
                logger.info("Routing automation command through HybridTaskManager.")
                return self.task_manager.execute_system_command(command_lower)

            # ---- Determine module intent ----
            module_name = self._determine_module(command)
            logger.debug(f"Detected intent: {module_name}")

            if not module_name or module_name not in self.modules:
                return self._fallback_response(command)

            module = self.modules[module_name]
            logger.info(f"Delegating command to {module_name} module.")

            method_map = {
                "voice": "process_command",
                "ai_chat": "generate_response",
                "system": "execute_command",
                "internet": "fetch_information",
                "automation": "handle_automation",
                "security": "handle_security",
                "updater": "process_update_request"
            }

            method_name = method_map.get(module_name)
            if method_name and hasattr(module, method_name):
                return getattr(module, method_name)(command)
            else:
                return self._fallback_response(command)

        except Exception as e:
            logger.error(f"Error while processing: {e}", exc_info=True)
            self.voice.speak("Sorry, there was an internal error.")
            return f"An internal error occurred: {e}"

    # -------------------------------------------------
    # Intent Detection Logic
    # -------------------------------------------------
    def _determine_module(self, command: str) -> Optional[str]:
        """Identify which logic domain (module) the command belongs to."""
        command = command.lower()

        direct_mentions = {
            "voice": ["voice", "speak", "listen", "speech"],
            "ai_chat": ["chat", "talk", "conversation"],
            "system": ["system", "computer", "pc", "file", "folder"],
            "internet": ["internet", "web", "online", "search"],
            "automation": ["automate", "schedule", "timer", "alarm"],
            "security": ["security", "password", "privacy"],
            "updater": ["update", "upgrade", "install"]
        }

        # Keyword-based detection
        for module, keywords in direct_mentions.items():
            for word in keywords:
                if word in command:
                    return module

        # Regex pattern matching
        for module, patterns in self.command_patterns.items():
            for pattern in patterns:
                if re.search(pattern, command, re.IGNORECASE):
                    return module

        # Default fallback
        return "ai_chat"

    # -------------------------------------------------
    # Fallback / Error Handling
    # -------------------------------------------------
    def _fallback_response(self, command: str) -> str:
        """Fallback for unrecognized or unclassified commands."""
        if "ai_chat" in self.modules:
            prompt = f"I'm not sure how to process '{command}'. Could you please rephrase?"
            return self.modules["ai_chat"].generate_response(prompt)
        self.voice.speak("I’m sorry, I didn’t understand that command.")
        return "I’m sorry, I don’t understand that yet."

    # -------------------------------------------------
    # Utility / Extensibility
    # -------------------------------------------------
    def add_command_pattern(self, module: str, pattern: str) -> bool:
        """Allows new regex patterns to be added dynamically."""
        try:
            if module in self.command_patterns:
                self.command_patterns[module].append(pattern)
                logger.info(f"Added new command pattern for {module}: {pattern}")
                return True
            logger.warning(f"Unknown target module '{module}'")
            return False
        except Exception as e:
            logger.error(f"Failed to add command pattern: {e}")
            return False

    def get_module_capabilities(self) -> Dict[str, List[str]]:
        """Returns all command patterns and registered modules for diagnostics."""
        capabilities = {}
        for module_name, patterns in self.command_patterns.items():
            if module_name in self.modules:
                clean_patterns = [p.replace("(", "").replace(")", "").replace("|", "/") for p in patterns]
                capabilities[module_name] = clean_patterns
        return capabilities

    def clear_history(self):
        """Wipes conversational memory and context."""
        self.session_history = []
        self.memory.store_context("session_history", [])
        logger.info("Session history cleared successfully.")
