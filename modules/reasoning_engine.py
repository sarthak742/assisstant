#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Reasoning Engine Module for Jarvis AI Assistant (Improved)
Processes user commands and decides actions/context.
"""

import logging
import re
from modules.hybrid_task_manager import HybridTaskManager
from modules.memory_manager import MemoryManager
from modules.voice_module import VoiceModule

from typing import Dict, List, Any, Optional, Callable

logger = logging.getLogger("Jarvis.ReasoningEngine")

class ReasoningEngine:
    """
    Core Reasoning Engine for Jarvis AI.
    Handles multi-turn, context-based command routing.
    """

def __init__(self, memory_manager):
    self.memory = memory_manager
    self.voice = VoiceModule()
    self.task_manager = HybridTaskManager(memory_manager=self.memory, voice_module=self.voice)
    self.modules = {}
    self.session_history = []  # Stores full turn/context history for current session

        self.command_patterns = {
            'voice': [
                r'speak (louder|softer|faster|slower)',
                r'(stop|start) (speaking|listening)',
                r'change (your|the) voice',
                r'adjust (volume|speed|pitch)'
            ],
            'ai_chat': [
                r'(tell|ask|answer|explain|summarize|help)',
                r'what (is|are|was|were|do|does|did)',
                r'how (to|do|can|would|should)',
                r'why (is|are|do|does|did)',
                r'who (is|are|was|were)',
                r'when (is|are|was|were)',
                r'where (is|are|was|were)'
            ],
            'system': [
                r'(open|close|launch|run|start|stop) (file|folder|app|application|program)',
                r'(shutdown|restart|lock|sleep) (computer|pc|system)',
                r'(show|hide|minimize|maximize) (window|app|application)',
                r'(adjust|change) (brightness|volume|settings)'
            ],
            'internet': [
                r'search (for|about)',
                r'(check|get|show) (weather|news|email|calendar)',
                r'(play|find) (music|video|song)',
                r'(send|read) (email|message)'
            ],
            'automation': [
                r'(schedule|automate|create) (task|reminder|alarm)',
                r'(run|execute) (script|program|task)',
                r'(set|create|delete) (timer|alarm|reminder)'
            ],
            'security': [
                r'(lock|unlock|secure) (system|computer|pc)',
                r'(change|update) (password|security settings)',
                r'(enable|disable) (privacy mode|security feature)'
            ],
            'updater': [
                r'(update|upgrade) (yourself|system|feature)',
                r'(add|install|remove) (feature|module|capability)',
                r'(learn|improve) (new skill|ability)'
            ]
        }
        logger.info("Reasoning Engine initialized")

    def register_modules(self, modules: Dict[str, Any]) -> None:
        self.modules = modules
        logger.info(f"Registered {len(modules)} modules with Reasoning Engine")

    def process(self, command: str) -> str:
        """
        Main logic to process a user command.
        Returns generated response string.
        """
        try:
            logger.info(f"Processing command: {command}")
            self.session_history.append(command)
            self.memory.store_context('current_command', command)
            self.memory.store_context('session_history', self.session_history[-20:])  # Only last 20 turns

            module_name = self._determine_module(command)
            logger.debug(f"Intent: {module_name}")

            if not module_name or module_name not in self.modules:
                return self._fallback_response(command)

            module = self.modules[module_name]
            logger.info(f"Delegating command to {module_name} module")

            # Unified delegation logic
            method_map = {
                'voice': 'process_command',
                'ai_chat': 'generate_response',
                'system': 'execute_command',
                'internet': 'fetch_information',
                'automation': 'handle_automation',
                'security': 'handle_security',
                'updater': 'process_update_request'
            }

            method_name = method_map.get(module_name)
            if method_name and hasattr(module, method_name):
                return getattr(module, method_name)(command)
            else:
                return self._fallback_response(command)

        except Exception as e:
            logger.error(f"Error processing command: {str(e)}", exc_info=True)
            return f"I'm sorry, I encountered an error while processing your request. {str(e)}"

    def _determine_module(self, command: str) -> Optional[str]:
        """
        Determines which module should respond.
        """
        command = command.lower()
        direct_mentions = {
            'voice': ['voice', 'speak', 'listen', 'speech'],
            'ai_chat': ['chat', 'talk', 'conversation'],
            'system': ['system', 'computer', 'pc', 'file', 'folder'],
            'internet': ['internet', 'web', 'online', 'search'],
            'automation': ['automate', 'schedule', 'timer', 'alarm'],
            'security': ['security', 'password', 'privacy'],
            'updater': ['update', 'upgrade', 'install']
        }
        for module, keywords in direct_mentions.items():
            for keyword in keywords:
                if keyword in command:
                    return module
        for module, patterns in self.command_patterns.items():
            for pattern in patterns:
                if re.search(pattern, command, re.IGNORECASE):
                    return module
        return 'ai_chat'  # Default: chat/LLM

    def _fallback_response(self, command: str) -> str:
        """
        Respond if no module matches. Uses AI chat if present.
        """
        if 'ai_chat' in self.modules:
            return self.modules['ai_chat'].generate_response(
                f"I'm not sure how to process '{command}'. Can you please rephrase?"
            )
        return "I'm sorry, I don't understand that command. Can you please try again with different wording?"

    def add_command_pattern(self, module: str, pattern: str) -> bool:
        try:
            if module in self.command_patterns:
                self.command_patterns[module].append(pattern)
                logger.info(f"Added command pattern for {module}: {pattern}")
                return True
            logger.warning(f"Unknown module: {module}")
            return False
        except Exception as e:
            logger.error(f"Error adding command pattern: {str(e)}")
            return False

    def get_module_capabilities(self) -> Dict[str, List[str]]:
        capabilities = {}
        for module_name, patterns in self.command_patterns.items():
            if module_name in self.modules:
                capabilities[module_name] = [
                    p.replace('(', '').replace(')', '').replace('|', '/') 
                    for p in patterns
                ]
        return capabilities

    def clear_history(self):
        """Clears session history, useful for privacy or fresh context."""
        self.session_history = []
        self.memory.store_context('session_history', [])

