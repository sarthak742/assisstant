#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Voice Module for Jarvis AI Assistant (Final v2.2 Stable)
--------------------------------------------------------
Features:
- Continuous listening with wake-word trigger (“Hey Jarvis”)
- Push-to-talk (mic button) for instant command capture (no wake word)
- Thread-safe, COM-safe TTS with retry logic
- Adaptive ambient noise calibration for changing environments
- Optional callback + Reasoning Engine integration
"""

import os
import logging
import threading
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
    """Handles Speech Recognition (STT), TTS, continuous wake-word listening, and push-to-talk."""

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
        logger.info("Voice Module initialized successfully.")

    # ---------------------------------------------------------
    # Initialization
    # ---------------------------------------------------------
    def _initialize_voice_components(self):
        try:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 3000
            self.recognizer.dynamic_energy_threshold = True
            self.engine = pyttsx3.init()

            voices = self.engine.getProperty("voices")
            if voices:
                self.engine.setProperty("voice", voices[0].id)
                self.voice_settings["voice"] = voices[0].id

            self.engine.setProperty("rate", self.voice_settings["rate"])
            self.engine.setProperty("volume", self.voice_settings["volume"])
        except Exception as e:
            logger.error(f"Speech engine initialization failed: {e}")
            self.recognizer = None
            self.engine = None

    # ---------------------------------------------------------
    # Adaptive Noise Calibration
    # ---------------------------------------------------------
    def calibrate_noise(self, duration: float = 1.5):
        if not self.recognizer:
            return
        try:
            with sr.Microphone() as source:
                logger.info("Calibrating ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=duration)
                logger.info(f"Energy threshold calibrated to: {self.recognizer.energy_threshold}")
        except Exception as e:
            logger.warning(f"Noise calibration failed: {e}")

    # ---------------------------------------------------------
    # Push-to-Talk (Mic Button) – Instant Command Mode
    # ---------------------------------------------------------
   def capture_single_command(self, callback: Callable = None):
    print("DEBUG: Entered capture_single_command")
    print("DEBUG: VOICE_DEPENDENCIES_AVAILABLE =", VOICE_DEPENDENCIES_AVAILABLE)
    print("DEBUG: recognizer =", self.recognizer)
    if not VOICE_DEPENDENCIES_AVAILABLE or not self.recognizer:
        print("DEBUG: Exiting - dependencies missing or recognizer not present")
        logger.error("Voice dependencies unavailable.")
        return False
    """Capture and process a single command (no wake word required)."""
    try:
        with sr.Microphone() as source:
            self.calibrate_noise(duration=1.0)
            self.speak("Listening for your command.")
            logger.info("Listening for single voice command (mic button).")
            audio = self.recognizer.listen(source, timeout=7, phrase_time_limit=10)
            try:
                command = self.recognizer.recognize_google(audio)
                logger.info(f"Single command recognized: {command}")
                if callback:
                    callback(command)
                elif self.reasoning_engine:
                    response = self.reasoning_engine.process(command)
                    self.speak(response)
                return command
            except sr.UnknownValueError:
                self.speak("Sorry, could you repeat that?")
                return None
    except Exception as e:
        logger.error(f"Single command listening failed: {e}")
        self.speak("Sorry, I couldn't hear you.")
        return None

 
    # The rest of your function remains unchanged.

    # ---------------------------------------------------------
    # Wake Word + Command (Continuous Listening)
    # ---------------------------------------------------------
    def start_listening(self, wake_word: str = None, callback: Callable = None):
        """Starts background listening loop (wake word mode)."""
        if not VOICE_DEPENDENCIES_AVAILABLE or not self.recognizer or not self.engine:
            logger.error("Voice dependencies unavailable.")
            return False

        if wake_word:
            self.wake_word = wake_word.lower()

        self.callback = callback
        self.listening = True
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()

        self.speak("Jarvis voice interface active.")
        logger.info(f"Listening for wake word: '{self.wake_word}'")
        return True

    def stop_listening(self):
        """Stops active listening thread."""
        self.listening = False
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=1)
        logger.info("Voice listening stopped.")

    def _listen_loop(self):
        """Continuously listens for wake word and handles commands."""
        try:
            with sr.Microphone() as source:
                self.calibrate_noise(duration=1.0)
                while self.listening:
                    try:
                        logger.debug("Listening for wake word...")
                        audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=4)
                        text = ""
                        try:
                            text = self.recognizer.recognize_google(audio).lower()
                        except sr.UnknownValueError:
                            continue

                        if self.wake_word in text:
                            self._play_ack_sound()
                            self.speak("Yes, I'm listening.")
                            logger.info("Wake word detected — awaiting user command.")
                            self._capture_command(source)
                    except Exception as e:
                        logger.error(f"Listening loop error: {e}")
                        time.sleep(0.5)
        except Exception as e:
            logger.error(f"Failed to start microphone loop: {e}")

    def _capture_command(self, source):
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

    def start_wake_word_listener(self):
        if not VOICE_DEPENDENCIES_AVAILABLE or not self.recognizer:
            logger.error("Wake word mode unavailable.")
            return False

        threading.Thread(target=self._listen_loop, daemon=True).start()
        self.speak("Wake word mode activated.")
        return True

    def _play_ack_sound(self):
        try:
            logger.info("Wake word acknowledgment detected.")
        except Exception as e:
            logger.warning(f"Acknowledgment error: {e}")

    # ---------------------------------------------------------
    # Text-to-Speech (Thread-Safe)
    # ---------------------------------------------------------
    def speak(self, text: str):
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
                    logger.warning("TTS busy; retrying...")
                    threading.Thread(target=self._retry_speak, args=(text,), daemon=True).start()
                except Exception as e:
                    logger.error(f"TTS error: {e}")
                    print(f"Jarvis: {text}")

        threading.Thread(target=_speak_thread, daemon=True).start()

    def _retry_speak(self, text: str):
        try:
            time.sleep(0.3)
            with self.engine_lock:
                self.engine.stop()
                self.engine.say(text)
                self.engine.runAndWait()
        except Exception as e:
            logger.error(f"TTS retry failed: {e}")
            print(f"Jarvis (retry): {text}")

    def change_voice(self, gender: Optional[str] = None):
        if not self.engine:
            return False
        try:
            voices = self.engine.getProperty("voices")
            for v in voices:
                if gender and gender.lower() in v.name.lower():
                    self.engine.setProperty("voice", v.id)
                    self.voice_settings["voice"] = v.id
                    return True
            logger.warning("Requested voice not found.")
            return False
        except Exception as e:
            logger.error(f"Voice change failed: {e}")
            return False

    def adjust_speech_rate(self, rate: int):
        try:
            self.engine.setProperty("rate", rate)
            self.voice_settings["rate"] = rate
            return True
        except Exception as e:
            logger.error(f"Rate adjustment failed: {e}")
            return False

    def adjust_volume(self, volume: float):
        try:
            vol = max(0.0, min(1.0, volume))
            self.engine.setProperty("volume", vol)
            self.voice_settings["volume"] = vol
            return True
        except Exception as e:
            logger.error(f"Volume adjustment failed: {e}")
            return False

    def get_voice_settings(self) -> Dict[str, Any]:
        return self.voice_settings.copy()
