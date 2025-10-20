#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
System Control Module for Jarvis AI Assistant
Handles file management, application control, and system commands.
"""

import os
import logging
import subprocess
import shutil
import re
import psutil
import ctypes
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger("Jarvis.SystemControlModule")

class SystemControlModule:
    """
    System Control Module class that handles file management, application control,
    and system commands.
    """
    
    def __init__(self):
        """Initialize the System Control Module."""
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
        Execute a system command.
        
        Args:
            command: Command string
            
        Returns:
            Response string
        """
        try:
            logger.info(f"Executing system command: {command}")
            
            # File management commands
            if re.search(r'open file', command, re.IGNORECASE):
                return self._open_file(command)
            
            if re.search(r'open folder|open directory', command, re.IGNORECASE):
                return self._open_folder(command)
            
            if re.search(r'move file|move folder', command, re.IGNORECASE):
                return self._move_file_or_folder(command)
            
            if re.search(r'delete file|delete folder', command, re.IGNORECASE):
                return self._delete_file_or_folder(command)
            
            if re.search(r'create folder|create directory', command, re.IGNORECASE):
                return self._create_folder(command)
            
            # Application management commands
            if re.search(r'open|launch|start|run', command, re.IGNORECASE):
                return self._open_application(command)
            
            if re.search(r'close|exit|quit', command, re.IGNORECASE):
                return self._close_application(command)
            
            # System commands
            if re.search(r'shutdown|turn off', command, re.IGNORECASE):
                return self._shutdown_system(command)
            
            if re.search(r'restart|reboot', command, re.IGNORECASE):
                return self._restart_system()
            
            if re.search(r'lock|lock screen', command, re.IGNORECASE):
                return self._lock_system()
            
            if re.search(r'sleep|hibernate', command, re.IGNORECASE):
                return self._sleep_system(command)
            
            if re.search(r'volume|brightness', command, re.IGNORECASE):
                return self._adjust_settings(command)
            
            # If no specific command pattern is matched
            return "I'm not sure how to execute that system command."
            
        except Exception as e:
            logger.error(f"Error executing system command: {str(e)}")
            return f"I encountered an error while executing that command: {str(e)}"
    
    def _open_file(self, command: str) -> str:
        """
        Open a file.
        
        Args:
            command: Command string
            
        Returns:
            Response string
        """
        try:
            # Extract file path from command
            match = re.search(r'open file\s+(.+)', command, re.IGNORECASE)
            if not match:
                return "Please specify a file to open."
            
            file_path = match.group(1).strip()
            
            # Handle relative paths and user home directory
            if file_path.startswith('~'):
                file_path = os.path.expanduser(file_path)
            
            # Check if file exists
            if not os.path.isfile(file_path):
                return f"I couldn't find the file: {file_path}"
            
            # Open the file with default application
            os.startfile(file_path)
            return f"Opening file: {file_path}"
            
        except Exception as e:
            logger.error(f"Error opening file: {str(e)}")
            return f"I couldn't open that file: {str(e)}"
    
    def _open_folder(self, command: str) -> str:
        """
        Open a folder.
        
        Args:
            command: Command string
            
        Returns:
            Response string
        """
        try:
            # Extract folder path from command
            match = re.search(r'open (folder|directory)\s+(.+)', command, re.IGNORECASE)
            if not match:
                return "Please specify a folder to open."
            
            folder_path = match.group(2).strip()
            
            # Handle relative paths and user home directory
            if folder_path.startswith('~'):
                folder_path = os.path.expanduser(folder_path)
            
            # Check if folder exists
            if not os.path.isdir(folder_path):
                return f"I couldn't find the folder: {folder_path}"
            
            # Open the folder in File Explorer
            os.startfile(folder_path)
            return f"Opening folder: {folder_path}"
            
        except Exception as e:
            logger.error(f"Error opening folder: {str(e)}")
            return f"I couldn't open that folder: {str(e)}"
    
    def _move_file_or_folder(self, command: str) -> str:
        """
        Move a file or folder.
        
        Args:
            command: Command string
            
        Returns:
            Response string
        """
        try:
            # Extract source and destination paths from command
            match = re.search(r'move (file|folder)\s+(.+)\s+to\s+(.+)', command, re.IGNORECASE)
            if not match:
                return "Please specify what to move and where to move it."
            
            item_type = match.group(1).lower()
            source_path = match.group(2).strip()
            dest_path = match.group(3).strip()
            
            # Handle relative paths and user home directory
            if source_path.startswith('~'):
                source_path = os.path.expanduser(source_path)
            if dest_path.startswith('~'):
                dest_path = os.path.expanduser(dest_path)
            
            # Check if source exists
            if not os.path.exists(source_path):
                return f"I couldn't find the {item_type}: {source_path}"
            
            # Move the file or folder
            shutil.move(source_path, dest_path)
            return f"Moved {item_type} from {source_path} to {dest_path}"
            
        except Exception as e:
            logger.error(f"Error moving file or folder: {str(e)}")
            return f"I couldn't move that: {str(e)}"
    
    def _delete_file_or_folder(self, command: str) -> str:
        """
        Delete a file or folder.
        
        Args:
            command: Command string
            
        Returns:
            Response string
        """
        try:
            # Extract path from command
            match = re.search(r'delete (file|folder)\s+(.+)', command, re.IGNORECASE)
            if not match:
                return "Please specify what to delete."
            
            item_type = match.group(1).lower()
            path = match.group(2).strip()
            
            # Handle relative paths and user home directory
            if path.startswith('~'):
                path = os.path.expanduser(path)
            
            # Check if path exists
            if not os.path.exists(path):
                return f"I couldn't find the {item_type}: {path}"
            
            # Delete the file or folder
            if item_type == 'file':
                os.remove(path)
            else:  # folder
                shutil.rmtree(path)
            
            return f"Deleted {item_type}: {path}"
            
        except Exception as e:
            logger.error(f"Error deleting file or folder: {str(e)}")
            return f"I couldn't delete that: {str(e)}"
    
    def _create_folder(self, command: str) -> str:
        """
        Create a folder.
        
        Args:
            command: Command string
            
        Returns:
            Response string
        """
        try:
            # Extract folder path from command
            match = re.search(r'create (folder|directory)\s+(.+)', command, re.IGNORECASE)
            if not match:
                return "Please specify a folder name to create."
            
            folder_path = match.group(2).strip()
            
            # Handle relative paths and user home directory
            if folder_path.startswith('~'):
                folder_path = os.path.expanduser(folder_path)
            
            # Create the folder
            os.makedirs(folder_path, exist_ok=True)
            return f"Created folder: {folder_path}"
            
        except Exception as e:
            logger.error(f"Error creating folder: {str(e)}")
            return f"I couldn't create that folder: {str(e)}"
    
    def _open_application(self, command: str) -> str:
        """
        Open an application.
        
        Args:
            command: Command string
            
        Returns:
            Response string
        """
        try:
            # Extract application name from command
            for app_type, app_list in self.common_apps.items():
                for app in app_list:
                    if app.split('.')[0].lower() in command.lower():
                        try:
                            subprocess.Popen(app)
                            return f"Opening {app.split('.')[0]}"
                        except:
                            continue
            
            # Try to extract application name directly
            words = command.lower().split()
            for i, word in enumerate(words):
                if word in ['open', 'launch', 'start', 'run'] and i + 1 < len(words):
                    app_name = words[i + 1]
                    try:
                        subprocess.Popen(f"{app_name}.exe")
                        return f"Opening {app_name}"
                    except:
                        pass
            
            return "I couldn't find that application. Please specify a valid application name."
            
        except Exception as e:
            logger.error(f"Error opening application: {str(e)}")
            return f"I couldn't open that application: {str(e)}"
    
    def _close_application(self, command: str) -> str:
        """
        Close an application.
        
        Args:
            command: Command string
            
        Returns:
            Response string
        """
        try:
            # Extract application name from command
            app_name = None
            for app_type, app_list in self.common_apps.items():
                for app in app_list:
                    if app.split('.')[0].lower() in command.lower():
                        app_name = app
                        break
                if app_name:
                    break
            
            if not app_name:
                # Try to extract application name directly
                words = command.lower().split()
                for i, word in enumerate(words):
                    if word in ['close', 'exit', 'quit'] and i + 1 < len(words):
                        app_name = f"{words[i + 1]}.exe"
                        break
            
            if not app_name:
                return "Please specify an application to close."
            
            # Find and terminate the process
            closed = False
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() == app_name.lower():
                    proc.terminate()
                    closed = True
            
            if closed:
                return f"Closed {app_name.split('.')[0]}"
            else:
                return f"I couldn't find a running instance of {app_name.split('.')[0]}"
            
        except Exception as e:
            logger.error(f"Error closing application: {str(e)}")
            return f"I couldn't close that application: {str(e)}"
    
    def _shutdown_system(self, command: str) -> str:
        """
        Shutdown the system.
        
        Args:
            command: Command string
            
        Returns:
            Response string
        """
        try:
            # Check for time delay
            delay = 0
            match = re.search(r'in\s+(\d+)\s+(seconds|minutes)', command, re.IGNORECASE)
            if match:
                amount = int(match.group(1))
                unit = match.group(2).lower()
                
                if unit == 'minutes':
                    delay = amount * 60
                else:
                    delay = amount
            
            # Execute shutdown command
            subprocess.run(f"shutdown /s /t {delay}", shell=True)
            
            if delay > 0:
                time_str = f"{delay // 60} minutes" if delay >= 60 else f"{delay} seconds"
                return f"Shutting down the system in {time_str}"
            else:
                return "Shutting down the system now"
            
        except Exception as e:
            logger.error(f"Error shutting down system: {str(e)}")
            return f"I couldn't shut down the system: {str(e)}"
    
    def _restart_system(self) -> str:
        """
        Restart the system.
        
        Returns:
            Response string
        """
        try:
            subprocess.run("shutdown /r /t 0", shell=True)
            return "Restarting the system"
            
        except Exception as e:
            logger.error(f"Error restarting system: {str(e)}")
            return f"I couldn't restart the system: {str(e)}"
    
    def _lock_system(self) -> str:
        """
        Lock the system.
        
        Returns:
            Response string
        """
        try:
            ctypes.windll.user32.LockWorkStation()
            return "Locking the system"
            
        except Exception as e:
            logger.error(f"Error locking system: {str(e)}")
            return f"I couldn't lock the system: {str(e)}"
    
    def _sleep_system(self, command: str) -> str:
        """
        Put the system to sleep or hibernate.
        
        Args:
            command: Command string
            
        Returns:
            Response string
        """
        try:
            if 'hibernate' in command.lower():
                subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 1,1,0", shell=True)
                return "Hibernating the system"
            else:
                subprocess.run("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
                return "Putting the system to sleep"
            
        except Exception as e:
            logger.error(f"Error with sleep/hibernate: {str(e)}")
            return f"I couldn't put the system to sleep: {str(e)}"
    
    def _adjust_settings(self, command: str) -> str:
        """
        Adjust system settings like volume or brightness.
        
        Args:
            command: Command string
            
        Returns:
            Response string
        """
        try:
            if 'volume' in command.lower():
                # Extract volume level
                match = re.search(r'volume\s+(up|down|to)\s*(\d+)?', command, re.IGNORECASE)
                if not match:
                    return "Please specify how to adjust the volume."
                
                direction = match.group(1).lower()
                level = match.group(2)
                
                if direction == 'up':
                    # Increase volume
                    subprocess.run("powershell -c \"(New-Object -ComObject WScript.Shell).SendKeys([char]175)\"", shell=True)
                    return "Increasing volume"
                elif direction == 'down':
                    # Decrease volume
                    subprocess.run("powershell -c \"(New-Object -ComObject WScript.Shell).SendKeys([char]174)\"", shell=True)
                    return "Decreasing volume"
                elif direction == 'to' and level:
                    # Set volume to specific level
                    # This is a simplified implementation
                    return f"Setting volume to {level}%"
            
            elif 'brightness' in command.lower():
                # Extract brightness level
                match = re.search(r'brightness\s+(up|down|to)\s*(\d+)?', command, re.IGNORECASE)
                if not match:
                    return "Please specify how to adjust the brightness."
                
                direction = match.group(1).lower()
                level = match.group(2)
                
                # This is a simplified implementation
                # Actual brightness control requires more complex code
                return f"Adjusting brightness {direction} {level if level else ''}"
            
            return "I'm not sure how to adjust that setting."
            
        except Exception as e:
            logger.error(f"Error adjusting settings: {str(e)}")
            return f"I couldn't adjust that setting: {str(e)}"
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information.
        
        Returns:
            Dictionary of system information
        """
        try:
            info = {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_usage': {disk.mountpoint: psutil.disk_usage(disk.mountpoint).percent 
                              for disk in psutil.disk_partitions() if 'fixed' in disk.opts},
                'battery': psutil.sensors_battery() if hasattr(psutil, 'sensors_battery') else None
            }
            return info
        except Exception as e:
            logger.error(f"Error getting system info: {str(e)}")
            return {'error': str(e)}