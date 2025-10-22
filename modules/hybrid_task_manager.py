#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Hybrid Task Manager for Jarvis AI Assistant
-------------------------------------------
Executes system tasks, asynchronous web actions, and scheduled routines.
Integrates with:
- ReasoningEngine (command parsing)
- MemoryManager (task logging and recall)
- VoiceModule (speech feedback)
- InternetAPIModule (API calls & web fetch)
"""

import os
import asyncio
import aiohttp
import subprocess
import threading
import datetime
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Callable

logger = logging.getLogger("Jarvis.HybridTaskManager")

class HybridTaskManager:
    """Unified executor for system, web, and scheduling tasks."""

    def __init__(self, memory_manager=None, voice_module=None, internet_module=None):
        self.memory = memory_manager
        self.voice = voice_module
        self.internet = internet_module
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self._start_async_loop, daemon=True).start()
        logger.info("Hybrid Task Manager initialized")

    # ------------------- Event Loop -------------------
    def _start_async_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def _run_async(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self.loop)

    # ------------------- System Level Tasks -------------------
    def execute_system_command(self, command: str) -> str:
        """Run local system commands or open applications."""
        try:
            logger.info(f"Executing system command: {command}")
            if "open" in command.lower():
                app = command.split("open")[-1].strip()
                if os.name == "nt":  # Windows
                    os.system(f"start {app}")
                elif os.name == "posix":
                    subprocess.Popen(["open" if "darwin" in os.sys.platform else "xdg-open", app])
                result = f"Opened {app} successfully."
            else:
                output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
                result = output.strip()

            if self.memory:
                self.memory.store_interaction("jarvis", f"Executed system task: {command}")
            if self.voice:
                self.voice.speak(result)
            return result
        except Exception as e:
            logger.error(f"System command failed: {e}")
            if self.voice:
                self.voice.speak(f"I couldn’t execute the system command: {str(e)}")
            return str(e)

    # ------------------- Async Web Tasks -------------------
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
        return future.result()

    # ------------------- Scheduling and Delays -------------------
    def schedule_task(self, delay_seconds: int, func: Callable, *args, **kwargs):
        """Run a callable after a delay."""
        def delayed():
            logger.info(f"Delayed task started: {func.__name__} after {delay_seconds}s")
            result = func(*args, **kwargs)
            if self.memory:
                self.memory.store_interaction("jarvis", f"Scheduled task completed: {func.__name__}")
            if self.voice:
                self.voice.speak(f"Task {func.__name__} completed.")
            return result

        threading.Timer(delay_seconds, delayed).start()
        if self.voice:
            self.voice.speak(f"I will execute {func.__name__} in {delay_seconds} seconds.")
        logger.info(f"Task {func.__name__} scheduled.")
        return True

    # ------------------- Web API Tasks -------------------
    def perform_web_action(self, url: str, action_type: str = "get", data: Dict[str, Any] = None):
        """Perform a web action: GET or POST."""
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
            self.memory.store_interaction("jarvis", f"Web action: {action_type} {url}")
        return result

    # ------------------- Integration with Reasoning Engine -------------------
    def execute_from_reasoning(self, inferred_task: Dict[str, Any]) -> str:
        """
        Execute based on Reasoning Engine’s inference output.
        Example input:
        {'type': 'system', 'command': 'open calculator'}
        {'type': 'web', 'url': 'https://example.com'}
        {'type': 'schedule', 'delay': 60, 'action': 'fetch_data', 'url': 'https://news.com'}
        """
        try:
            task_type = inferred_task.get("type", "")
            if task_type == "system":
                return self.execute_system_command(inferred_task.get("command", ""))
            elif task_type == "web":
                return self.fetch_data(inferred_task.get("url", ""))
            elif task_type == "schedule":
                delay = inferred_task.get("delay", 60)
                if inferred_task.get("action") == "fetch_data":
                    return self.schedule_task(delay, self.fetch_data, inferred_task.get("url"))
            else:
                if self.voice:
                    self.voice.speak("I’m not sure how to handle that task.")
                return "Unknown task type."
        except Exception as e:
            logger.error(f"Task execution error: {e}")
            return f"Execution failed: {e}"

    # ------------------- Task Recall -------------------
    def get_task_history(self):
        """Fetch past task logs."""
        if self.memory:
            return self.memory.get_recent_interactions(10)
        return []

    def summarize_last_tasks(self):
        """Quick summary for voice output."""
        history = self.get_task_history()
        return "Recent tasks: " + ", ".join([i["message"] for i in history]) if history else "No tasks logged yet."
