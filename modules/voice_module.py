#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Voice Module for Jarvis AI Assistant (Integrated & Continuous)
Handles speech recognition (STT), text-to-speech (TTS), and real-time conversation looping.
"""

import os
import logging
import threading
import queue
import time
from typing import Callable, Optional, Dict, Any

try:
    import speech_recognition as sr
    import pyttsx3
    from pydub import AudioSegment
    from pydub.playback import play
    VOICE_DEPENDENCIES_AVAILABLE = True
except ImportError:
    VOICE_DEPENDENCIES_AVAILABLE = False
    logging.warning("Voice dependencies missing. Install: pip install speech_recognition pyttsx3 pydub")

logger = logging.getLogger("Jarvis.VoiceModule")

class VoiceModule:
    """Handles voice I/O for Jarvis (Speech Recognition + TTS + Continuous Learning Mode)."""

    def __init__(self, reasoning_engine: Optional[Any] = None):
        self.recognizer = None
        self.engine = None
        self.reasoning_engine = reasoning_engine  # Link to ReasoningEngine
        self.wake_word = "hey jarvis"
        self.callback = None
        self.listening = False
        self.listen_thread = None
        self.audio_queue = queue.Queue()
        self.voice_settings = {'rate': 150, 'volume': 1.0, 'voice': None}
        if VOICE_DEPENDENCIES_AVAILABLE:
            self._initialize_speech_components()
        logger.info("Voice Module initialized successfully")

    # ------------------- Initialization -------------------
    def _initialize_speech_components(self):
        try:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 4000
            self.recognizer.dynamic_energy_threshold = True

            self.engine = pyttsx3.init()
            voices = self.engine.getProperty("voices")
            if voices:
                self.engine.setProperty("voice", voices[0].id)
                self.voice_settings["voice"] = voices[0].id

            self.engine.setProperty("rate", self.voice_settings["rate"])
            self.engine.setProperty("volume", self.voice_settings["volume"])
        except Exception as e:
            logger.error(f"Speech init failed: {e}")
            self.recognizer = None
            self.engine = None

    # ------------------- Listening Cycle -------------------
    def start_listening(self, wake_word: str = None, callback: Callable = None):
        """Begins listening in a background thread and resumes automatically."""
        if not VOICE_DEPENDENCIES_AVAILABLE or not self.recognizer or not self.engine:
            logger.error("Dependencies unavailable for speech recognition.")
            return False

        if wake_word:
            self.wake_word = wake_word.lower()
        self.callback = callback
        self.listening = True

        self.listen_thread = threading.Thread(target=self._listen_loop)
        self.listen_thread.daemon = True
        self.listen_thread.start()

        self.speak("Jarvis voice interface is now active.")
        logger.info(f"Listening for wake word: '{self.wake_word}'")
        return True

    def stop_listening(self):
        self.listening = False
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=1.0)
        logger.info("Voice listening stopped.")

    def _listen_loop(self):
        """Continuously detects wake word, accepts commands, invokes callback or Reasoning Engine."""
        with sr.Microphone() as source:
            logger.info("Adjusting for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

            while self.listening:
                try:
                    logger.debug("Listening for wake word...")
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    text = ""

                    try:
                        text = self.recognizer.recognize_google(audio).lower()
                    except sr.UnknownValueError:
                        continue

                    if self.wake_word in text:
                        self._play_acknowledgment()
                        self.speak("Yes, I’m listening.")
                        logger.info("Wake word detected. Awaiting command...")

                        command_audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                        try:
                            command = self.recognizer.recognize_google(command_audio)
                            logger.info(f"Command recognized: {command}")

                            # Route to reasoning / callback
                            if self.callback:
                                self.callback(command)
                            elif self.reasoning_engine:
                                response = self.reasoning_engine.process(command)
                                self.speak(response)
                        except sr.UnknownValueError:
                            self.speak("Sorry, could you please repeat that?")
                        except Exception as e:
                            logger.error(f"Command processing error: {e}")

                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error in voice loop: {str(e)}")
                    time.sleep(1)

    # ------------------- Core Functionality -------------------
    def _play_acknowledgment(self):
        try:
            logger.info("Wake word detected (acknowledgment sound placeholder).")
        except Exception as e:
            logger.error(f"Acknowledgment error: {e}")

    def speak(self, text: str):
        """Convert Jarvis’s text response to speech."""
        if not VOICE_DEPENDENCIES_AVAILABLE or not self.engine:
            logger.warning("TTS engine unavailable. Falling back to text output.")
            print(f"Jarvis: {text}")
            return
        try:
            logger.info(f"Jarvis speaking: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"TTS Error: {e}")

    # ------------------- Customization -------------------
    def change_voice(self, voice_id=None, gender=None):
        if not VOICE_DEPENDENCIES_AVAILABLE or not self.engine:
            return False
        try:
            voices = self.engine.getProperty("voices")
            if voice_id:
                self.engine.setProperty("voice", voice_id)
                return True
            elif gender:
                gender = gender.lower()
                for v in voices:
                    v_gender = "female" if "female" in v.id.lower() else "male"
                    if v_gender == gender:
                        self.engine.setProperty("voice", v.id)
                        return True
                logger.warning(f"No {gender} voice found.")
                return False
        except Exception as e:
            logger.error(f"Error changing voice: {e}")
            return False

    def adjust_speech_rate(self, rate: int):
        try:
            self.engine.setProperty('rate', rate)
            self.voice_settings['rate'] = rate
            return True
        except Exception as e:
            logger.error(f"Speech rate error: {e}")
            return False

    def adjust_volume(self, volume: float):
        try:
            vol = max(0.0, min(1.0, volume))
            self.engine.setProperty("volume", vol)
            self.voice_settings["volume"] = vol
            return True
        except Exception as e:
            logger.error(f"Volume error: {e}")
            return False

    # ------------------- Status -------------------
    def get_voice_settings(self) -> Dict[str, Any]:
        return self.voice_settings.copy()
