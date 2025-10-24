#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Voice Module for Jarvis AI Assistant (Final v2.1)
-------------------------------------------------
Features:
- Continuous listening with wake-word trigger (“Hey Jarvis”)
- Thread-safe, COM-safe TTS with retry logic
- Adaptive ambient noise adjustment for dynamic environments
- Optional callback + ReasoningEngine integration
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
    logging.warning("Missing dependencies. Run: pip install speech_recognition pyttsx3 pydub pywin32")

logger = logging.getLogger("Jarvis.VoiceModule")


class VoiceModule:
    """Handles Speech Recognition (STT), Text-to-Speech (TTS), and continuous wake-word listening."""

    def __init__(self, reasoning_engine: Optional[Any] = None):
        self.reasoning_engine = reasoning_engine
        self.recognizer = None
        self.engine = None
        self.engine_lock = threading.Lock()
        self.listening = False
        self.wake_word = "hey jarvis"
        self.callback = None
        self.listen_thread = None
        self.voice_settings = {'rate': 160, 'volume': 1.0, 'voice': None}
        if VOICE_DEPENDENCIES_AVAILABLE:
            self._initialize_voice_components()
        logger.info("Voice Module initialized and ready.")

    # ---------------------------------------------------------
    # Initialization
    # ---------------------------------------------------------
    def _initialize_voice_components(self):
        try:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 3000
            self.recognizer.dynamic_energy_threshold = True
            self.engine = pyttsx3.init()

            # Voice setup
            voices = self.engine.getProperty("voices")
            if voices:
                self.engine.setProperty("voice", voices[0].id)
                self.voice_settings["voice"] = voices[0].id

            self.engine.setProperty("rate", self.voice_settings["rate"])
            self.engine.setProperty("volume", self.voice_settings["volume"])
        except Exception as e:
            logger.error(f"Voice init failed: {e}")
            self.engine = None
            self.recognizer = None

    # ---------------------------------------------------------
    # Adaptive Ambient Noise Calibration
    # ---------------------------------------------------------
    def calibrate_noise(self, duration: float = 1.5):
        """Adjusts recognition threshold dynamically."""
        if not self.recognizer:
            return
        try:
            with sr.Microphone() as source:
                logger.info("Calibrating ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
                logger.info(f"Adjusted threshold: {self.recognizer.energy_threshold}")
        except Exception as e:
            logger.warning(f"Noise calibration failed: {e}")

    # ---------------------------------------------------------
    # Listening Loop
    # ---------------------------------------------------------
    def start_listening(self, wake_word: str = None, callback: Callable = None):
        """Begin voice recognition loop."""
        if not VOICE_DEPENDENCIES_AVAILABLE or not self.recognizer or not self.engine:
            logger.error("Voice dependencies unavailable.")
            return False

        if wake_word:
            self.wake_word = wake_word.lower()
        self.callback = callback
        self.listening = True

        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()

        self.speak("Voice interface active.")
        logger.info(f"Listening for wake word: '{self.wake_word}'")
        return True

    def stop_listening(self):
        """Stops active listening loop."""
        self.listening = False
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=1)
        logger.info("Voice loop stopped.")

    def _listen_loop(self):
        """Broad continuous loop for wake word detection."""
        try:
            with sr.Microphone() as source:
                self.calibrate_noise(duration=1.0)
                while self.listening:
                    try:
                        logger.debug("Listening for wake word…")
                        audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=4)
                        text = ""
                        try:
                            text = self.recognizer.recognize_google(audio).lower()
                        except sr.UnknownValueError:
                            continue

                        if self.wake_word in text:
                            self._play_ack_sound()
                            self.speak("Yes, I'm listening.")
                            logger.info("Wake word detected — awaiting next command.")
                            self._capture_command(source)
                    except Exception as e:
                        logger.error(f"Loop error: {e}")
                        time.sleep(0.5)
        except Exception as e:
            logger.error(f"Voice listen loop failed: {e}")

    def _capture_command(self, source):
        """Capture and process user’s command speech."""
        try:
            command_audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            command = self.recognizer.recognize_google(command_audio)
            logger.info(f"Command recognized: {command}")

            if self.callback:
                self.callback(command)
            elif self.reasoning_engine:
                response = self.reasoning_engine.process(command)
                self.speak(response)
        except sr.UnknownValueError:
            self.speak("Sorry, could you repeat that?")
        except Exception as e:
            logger.error(f"Command processing failed: {e}")

    # ---------------------------------------------------------
    # Wake-Word Continuous Mode
    # ---------------------------------------------------------
    def start_wake_word_listener(self):
        """Non-blocking continuous 'Hey Jarvis' detector."""
        if not VOICE_DEPENDENCIES_AVAILABLE or not self.recognizer:
            logger.error("Wake listener not available.")
            return False

        threading.Thread(target=self._listen_loop, daemon=True).start()
        self.speak("Wake word mode activated.")
        return True

    # ---------------------------------------------------------
    # Playback Helper
    # ---------------------------------------------------------
    def _play_ack_sound(self):
        try:
            logger.info("Wake word acknowledged.")
        except Exception as e:
            logger.warning(f"Ack sound error: {e}")

    # ---------------------------------------------------------
    # TTS (Thread-Safe)
    # ---------------------------------------------------------
    def speak(self, text: str):
        """Safe pyttsx3 speech that never blocks main loop."""
        if not VOICE_DEPENDENCIES_AVAILABLE or not self.engine:
            print(f"Jarvis: {text}")
            return

        def _speak_thread():
            with self.engine_lock:
                try:
                    self.engine.stop()
                    self.engine.say(text)
                    self.engine.runAndWait()
                except RuntimeError:
                    logger.warning("TTS busy, retrying in backup thread.")
                    threading.Thread(target=self._retry_speak, args=(text,), daemon=True).start()
                except Exception as e:
                    logger.error(f"TTS failure: {e}")
                    print(f"Jarvis: {text}")

        threading.Thread(target=_speak_thread, daemon=True).start()

    def _retry_speak(self, text: str):
        """Backup retry if the engine throws a run-time error."""
        try:
            time.sleep(0.3)
            with self.engine_lock:
                self.engine.stop()
                self.engine.say(text)
                self.engine.runAndWait()
        except Exception as e:
            logger.error(f"Retry TTS failed: {e}")
            print(f"Jarvis (retry): {text}")

    # ---------------------------------------------------------
    # Customization Methods
    # ---------------------------------------------------------
    def change_voice(self, gender: Optional[str] = None):
        """Change to a male or female voice if available."""
        if not self.engine:
            return False
        try:
            voices = self.engine.getProperty("voices")
            target = None
            for v in voices:
                if gender and gender.lower() in v.name.lower():
                    target = v.id
                    break
            if target:
                self.engine.setProperty("voice", target)
                self.voice_settings["voice"] = target
                return True
            logger.warning("Requested voice not found.")
            return False
        except Exception as e:
            logger.error(f"Voice change error: {e}")
            return False

    def adjust_speech_rate(self, rate: int):
        try:
            self.engine.setProperty("rate", rate)
            self.voice_settings["rate"] = rate
            return True
        except Exception as e:
            logger.error(f"Rate adjustment error: {e}")
            return False

    def adjust_volume(self, volume: float):
        try:
            vol = max(0.0, min(1.0, volume))
            self.engine.setProperty("volume", vol)
            self.voice_settings["volume"] = vol
            return True
        except Exception as e:
            logger.error(f"Volume adjustment error: {e}")
            return False

    def get_voice_settings(self) -> Dict[str, Any]:
        return self.voice_settings.copy()


