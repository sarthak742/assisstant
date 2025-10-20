#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Reasoning Engine Module for Jarvis AI Assistant
Responsible for processing user commands and deciding the appropriate actions.
"""

import logging
import re
from typing import Dict, List, Any, Optional, Callable

logger = logging.getLogger("Jarvis.ReasoningEngine")

class ReasoningEngine:
    """
    Reasoning Engine class that processes user commands and decides which modules
    to use for responding to user requests.
    """
    
    def __init__(self, memory_manager):
        """
        Initialize the Reasoning Engine.
        
        Args:
            memory_manager: Reference to the Memory Manager module
        """
        self.memory = memory_manager
        self.modules = {}
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
        """
        Register modules with the reasoning engine.
        
        Args:
            modules: Dictionary of module names and their instances
        """
        self.modules = modules
        logger.info(f"Registered {len(modules)} modules with the Reasoning Engine")
    
    def process(self, command: str) -> str:
        """
        Process a user command and determine the appropriate action.
        
        Args:
            command: User command string
            
        Returns:
            Response string
        """
        try:
            logger.info(f"Processing command: {command}")
            
            # Store command context
            self.memory.store_context('current_command', command)
            
            # Determine which module should handle the command
            module_name = self._determine_module(command)
            
            if not module_name or module_name not in self.modules:
                return self._fallback_response(command)
            
            # Get the appropriate module
            module = self.modules[module_name]
            
            # Process the command with the selected module
            logger.info(f"Delegating command to {module_name} module")
            
            # Different modules have different processing methods
            if module_name == 'voice':
                # Voice module commands are handled differently
                return module.process_command(command)
            elif module_name == 'ai_chat':
                # AI Chat module handles natural language queries
                return module.generate_response(command)
            elif module_name == 'system':
                # System control module handles system commands
                return module.execute_command(command)
            elif module_name == 'internet':
                # Internet module handles online queries
                return module.fetch_information(command)
            elif module_name == 'automation':
                # Automation module handles task scheduling
                return module.handle_automation(command)
            elif module_name == 'security':
                # Security module handles security-related commands
                return module.handle_security(command)
            elif module_name == 'updater':
                # Self-update module handles update requests
                return module.process_update_request(command)
            else:
                return self._fallback_response(command)
                
        except Exception as e:
            logger.error(f"Error processing command: {str(e)}", exc_info=True)
            return f"I'm sorry, I encountered an error while processing your request. {str(e)}"
    
    def _determine_module(self, command: str) -> Optional[str]:
        """
        Determine which module should handle the command.
        
        Args:
            command: User command string
            
        Returns:
            Module name or None if no match
        """
        command = command.lower()
        
        # Check for direct module mentions
        direct_mentions = {
            'voice': ['voice', 'speak', 'listen', 'speech'],
            'ai_chat': ['chat', 'talk', 'conversation'],
            'system': ['system', 'computer', 'pc', 'file', 'folder'],
            'internet': ['internet', 'web', 'online', 'search'],
            'automation': ['automate', 'schedule', 'timer', 'alarm'],
            'security': ['security', 'password', 'privacy'],
            'updater': ['update', 'upgrade', 'install']
        }
        
        # Check for direct mentions first
        for module, keywords in direct_mentions.items():
            for keyword in keywords:
                if keyword in command:
                    return module
        
        # Check command patterns
        for module, patterns in self.command_patterns.items():
            for pattern in patterns:
                if re.search(pattern, command, re.IGNORECASE):
                    return module
        
        # Default to AI chat for general queries
        return 'ai_chat'
    
    def _fallback_response(self, command: str) -> str:
        """
        Generate a fallback response when no module can handle the command.
        
        Args:
            command: User command string
            
        Returns:
            Fallback response string
        """
        # Check if we have an AI chat module for fallback
        if 'ai_chat' in self.modules:
            return self.modules['ai_chat'].generate_response(
                f"I'm not sure how to process '{command}'. Can you please rephrase?"
            )
        
        return "I'm sorry, I don't understand that command. Can you please try again with different wording?"
    
    def add_command_pattern(self, module: str, pattern: str) -> bool:
        """
        Add a new command pattern for a module.
        
        Args:
            module: Module name
            pattern: Regex pattern string
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if module in self.command_patterns:
                self.command_patterns[module].append(pattern)
                logger.info(f"Added new command pattern for {module}: {pattern}")
                return True
            else:
                logger.warning(f"Cannot add pattern for unknown module: {module}")
                return False
        except Exception as e:
            logger.error(f"Error adding command pattern: {str(e)}")
            return False
    
    def get_module_capabilities(self) -> Dict[str, List[str]]:
        """
        Get a dictionary of modules and their capabilities.
        
        Returns:
            Dictionary of module names and their capabilities
        """
        capabilities = {}
        
        for module_name, patterns in self.command_patterns.items():
            if module_name in self.modules:
                # Extract capabilities from patterns
                capabilities[module_name] = [
                    p.replace('(', '').replace(')', '').replace('|', '/') 
                    for p in patterns
                ]
        
        return capabilities