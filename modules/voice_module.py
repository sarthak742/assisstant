#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Voice Module for Jarvis AI Assistant
Handles speech recognition (STT) and text-to-speech (TTS) functionality.
"""

import os
import logging
import threading
import queue
import time
from typing import Callable, Optional, Dict, Any

# Third-party imports for speech recognition and synthesis
# Note: These libraries need to be installed via pip
try:
    import speech_recognition as sr
    import pyttsx3
    from pydub import AudioSegment
    from pydub.playback import play
    VOICE_DEPENDENCIES_AVAILABLE = True
except ImportError:
    VOICE_DEPENDENCIES_AVAILABLE = False
    logging.warning("Voice dependencies not available. Install with: pip install speech_recognition pyttsx3 pydub")

logger = logging.getLogger("Jarvis.VoiceModule")

class VoiceModule:
    """
    Voice Module class that handles speech recognition and text-to-speech functionality.
    """
    
    def __init__(self):
        """Initialize the Voice Module."""
        self.recognizer = None
        self.engine = None
        self.listening = False
        self.wake_word = "hey jarvis"
        self.callback = None
        self.listen_thread = None
        self.audio_queue = queue.Queue()
        self.voice_settings = {
            'rate': 150,  # Speed of speech
            'volume': 1.0,  # Volume (0.0 to 1.0)
            'voice': None  # Default voice
        }
        
        # Initialize speech recognition and TTS if dependencies are available
        if VOICE_DEPENDENCIES_AVAILABLE:
            self._initialize_speech_components()
        
        logger.info("Voice Module initialized")
    
    def _initialize_speech_components(self):
        """Initialize speech recognition and TTS components."""
        try:
            # Initialize speech recognizer
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 4000
            self.recognizer.dynamic_energy_threshold = True
            
            # Initialize text-to-speech engine
            self.engine = pyttsx3.init()
            
            # Get available voices
            voices = self.engine.getProperty('voices')
            if voices:
                # Set a default voice (usually index 0 is male, 1 is female)
                self.engine.setProperty('voice', voices[0].id)
                self.voice_settings['voice'] = voices[0].id
            
            # Set initial speech rate and volume
            self.engine.setProperty('rate', self.voice_settings['rate'])
            self.engine.setProperty('volume', self.voice_settings['volume'])
            
            logger.info("Speech components initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing speech components: {str(e)}")
            self.recognizer = None
            self.engine = None
    
    def start_listening(self, wake_word: str = None, callback: Callable = None):
        """
        Start listening for voice commands.
        
        Args:
            wake_word: Wake word to activate the assistant (e.g., "Hey Jarvis")
            callback: Function to call when a command is recognized
        """
        if not VOICE_DEPENDENCIES_AVAILABLE:
            logger.error("Cannot start listening: Voice dependencies not available")
            return False
        
        if self.recognizer is None or self.engine is None:
            logger.error("Cannot start listening: Speech components not initialized")
            return False
        
        if wake_word:
            self.wake_word = wake_word.lower()
        
        self.callback = callback
        self.listening = True
        
        # Start listening in a separate thread
        self.listen_thread = threading.Thread(target=self._listen_loop)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        
        logger.info(f"Started listening for wake word: '{self.wake_word}'")
        return True
    
    def stop_listening(self):
        """Stop listening for voice commands."""
        self.listening = False
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=1.0)
        logger.info("Stopped listening")
    
    def _listen_loop(self):
        """Background thread for continuous listening."""
        with sr.Microphone() as source:
            # Adjust for ambient noise
            logger.info("Adjusting for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            while self.listening:
                try:
                    logger.debug("Listening for audio...")
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    self.audio_queue.put(audio)
                    
                    # Process audio in a separate thread to keep listening
                    process_thread = threading.Thread(
                        target=self._process_audio,
                        args=(audio,)
                    )
                    process_thread.daemon = True
                    process_thread.start()
                    
                except sr.WaitTimeoutError:
                    # Timeout, continue listening
                    continue
                except Exception as e:
                    logger.error(f"Error in listen loop: {str(e)}")
                    time.sleep(1)  # Prevent tight loop on error
    
    def _process_audio(self, audio):
        """
        Process audio data to recognize commands.
        
        Args:
            audio: Audio data from the recognizer
        """
        try:
            # Convert speech to text
            text = self.recognizer.recognize_google(audio).lower()
            logger.debug(f"Recognized: {text}")
            
            # Check for wake word
            if self.wake_word in text:
                # Play acknowledgment sound
                self._play_acknowledgment()
                
                # Wait for the command after wake word
                with sr.Microphone() as source:
                    logger.info("Wake word detected! Listening for command...")
                    command_audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    command = self.recognizer.recognize_google(command_audio)
                    logger.info(f"Command recognized: {command}")
                    
                    # Call the callback function with the command
                    if self.callback:
                        self.callback(command)
            
        except sr.UnknownValueError:
            # Speech was unintelligible
            logger.debug("Could not understand audio")
        except sr.RequestError as e:
            # Could not request results from Google Speech Recognition service
            logger.error(f"Recognition service error: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing audio: {str(e)}")
    
    def _play_acknowledgment(self):
        """Play a short sound to acknowledge wake word detection."""
        try:
            # This is a placeholder. In a real implementation, you would play a sound file
            logger.info("Wake word acknowledged")
        except Exception as e:
            logger.error(f"Error playing acknowledgment: {str(e)}")
    
    def speak(self, text: str) -> bool:
        """
        Convert text to speech.
        
        Args:
            text: Text to convert to speech
            
        Returns:
            True if successful, False otherwise
        """
        if not VOICE_DEPENDENCIES_AVAILABLE or self.engine is None:
            logger.error("Cannot speak: TTS engine not available")
            return False
        
        try:
            logger.info(f"Speaking: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
            return True
        except Exception as e:
            logger.error(f"Error in text-to-speech: {str(e)}")
            return False
    
    def change_voice(self, voice_id: str = None, gender: str = None) -> bool:
        """
        Change the voice used for text-to-speech.
        
        Args:
            voice_id: ID of the voice to use
            gender: Gender of the voice ('male' or 'female')
            
        Returns:
            True if successful, False otherwise
        """
        if not VOICE_DEPENDENCIES_AVAILABLE or self.engine is None:
            logger.error("Cannot change voice: TTS engine not available")
            return False
        
        try:
            voices = self.engine.getProperty('voices')
            
            if voice_id:
                # Set specific voice by ID
                self.engine.setProperty('voice', voice_id)
                self.voice_settings['voice'] = voice_id
                logger.info(f"Changed voice to ID: {voice_id}")
                return True
            
            elif gender and voices:
                # Find voice by gender
                target_gender = gender.lower()
                for voice in voices:
                    # This is a heuristic approach - voice IDs often contain gender indicators
                    voice_gender = 'female' if 'female' in voice.id.lower() else 'male'
                    
                    if voice_gender == target_gender:
                        self.engine.setProperty('voice', voice.id)
                        self.voice_settings['voice'] = voice.id
                        logger.info(f"Changed voice to {target_gender}: {voice.id}")
                        return True
                
                logger.warning(f"No {target_gender} voice found")
                return False
            
            else:
                logger.warning("No voice ID or gender specified")
                return False
                
        except Exception as e:
            logger.error(f"Error changing voice: {str(e)}")
            return False
    
    def adjust_speech_rate(self, rate: int) -> bool:
        """
        Adjust the speech rate.
        
        Args:
            rate: Speech rate (words per minute, typically 100-200)
            
        Returns:
            True if successful, False otherwise
        """
        if not VOICE_DEPENDENCIES_AVAILABLE or self.engine is None:
            logger.error("Cannot adjust speech rate: TTS engine not available")
            return False
        
        try:
            self.engine.setProperty('rate', rate)
            self.voice_settings['rate'] = rate
            logger.info(f"Adjusted speech rate to {rate}")
            return True
        except Exception as e:
            logger.error(f"Error adjusting speech rate: {str(e)}")
            return False
    
    def adjust_volume(self, volume: float) -> bool:
        """
        Adjust the speech volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
            
        Returns:
            True if successful, False otherwise
        """
        if not VOICE_DEPENDENCIES_AVAILABLE or self.engine is None:
            logger.error("Cannot adjust volume: TTS engine not available")
            return False
        
        try:
            # Ensure volume is within valid range
            volume = max(0.0, min(1.0, volume))
            
            self.engine.setProperty('volume', volume)
            self.voice_settings['volume'] = volume
            logger.info(f"Adjusted volume to {volume}")
            return True
        except Exception as e:
            logger.error(f"Error adjusting volume: {str(e)}")
            return False
    
    def process_command(self, command: str) -> str:
        """
        Process voice-related commands.
        
        Args:
            command: Voice command string
            
        Returns:
            Response string
        """
        command = command.lower()
        
        if 'speak louder' in command:
            new_volume = min(1.0, self.voice_settings['volume'] + 0.1)
            if self.adjust_volume(new_volume):
                return "I've increased my speaking volume."
            
        elif 'speak softer' in command:
            new_volume = max(0.0, self.voice_settings['volume'] - 0.1)
            if self.adjust_volume(new_volume):
                return "I've decreased my speaking volume."
            
        elif 'speak faster' in command:
            new_rate = self.voice_settings['rate'] + 25
            if self.adjust_speech_rate(new_rate):
                return "I'm now speaking faster."
            
        elif 'speak slower' in command:
            new_rate = max(50, self.voice_settings['rate'] - 25)
            if self.adjust_speech_rate(new_rate):
                return "I'm now speaking slower."
            
        elif 'female voice' in command:
            if self.change_voice(gender='female'):
                return "I've switched to a female voice."
            
        elif 'male voice' in command:
            if self.change_voice(gender='male'):
                return "I've switched to a male voice."
            
        elif 'stop listening' in command:
            self.stop_listening()
            return "I've stopped listening for commands."
            
        elif 'start listening' in command:
            if self.start_listening(wake_word=self.wake_word, callback=self.callback):
                return "I'm now listening for commands."
            
        return "I'm not sure how to process that voice command."
    
    def get_voice_settings(self) -> Dict[str, Any]:
        """
        Get current voice settings.
        
        Returns:
            Dictionary of current voice settings
        """
        return self.voice_settings.copy()