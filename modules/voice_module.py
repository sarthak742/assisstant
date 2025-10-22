#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Voice Module for Jarvis AI Assistant (Improved)
Handles speech recognition (STT) and text-to-speech (TTS) functionality.
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
    logging.warning("Voice dependencies not available. Install with: pip install speech_recognition pyttsx3 pydub")

logger = logging.getLogger("Jarvis.VoiceModule")

class VoiceModule:
    """
    Voice Module class that handles speech recognition and text-to-speech functionality.
    """

    def __init__(self):
        self.recognizer = None
        self.engine = None
        self.listening = False
        self.wake_word = "hey jarvis"
        self.callback = None
        self.listen_thread = None
        self.audio_queue = queue.Queue()
        self.voice_settings = {'rate': 150, 'volume': 1.0, 'voice': None}
        if VOICE_DEPENDENCIES_AVAILABLE:
            self._initialize_speech_components()
        logger.info("Voice Module initialized")

    def _initialize_speech_components(self):
        try:
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 4000
            self.recognizer.dynamic_energy_threshold = True
            self.engine = pyttsx3.init()
            voices = self.engine.getProperty('voices')
            if voices:
                self.engine.setProperty('voice', voices[0].id)
                self.voice_settings['voice'] = voices[0].id
            self.engine.setProperty('rate', self.voice_settings['rate'])
            self.engine.setProperty('volume', self.voice_settings['volume'])
            logger.info("Speech components initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing speech components: {str(e)}")
            self.recognizer = None
            self.engine = None

    def start_listening(self, wake_word: str = None, callback: Callable = None):
        if not VOICE_DEPENDENCIES_AVAILABLE or self.recognizer is None or self.engine is None:
            logger.error("Cannot start listening: dependencies or speech engine unavailable")
            return False
        if wake_word:
            self.wake_word = wake_word.lower()
        self.callback = callback
        self.listening = True
        self.listen_thread = threading.Thread(target=self._listen_loop)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        logger.info(f"Started listening for wake word: '{self.wake_word}'")
        return True

    def stop_listening(self):
        self.listening = False
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=1.0)
        logger.info("Stopped listening")

    def _listen_loop(self):
        with sr.Microphone() as source:
            # Ambient noise calibration (happens only once, on start)
            logger.info("Adjusting for ambient noise...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            while self.listening:
                try:
                    logger.debug("Listening for audio (wake word)...")
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    try:
                        text = self.recognizer.recognize_google(audio).lower()
                        logger.debug(f"Wake-phase recognized: {text}")
                        if self.wake_word in text:
                            self._play_acknowledgment()
                            logger.info("Wake word detected, waiting for command...")
                            command_audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                            try:
                                command = self.recognizer.recognize_google(command_audio)
                                logger.info(f"Command recognized: {command}")
                                if self.callback:
                                    self.callback(command)
                            except sr.UnknownValueError:
                                logger.debug("Could not understand post-wake command.")
                                self.speak("Sorry, I did not catch that.")
                            except Exception as e:
                                logger.error(f"Error in recognizing command: {str(e)}")
                    except sr.UnknownValueError:
                        # Wasn't wake word, just background speech
                        pass
                    except Exception as e:
                        logger.error(f"Error in recognizing wake word: {str(e)}")
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error in listen loop: {str(e)}")
                    time.sleep(1)

    def _play_acknowledgment(self):
        try:
            # Placeholder for sound: print/log or add WAV/MP3 playback
            logger.info("Wake word acknowledged (sound would play here)")
        except Exception as e:
            logger.error(f"Error playing acknowledgment: {str(e)}")

    def speak(self, text: str) -> bool:
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
        if not VOICE_DEPENDENCIES_AVAILABLE or self.engine is None:
            logger.error("Cannot change voice: TTS engine not available")
            return False
        try:
            voices = self.engine.getProperty('voices')
            if voice_id:
                self.engine.setProperty('voice', voice_id)
                self.voice_settings['voice'] = voice_id
                logger.info(f"Changed voice to ID: {voice_id}")
                return True
            elif gender and voices:
                target_gender = gender.lower()
                for voice in voices:
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
        if not VOICE_DEPENDENCIES_AVAILABLE or self.engine is None:
            logger.error("Cannot adjust volume: TTS engine not available")
            return False
        try:
            volume = max(0.0, min(1.0, volume))
            self.engine.setProperty('volume', volume)
            self.voice_settings['volume'] = volume
            logger.info(f"Adjusted volume to {volume}")
            return True
        except Exception as e:
            logger.error(f"Error adjusting volume: {str(e)}")
            return False

    def process_command(self, command: str) -> str:
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
        return self.voice_settings.copy()
