#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Jarvis - Personal AI Assistant
Main entry point for the Jarvis AI assistant application.
"""

import os
import sys
import logging
from datetime import datetime

# Import core modules
from modules.memory_manager import MemoryManager
from modules.reasoning_engine import ReasoningEngine
from modules.voice_module import VoiceModule
from modules.ai_chat_module import AIChatModule
from modules.system_control import SystemControlModule
from modules.internet_api import InternetAPIModule
from modules.automation import AutomationModule
from modules.security import SecurityModule
from modules.self_update import SelfUpdateManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs', 'jarvis.log')),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("Jarvis")

class Jarvis:
    """Main Jarvis assistant class that coordinates all modules."""
    
    def __init__(self):
        """Initialize Jarvis and all its modules."""
        logger.info("Initializing Jarvis...")
        
        # Create logs directory if it doesn't exist
        os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs'), exist_ok=True)
        
        # Initialize all modules
        self.memory = MemoryManager()
        self.voice = VoiceModule()
        self.reasoning = ReasoningEngine(self.memory)
        self.ai_chat = AIChatModule(self.memory)
        self.system = SystemControlModule()
        self.internet = InternetAPIModule()
        self.automation = AutomationModule()
        self.security = SecurityModule()
        self.updater = SelfUpdateManager()
        
        # Connect modules to the reasoning engine
        self.reasoning.register_modules({
            'voice': self.voice,
            'ai_chat': self.ai_chat,
            'system': self.system,
            'internet': self.internet,
            'automation': self.automation,
            'security': self.security,
            'updater': self.updater
        })
        
        logger.info("Jarvis initialization complete.")
    
    def start(self):
        """Start Jarvis assistant."""
        logger.info("Starting Jarvis...")
        
        # Authenticate user
        if not self.security.authenticate():
            logger.error("Authentication failed. Exiting.")
            return
        
        # Start voice recognition with wake word
        self.voice.start_listening(wake_word="Hey Jarvis", callback=self.process_command)
        
        logger.info("Jarvis is now listening...")
    
    def process_command(self, command):
        """Process user command through the reasoning engine."""
        if not command:
            return
        
        logger.info(f"Processing command: {command}")
        
        # Store command in memory
        self.memory.store_interaction("user", command)
        
        # Process through reasoning engine
        response = self.reasoning.process(command)
        
        # Store response in memory
        self.memory.store_interaction("jarvis", response)
        
        # Convert response to speech
        self.voice.speak(response)
        
        return response
    
    def stop(self):
        """Stop Jarvis assistant."""
        logger.info("Stopping Jarvis...")
        self.voice.stop_listening()
        # Perform any cleanup needed
        logger.info("Jarvis stopped.")

if __name__ == "__main__":
    # Create Jarvis instance
    jarvis = Jarvis()
    
    try:
        # Start Jarvis
        jarvis.start()
        
        # Keep running until interrupted
        while True:
            pass
    except KeyboardInterrupt:
        # Handle graceful shutdown
        jarvis.stop()
        logger.info("Jarvis shutdown complete.")
    except Exception as e:
        logger.error(f"Error in Jarvis: {str(e)}", exc_info=True)
        jarvis.stop()