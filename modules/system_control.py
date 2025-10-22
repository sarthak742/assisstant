#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
System Control Module for Jarvis AI Assistant (Improved)
Handles file management, application control, system commands (Windows).
"""

import os
import logging
import subprocess
import shutil
import re
import psutil
import ctypes
from typing import Dict, Any

logger = logging.getLogger("Jarvis.SystemControlModule")

class SystemControlModule:
    """
    Handles file management, application and system commands (Windows-focused).
    """

    def __init__(self):
        self.common_apps = {
            'browser': ['chrome.exe', 'firefox.exe', 'msedge.exe'],
            'editor': ['notepad.exe', 'code.exe', 'wordpad.exe'],
            'media': ['wmplayer.exe', 'vlc.exe', 'spotify.exe'],
            'office': ['winword.exe', 'excel.exe', 'powerpnt.exe'],
            'terminal': ['cmd.exe', 'powershell.exe', 'windowsterminal.exe']
        }
        logger.info("System Control Module initialized")

    def execute_command(self, command: str) -> str:
        """
        Unified natural-language command executor.
        """
        try:
            cmd = command.lower().strip()

            patterns = [
                (r'open file\s+(.+)', self._open_file),
                (r'open (folder|directory)\s+(.+)', self._open_folder),
                (r'move (file|folder)\s+(.+)\s+to\s+(.+)', self._move_file_or_folder),
                (r'delete (file|folder)\s+(.+)', self._delete_file_or_folder),
                (r'create (folder|directory)\s+(.+)', self._create_folder),
                (r'(open|launch|start|run)\s+([a-zA-Z0-9_ -]+)', self._open_application),
                (r'(close|exit|quit)\s+([a-zA-Z0-9_ -]+)', self._close_application),
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
        except Exception as e:
            logger.error(f"System command error: {str(e)}")
            return f"I encountered an error while executing that command: {str(e)}"

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
            if not match:
                return "Please specify a folder to open."
            folder_path = os.path.expanduser(match.group(2).strip())
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
            if not match:
                return "Specify what to move and the destination."
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
            match = re.search(r'delete (file|folder)\s+(.+)', command, re.IGNORECASE)
            if not match:
                return "Specify what to delete."
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
            if not match:
                return "Specify a folder name."
            folder_path = os.path.expanduser(match.group(2).strip())
            os.makedirs(folder_path, exist_ok=True)
            return f"Created folder: {folder_path}"
        except Exception as e:
            logger.error(f"Error creating folder: {str(e)}")
            return f"Could not create folder: {str(e)}"

    def _open_application(self, command: str) -> str:
        try:
            app_found = False
            for apps in self.common_apps.values():
                for app in apps:
                    if app.split('.')[0] in command.lower():
                        subprocess.Popen(app)
                        return f"Opening {app.split('.')[0]}"
            # Try to extract generic app name
            match = re.search(r'(open|launch|start|run)\s+([a-zA-Z0-9_ -]+)', command)
            if match:
                app_name = f"{match.group(2).strip()}.exe"
                try:
                    subprocess.Popen(app_name)
                    return f"Opening {app_name}"
                except:
                    pass
            return "Couldn't find specified application."
        except Exception as e:
            logger.error(f"Error opening app: {str(e)}")
            return f"Could not open application: {str(e)}"

    def _close_application(self, command: str) -> str:
        try:
            match = re.search(r'(close|exit|quit)\s+([a-zA-Z0-9_ -]+)', command)
            app_name = f"{match.group(2).strip()}.exe" if match else None
            if not app_name:
                return "Specify the application to close."
            closed = False
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() == app_name.lower():
                    proc.terminate()
                    closed = True
            return f"Closed {app_name}" if closed else f"Couldn't find running {app_name}"
        except Exception as e:
            logger.error(f"Error closing app: {str(e)}")
            return f"Could not close application: {str(e)}"

    def _shutdown_system(self, command: str) -> str:
        try:
            delay = 0
            match = re.search(r'in\s+(\d+)\s+(seconds|minutes)', command, re.IGNORECASE)
            if match:
                delay = int(match.group(1)) * (60 if 'minute' in match.group(2) else 1)
            subprocess.run(f"shutdown /s /t {delay}", shell=True)
            return f"Shutting down in {delay}s" if delay else "Shutting down now."
        except Exception as e:
            logger.error(f"Shutdown error: {str(e)}")
            return f"Could not shut down: {str(e)}"

    def _restart_system(self, command: str = "") -> str:
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
            return f"Could not sleep/hibernate: {str(e)}"

    def _adjust_settings(self, command: str) -> str:
        try:
            if 'volume' in command.lower():
                match = re.search(r'volume\s+(up|down|to)\s*(\d+)?', command, re.IGNORECASE)
                if not match:
                    return "Specify how to adjust volume."
                direction, level = match.group(1).lower(), match.group(2)
                if direction == 'up':
                    subprocess.run("powershell -c \"(New-Object -ComObject WScript.Shell).SendKeys([char]175)\"", shell=True)
                    return "Volume up."
                elif direction == 'down':
                    subprocess.run("powershell -c \"(New-Object -ComObject WScript.Shell).SendKeys([char]174)\"", shell=True)
                    return "Volume down."
                elif direction == 'to' and level:
                    return f"Set volume to {level}%"
            elif 'brightness' in command.lower():
                match = re.search(r'brightness\s+(up|down|to)\s*(\d+)?', command, re.IGNORECASE)
                if not match:
                    return "Specify how to adjust brightness."
                direction, level = match.group(1).lower(), match.group(2)
                return f"Adjusting brightness {direction} {level if level else ''}"
            return "Not sure how to adjust that setting."
        except Exception as e:
            logger.error(f"Setting adj error: {str(e)}")
            return f"Could not adjust setting: {str(e)}"

    def get_system_info(self) -> Dict[str, Any]:
        try:
            return {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': {disk.mountpoint: psutil.disk_usage(disk.mountpoint).percent
                                for disk in psutil.disk_partitions() if 'fixed' in disk.opts},
                'battery': psutil.sensors_battery() if hasattr(psutil, 'sensors_battery') else None
            }
        except Exception as e:
            logger.error(f"SysInfo error: {str(e)}")
            return {'error': str(e)}
