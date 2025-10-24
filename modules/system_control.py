#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
System Control Module for Jarvis AI Assistant (Enhanced Automation Edition)
Enables hybrid desktop + web automation: app launching, WhatsApp messaging, email drafting,
file operations, and safe system control (Windows optimized).
"""

import os
import logging
import subprocess
import shutil
import re
import psutil
import ctypes
import webbrowser
from typing import Dict, Any

logger = logging.getLogger("Jarvis.SystemControlModule")

try:
    import pywhatkit
except ImportError:
    pywhatkit = None
    logger.warning("Optional library 'pywhatkit' not found. WhatsApp features disabled.")

# ==========================================================
# Core Class Definition
# ==========================================================

class SystemControlModule:
    """Manages app launching, web control, file ops, and OS commands."""

    def __init__(self):
        self.common_apps = {
            'browser': ['chrome.exe', 'firefox.exe', 'msedge.exe'],
            'editor': ['notepad.exe', 'code.exe', 'wordpad.exe'],
            'media': ['wmplayer.exe', 'vlc.exe', 'spotify.exe'],
            'office': ['winword.exe', 'excel.exe', 'powerpnt.exe'],
            'terminal': ['cmd.exe', 'powershell.exe', 'windowsterminal.exe']
        }

        self.web_apps = {
            'whatsapp': 'https://web.whatsapp.com',
            'gmail': 'https://mail.google.com',
            'youtube': 'https://www.youtube.com',
            'drive': 'https://drive.google.com',
            'maps': 'https://www.google.com/maps',
            'chatgpt': 'https://chat.openai.com',
        }

        self.safe_mode = not os.getenv("JARVIS_ALLOW_SYSTEM_POWER", "false").lower() == "true"
        logger.info("System Control Module (Jarvis 2.0 upgrade) initialized.")

    # ==========================================================
    # Public Entry Point
    # ==========================================================

    def run_task(self, task: str) -> str:
        """Interpret & execute natural‑language task instructions."""
        try:
            result = self.execute_command(task)
            return result
        except Exception as e:
            logger.error(f"Task Execution Error: {str(e)}")
            return f"Something went wrong while executing: {str(e)}"

    # ==========================================================
    # Command Interpreter
    # ==========================================================

    def execute_command(self, command: str) -> str:
        """Unified dispatcher for all OS tasks."""
        cmd = command.lower().strip()

        patterns = [
            (r'open file\s+(.+)', self._open_file),
            (r'open (folder|directory)\s+(.+)', self._open_folder),
            (r'move (file|folder)\s+(.+)\s+to\s+(.+)', self._move_file_or_folder),
            (r'delete (file|folder)\s+(.+)', self._delete_file_or_folder),
            (r'create (folder|directory)\s+(.+)', self._create_folder),
            (r'(open|launch|start|run)\s+([a-zA-Z0-9_ -]+)', self._open_application),
            (r'(close|exit|quit)\s+([a-zA-Z0-9_ -]+)', self._close_application),
            (r'send\s+whatsapp\s+message\s+to\s+(\+?\d+)\s+(.+)', self._send_whatsapp_message),
            (r'compose\s+email\s+to\s+([^\s]+)', self._compose_email),
            (r'shutdown|turn off', self._shutdown_system),
            (r'restart|reboot', self._restart_system),
            (r'lock|lock screen', self._lock_system),
            (r'sleep|hibernate', self._sleep_system),
            (r'volume|brightness', self._adjust_settings)
        ]

        for pattern, func in patterns:
            match = re.search(pattern, cmd)
            if match:
                return func(command)

        return "I'm not sure how to execute that system command."

    # ==========================================================
    # File Management
    # ==========================================================

    def _open_file(self, command: str) -> str:
        try:
            match = re.search(r'open file\s+(.+)', command, re.IGNORECASE)
            if not match:
                return "Please specify a file to open."
            file_path = os.path.expanduser(match.group(1).strip())
            if not os.path.isfile(file_path):
                return f"I couldn't find the file: {file_path}"
            os.startfile(file_path)
            return f"Opening file: {file_path}"
        except Exception as e:
            logger.error(f"Error opening file: {str(e)}")
            return f"Could not open file: {str(e)}"

    def _open_folder(self, command: str) -> str:
        try:
            match = re.search(r'open (folder|directory)\s+(.+)', command, re.IGNORECASE)
            folder_path = os.path.expanduser(match.group(2).strip()) if match else None
            if not os.path.isdir(folder_path):
                return f"I couldn't find the folder: {folder_path}"
            os.startfile(folder_path)
            return f"Opening folder: {folder_path}"
        except Exception as e:
            logger.error(f"Error opening folder: {str(e)}")
            return f"Could not open folder: {str(e)}"

    def _move_file_or_folder(self, command: str) -> str:
        try:
            match = re.search(r'move (file|folder)\s+(.+)\s+to\s+(.+)', command, re.IGNORECASE)
            item_type, src, dst = match.group(1), match.group(2).strip(), match.group(3).strip()
            src, dst = os.path.expanduser(src), os.path.expanduser(dst)
            if not os.path.exists(src):
                return f"Couldn't find {item_type}: {src}"
            shutil.move(src, dst)
            return f"Moved {item_type} from {src} to {dst}"
        except Exception as e:
            logger.error(f"Error moving: {str(e)}")
            return f"Could not move: {str(e)}"

    def _delete_file_or_folder(self, command: str) -> str:
        try:
            if self.safe_mode:
                return "Delete operations are disabled in safe mode."
            match = re.search(r'delete (file|folder)\s+(.+)', command, re.IGNORECASE)
            item_type, path = match.group(1), os.path.expanduser(match.group(2).strip())
            if not os.path.exists(path):
                return f"Couldn't find {item_type}: {path}"
            if item_type == 'file':
                os.remove(path)
            else:
                shutil.rmtree(path)
            return f"Deleted {item_type}: {path}"
        except Exception as e:
            logger.error(f"Error deleting: {str(e)}")
            return f"Could not delete: {str(e)}"

    def _create_folder(self, command: str) -> str:
        try:
            match = re.search(r'create (folder|directory)\s+(.+)', command, re.IGNORECASE)
            folder_path = os.path.expanduser(match.group(2).strip()) if match else None
            os.makedirs(folder_path, exist_ok=True)
            return f"Created folder: {folder_path}"
        except Exception as e:
            logger.error(f"Error creating folder: {str(e)}")
            return f"Could not create folder: {str(e)}"

    # ==========================================================
    # Application and Web Control
    # ==========================================================

    def _open_application(self, command: str) -> str:
        try:
            cmd_lower = command.lower()

            # recognized web apps first
            for key, url in self.web_apps.items():
                if key in cmd_lower:
                    webbrowser.open(url)
                    return f"Opening {key.title()}."

            # standard desktop apps
            for apps in self.common_apps.values():
                for app in apps:
                    if app.split('.')[0] in cmd_lower:
                        subprocess.Popen(app)
                        return f"Opening {app.split('.')[0]}."

            # attempt generic application name
            match = re.search(r'(open|launch|start|run)\s+([a-zA-Z0-9_ -]+)', command)
            if match:
                app_name = f"{match.group(2).strip()}.exe"
                try:
                    subprocess.Popen(app_name)
                    return f"Opening {app_name}"
                except Exception:
                    pass
            return "Couldn't find specified application."
        except Exception as e:
            logger.error(f"Error opening application: {str(e)}")
            return f"Could not open application: {str(e)}"

    def _close_application(self, command: str) -> str:
        try:
            match = re.search(r'(close|exit|quit)\s+([a-zA-Z0-9_ -]+)', command)
            app_name = f"{match.group(2).strip()}.exe" if match else None
            closed = False
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() == app_name.lower():
                    proc.terminate()
                    closed = True
            return f"Closed {app_name}" if closed else f"No running app named {app_name}"
        except Exception as e:
            logger.error(f"Error closing app: {str(e)}")
            return f"Could not close app: {str(e)}"

    # ==========================================================
    # Communication & Intent Automation
    # ==========================================================

    def _send_whatsapp_message(self, command: str) -> str:
        if not pywhatkit:
            return "WhatsApp messaging requires 'pywhatkit'. Install it via pip."
        try:
            match = re.search(r'send\s+whatsapp\s+message\s+to\s+(\+?\d+)\s+(.+)', command, re.IGNORECASE)
            number, message = match.group(1), match.group(2)
            pywhatkit.sendwhatmsg_instantly(number, message)
            return f"Sending WhatsApp message to {number}: {message}"
        except Exception as e:
            logger.error(f"WhatsApp send error: {str(e)}")
            return f"Could not send WhatsApp message: {str(e)}"

    def _compose_email(self, command: str) -> str:
        try:
            match = re.search(r'compose\s+email\s+to\s+([^\s]+)', command, re.IGNORECASE)
            email = match.group(1)
            draft = f"https://mail.google.com/mail/?view=cm&to={email}"
            webbrowser.open(draft)
            return f"Opening email composer for {email}"
        except Exception as e:
            logger.error(f"Email error: {str(e)}")
            return f"Could not compose email: {str(e)}"

    # ==========================================================
    # System Power and Settings
    # ==========================================================

    def _shutdown_system(self, command: str) -> str:
        if self.safe_mode:
            return "Shutdown command disabled in safe mode."
        try:
            subprocess.run("shutdown /s /t 0", shell=True)
            return "Shutting down system."
        except Exception as e:
            logger.error(f"Shutdown error: {str(e)}")
            return f"Could not shut down: {str(e)}"

    def _restart_system(self, command: str = "") -> str:
        if self.safe_mode:
            return "Restart command disabled in safe mode."
        try:
            subprocess.run("shutdown /r /t 0", shell=True)
            return "Restarting system."
        except Exception as e:
            logger.error(f"Restart error: {str(e)}")
            return f"Could not restart: {str(e)}"

    def _lock_system(self, command: str = "") -> str:
        try:
            ctypes.windll.user32.LockWorkStation()
            return "Locking system."
        except Exception as e:
            logger.error(f"Lock error: {str(e)}")
            return f"Could not lock: {str(e)}"

    def _sleep_system(self, command: str) -> str:
        try:
            if 'hibernate' in command.lower():
                subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 1,1,0", shell=True)
                return "Hibernating system."
            else:
                subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
                return "Sleeping system."
        except Exception as e:
            logger.error(f"Sleep error: {str(e)}")
            return f"Could not sleep: {str(e)}"

    def _adjust_settings(self, command: str) -> str:
        try:
            if 'volume' in command.lower():
                match = re.search(r'volume\s+(up|down)', command, re.IGNORECASE)
                if not match:
                    return "Specify up or down for volume."
                direction = match.group(1).lower()
                key = 175 if direction == 'up' else 174
                subprocess.run(f"powershell -c \"(New-Object -ComObject WScript.Shell).SendKeys([char]{key})\"", shell=True)
                return f"Volume {direction}."
            elif 'brightness' in command.lower():
                return "Brightness adjustment triggered (implementation varies)."
            return "Could not interpret settings command."
        except Exception as e:
            logger.error(f"Setting error: {str(e)}")
            return f"Could not adjust setting: {str(e)}"

    # ==========================================================
    # System Info
    # ==========================================================

    def get_system_info(self) -> Dict[str, Any]:
        try:
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': {disk.mountpoint: psutil.disk_usage(disk.mountpoint).percent
                                for disk in psutil.disk_partitions() if 'fixed' in disk.opts},
                'battery': psutil.sensors_battery().percent if hasattr(psutil, 'sensors_battery') else None
            }
        except Exception as e:
            logger.error(f"System info error: {str(e)}")
            return {'error': str(e)}

