#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Hybrid Task Manager for Jarvis 2.0
----------------------------------
Coordinates command execution across:
- SystemControlModule (desktop + web automation)
- Async web requests (aiohttp)
- Scheduling
- ReasoningEngine + MemoryManager + VoiceModule integration
"""

import os
import asyncio
import aiohttp
import subprocess
import threading
import datetime
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Callable, Optional
from modules.system_control import SystemControlModule

logger = logging.getLogger("Jarvis.HybridTaskManager")


class HybridTaskManager:
    """Unified orchestrator for system automation, web actions, and smart scheduling."""

    def __init__(self, memory_manager=None, voice_module=None, internet_module=None):
        self.memory = memory_manager
        self.voice = voice_module
        self.internet = internet_module
        self.system_controller = SystemControlModule()  # Integration point with new Jarvis automation
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self._start_async_loop, daemon=True).start()
        logger.info("Hybrid Task Manager initialized with SystemControl integration")

    # -------------------------------------------------
    # Async event loop management
    # -------------------------------------------------
    def _start_async_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def _run_async(self, coro):
        """Thread-safe coroutine executor."""
        return asyncio.run_coroutine_threadsafe(coro, self.loop)

    # -------------------------------------------------
    # System command handling (delegates to SystemControl)
    # -------------------------------------------------
    def execute_system_command(self, command: str) -> str:
        """Run any system command via SystemControl."""
        try:
            logger.info(f"Executing hybrid system command: {command}")
            result = self.system_controller.run_task(command)
            if self.memory:
                self.memory.store_interaction("jarvis", f"Executed system task: {command}")
            if self.voice:
                self.voice.speak(result)
            return result
        except Exception as e:
            logger.error(f"System command failed: {e}")
            if self.voice:
                self.voice.speak(f"I couldn’t execute the system command: {str(e)}")
            return f"System execution error: {e}"

    # -------------------------------------------------
    # Web async tasks
    # -------------------------------------------------
    async def fetch_data_async(self, url: str) -> str:
        """Asynchronously fetch web data via aiohttp."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    html = await response.text()
                    logger.info(f"Fetched content from {url}")
                    if self.memory:
                        self.memory.store_interaction("jarvis", f"Fetched data from {url}")
                    return html
        except Exception as e:
            logger.error(f"Async fetch failed for {url}: {e}")
            return f"Error fetching {url}: {e}"

    def fetch_data(self, url: str):
        """Initiate async fetch via thread-safe loop."""
        future = self._run_async(self.fetch_data_async(url))
        result = future.result()
        if self.voice:
            self.voice.speak("Content fetched successfully.")
        return result

    # -------------------------------------------------
    # Scheduler and Delayed Tasks
    # -------------------------------------------------
    def schedule_task(self, delay_seconds: int, func: Callable, *args, **kwargs):
        """Run callable after delay (non-blocking)."""
        def delayed():
            logger.info(f"Delayed task starting: {func.__name__} after {delay_seconds}s")
            result = func(*args, **kwargs)
            if self.memory:
                self.memory.store_interaction("jarvis", f"Completed scheduled task: {func.__name__}")
            if self.voice:
                self.voice.speak(f"Scheduled task {func.__name__} completed.")
            return result

        threading.Timer(delay_seconds, delayed).start()
        if self.voice:
            self.voice.speak(f"I will execute {func.__name__} in {delay_seconds} seconds.")
        logger.info(f"Task {func.__name__} scheduled at {datetime.datetime.now() + datetime.timedelta(seconds=delay_seconds)}")
        return True

    # -------------------------------------------------
    # Web API Action Layer
    # -------------------------------------------------
    def perform_web_action(self, url: str, action_type: str = "get", data: Dict[str, Any] = None):
        """Execute API requests asynchronously (GET/POST)."""

        async def api_call():
            async with aiohttp.ClientSession() as session:
                if action_type.lower() == "post":
                    async with session.post(url, json=data) as response:
                        return await response.text()
                async with session.get(url) as response:
                    return await response.text()

        logger.info(f"Performing {action_type.upper()} request for {url}")
        future = self._run_async(api_call())
        result = future.result()

        if self.voice:
            self.voice.speak("Web request completed successfully.")
        if self.memory:
            self.memory.store_interaction("jarvis", f"Web API {action_type.upper()} action for {url}")

        return result

    # -------------------------------------------------
    # Integration with Reasoning Engine
    # -------------------------------------------------
    def execute_from_reasoning(self, inferred_task: Dict[str, Any]) -> str:
        """
        Execute commands inferred by the ReasoningEngine.

        Example input:
        {'type': 'system', 'command': 'open calculator'}
        {'type': 'web', 'url': 'https://example.com'}
        {'type': 'schedule', 'delay': 60, 'action': 'fetch_data', 'url': 'https://news.com'}
        """
        try:
            task_type = inferred_task.get("type", "").lower()

            if task_type == "system":
                return self.execute_system_command(inferred_task.get("command", ""))

            elif task_type == "web":
                return self.fetch_data(inferred_task.get("url", ""))

            elif task_type == "schedule":
                delay = inferred_task.get("delay", 60)
                if inferred_task.get("action") == "fetch_data":
                    return self.schedule_task(delay, self.fetch_data, inferred_task.get("url", ""))

            elif task_type == "communication":
                return self.execute_system_command(inferred_task.get("task", ""))

            else:
                logger.warning(f"Unknown task type received: {task_type}")
                if self.voice:
                    self.voice.speak("I’m not sure how to handle that task.")
                return "Unknown or unsupported task type."
        except Exception as e:
            logger.error(f"Task execution error: {e}")
            return f"Execution failed: {e}"

        # -------------------------------------------------
    # Task recall utilities
    # -------------------------------------------------
    def get_task_history(self):
        """Retrieve previous interactions or task logs."""
        if self.memory:
            return self.memory.get_recent_interactions(10)
        return []

    def summarize_last_tasks(self):
        """Provide spoken or textual summary of recent tasks."""
        history = self.get_task_history()
        if history:
            summary = "Recent tasks: " + ", ".join([i["message"] for i in history])
        else:
            summary = "No tasks logged yet."

        if self.voice:
            self.voice.speak(summary)
        return summary

 history else "No tasks logged yet."
