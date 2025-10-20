import os
import json
import logging
import requests
import subprocess
import shutil
import time
import threading
from datetime import datetime

class SelfUpdateManager:
    """
    Module for handling self-updates, version checking, and module management.
    Provides functionality to check for updates, download and install updates,
    and manage installed modules.
    """
    
    def __init__(self, memory_manager):
        """Initialize the Self-Update Manager."""
        self.logger = logging.getLogger("jarvis.self_update")
        self.memory_manager = memory_manager
        self.update_settings = self._load_update_settings()
        self.current_version = "1.0.0"  # Initial version
        self.update_thread = None
        self.update_in_progress = False
        
    def _load_update_settings(self):
        """Load update settings from memory manager"""
        try:
            settings = self.memory_manager.get_preference("update_settings")
            if not settings:
                # Default update settings
                settings = {
                    "auto_check_updates": True,
                    "check_interval": 86400,  # 24 hours
                    "last_check": None,
                    "update_channel": "stable",  # stable, beta, dev
                    "backup_before_update": True,
                    "update_repository": "https://api.github.com/repos/user/jarvis/releases/latest"
                }
                self.memory_manager.store_preference("update_settings", settings)
            return settings
        except Exception as e:
            self.logger.error(f"Error loading update settings: {str(e)}")
            return {}
    
    def get_current_version(self):
        """
        Get the current version of Jarvis.
        
        Returns:
            Current version string
        """
        return self.current_version
    
    def check_for_updates(self, force=False):
        """
        Check for available updates.
        
        Args:
            force: Force check even if last check was recent
            
        Returns:
            Update information if available, None otherwise
        """
        try:
            # Check if we should check for updates
            if not force:
                last_check = self.update_settings.get("last_check")
                check_interval = self.update_settings.get("check_interval", 86400)
                
                if last_check:
                    last_check_time = datetime.fromisoformat(last_check)
                    time_since_check = (datetime.now() - last_check_time).total_seconds()
                    
                    if time_since_check < check_interval:
                        self.logger.info(f"Skipping update check, last check was {time_since_check} seconds ago")
                        return None
            
            # Update last check time
            self.update_settings["last_check"] = datetime.now().isoformat()
            self.memory_manager.store_preference("update_settings", self.update_settings)
            
            # Check for updates from repository
            update_repo = self.update_settings.get("update_repository")
            update_channel = self.update_settings.get("update_channel", "stable")
            
            self.logger.info(f"Checking for updates from {update_repo}, channel: {update_channel}")
            
            # This is a placeholder for actual update checking logic
            # In a real implementation, this would make API calls to check for updates
            
            # Simulate update check
            # In a real implementation, this would parse the response from the update repository
            latest_version = "1.1.0"  # This would come from the update repository
            
            if self._compare_versions(latest_version, self.current_version) > 0:
                update_info = {
                    "version": latest_version,
                    "release_date": datetime.now().isoformat(),
                    "changelog": "- Added new features\n- Fixed bugs\n- Improved performance",
                    "download_url": "https://example.com/jarvis/download/1.1.0",
                    "size": "10.5 MB"
                }
                return update_info
            else:
                return None
        except Exception as e:
            self.logger.error(f"Error checking for updates: {str(e)}")
            return None
    
    def _compare_versions(self, version1, version2):
        """
        Compare two version strings.
        
        Args:
            version1: First version string
            version2: Second version string
            
        Returns:
            1 if version1 > version2, -1 if version1 < version2, 0 if equal
        """
        v1_parts = list(map(int, version1.split(".")))
        v2_parts = list(map(int, version2.split(".")))
        
        # Pad with zeros if necessary
        while len(v1_parts) < len(v2_parts):
            v1_parts.append(0)
        while len(v2_parts) < len(v1_parts):
            v2_parts.append(0)
        
        for i in range(len(v1_parts)):
            if v1_parts[i] > v2_parts[i]:
                return 1
            elif v1_parts[i] < v2_parts[i]:
                return -1
        
        return 0
    
    def download_update(self, update_info):
        """
        Download an update.
        
        Args:
            update_info: Update information dictionary
            
        Returns:
            Path to downloaded update or None if failed
        """
        try:
            if not update_info or "download_url" not in update_info:
                return None
                
            download_url = update_info["download_url"]
            version = update_info["version"]
            
            # Create downloads directory if it doesn't exist
            downloads_dir = os.path.join(os.getcwd(), "downloads")
            if not os.path.exists(downloads_dir):
                os.makedirs(downloads_dir)
                
            # Download file
            self.logger.info(f"Downloading update from {download_url}")
            
            # This is a placeholder for actual download logic
            # In a real implementation, this would download the file from the URL
            
            # Simulate download
            download_path = os.path.join(downloads_dir, f"jarvis-{version}.zip")
            
            # Create an empty file to simulate download
            with open(download_path, "w") as f:
                f.write("Simulated update package")
                
            return download_path
        except Exception as e:
            self.logger.error(f"Error downloading update: {str(e)}")
            return None
    
    def install_update(self, update_path):
        """
        Install an update from a downloaded package.
        
        Args:
            update_path: Path to the update package
            
        Returns:
            Success message or error message
        """
        if self.update_in_progress:
            return "Update already in progress"
            
        self.update_in_progress = True
        
        try:
            if not os.path.exists(update_path):
                self.update_in_progress = False
                return f"Update package not found at {update_path}"
                
            # Backup current installation if enabled
            if self.update_settings.get("backup_before_update", True):
                backup_result = self._backup_current_installation()
                if not backup_result.startswith("Backup"):
                    self.update_in_progress = False
                    return f"Failed to create backup: {backup_result}"
            
            # This is a placeholder for actual update installation logic
            # In a real implementation, this would extract the update package and replace files
            
            # Simulate installation
            self.logger.info(f"Installing update from {update_path}")
            time.sleep(2)  # Simulate installation time
            
            # Update current version
            # In a real implementation, this would read the version from the update package
            self.current_version = "1.1.0"
            
            # Clean up
            os.remove(update_path)
            
            self.update_in_progress = False
            return f"Update installed successfully. New version: {self.current_version}"
        except Exception as e:
            self.update_in_progress = False
            self.logger.error(f"Error installing update: {str(e)}")
            return f"Failed to install update. Error: {str(e)}"
    
    def _backup_current_installation(self):
        """Create a backup of the current installation"""
        try:
            # Create backups directory if it doesn't exist
            backups_dir = os.path.join(os.getcwd(), "backups")
            if not os.path.exists(backups_dir):
                os.makedirs(backups_dir)
                
            # Create backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backups_dir, f"jarvis_backup_{timestamp}")
            
            # This is a placeholder for actual backup logic
            # In a real implementation, this would copy all necessary files to the backup directory
            
            # Simulate backup
            os.makedirs(backup_path, exist_ok=True)
            
            # Copy main files
            shutil.copy("jarvis.py", backup_path)
            
            # Copy modules directory
            modules_backup_path = os.path.join(backup_path, "modules")
            os.makedirs(modules_backup_path, exist_ok=True)
            
            for module_file in os.listdir("modules"):
                if module_file.endswith(".py"):
                    shutil.copy(os.path.join("modules", module_file), modules_backup_path)
            
            return f"Backup created at {backup_path}"
        except Exception as e:
            self.logger.error(f"Error creating backup: {str(e)}")
            return f"Failed to create backup. Error: {str(e)}"
    
    def restore_backup(self, backup_path):
        """
        Restore from a backup.
        
        Args:
            backup_path: Path to the backup directory
            
        Returns:
            Success message or error message
        """
        try:
            if not os.path.exists(backup_path):
                return f"Backup not found at {backup_path}"
                
            # This is a placeholder for actual restore logic
            # In a real implementation, this would copy files from the backup directory
            
            # Simulate restore
            self.logger.info(f"Restoring from backup at {backup_path}")
            
            # Copy main files
            shutil.copy(os.path.join(backup_path, "jarvis.py"), "jarvis.py")
            
            # Copy modules
            modules_backup_path = os.path.join(backup_path, "modules")
            if os.path.exists(modules_backup_path):
                for module_file in os.listdir(modules_backup_path):
                    if module_file.endswith(".py"):
                        shutil.copy(
                            os.path.join(modules_backup_path, module_file),
                            os.path.join("modules", module_file)
                        )
            
            return "Backup restored successfully"
        except Exception as e:
            self.logger.error(f"Error restoring backup: {str(e)}")
            return f"Failed to restore backup. Error: {str(e)}"
    
    def list_backups(self):
        """
        List all available backups.
        
        Returns:
            List of backup information dictionaries
        """
        try:
            backups_dir = os.path.join(os.getcwd(), "backups")
            if not os.path.exists(backups_dir):
                return []
                
            backups = []
            for backup in os.listdir(backups_dir):
                backup_path = os.path.join(backups_dir, backup)
                if os.path.isdir(backup_path) and backup.startswith("jarvis_backup_"):
                    # Extract timestamp from backup name
                    timestamp_str = backup.replace("jarvis_backup_", "")
                    try:
                        timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                        formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        formatted_time = "Unknown"
                        
                    backups.append({
                        "name": backup,
                        "path": backup_path,
                        "created": formatted_time,
                        "size": self._get_directory_size(backup_path)
                    })
                    
            return backups
        except Exception as e:
            self.logger.error(f"Error listing backups: {str(e)}")
            return []
    
    def _get_directory_size(self, path):
        """Get the size of a directory in bytes"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
        
        # Convert to human-readable format
        for unit in ["B", "KB", "MB", "GB"]:
            if total_size < 1024:
                return f"{total_size:.2f} {unit}"
            total_size /= 1024
        return f"{total_size:.2f} TB"
    
    def delete_backup(self, backup_path):
        """
        Delete a backup.
        
        Args:
            backup_path: Path to the backup directory
            
        Returns:
            Success message or error message
        """
        try:
            if not os.path.exists(backup_path):
                return f"Backup not found at {backup_path}"
                
            shutil.rmtree(backup_path)
            return "Backup deleted successfully"
        except Exception as e:
            self.logger.error(f"Error deleting backup: {str(e)}")
            return f"Failed to delete backup. Error: {str(e)}"
    
    def start_auto_update_checker(self):
        """
        Start the automatic update checker in a background thread.
        
        Returns:
            Success message
        """
        if self.update_thread and self.update_thread.is_alive():
            return "Auto update checker is already running"
            
        self.update_thread = threading.Thread(target=self._auto_update_checker)
        self.update_thread.daemon = True
        self.update_thread.start()
        
        return "Auto update checker started"
    
    def _auto_update_checker(self):
        """Run the automatic update checker"""
        while True:
            if self.update_settings.get("auto_check_updates", True):
                update_info = self.check_for_updates()
                if update_info:
                    self.logger.info(f"New update available: {update_info['version']}")
                    # In a real implementation, this would notify the user
            
            # Sleep for the check interval
            check_interval = self.update_settings.get("check_interval", 86400)
            time.sleep(check_interval)
    
    def update_settings_value(self, setting, value):
        """
        Update a setting value.
        
        Args:
            setting: Setting name
            value: New setting value
            
        Returns:
            Success message
        """
        try:
            self.update_settings[setting] = value
            self.memory_manager.store_preference("update_settings", self.update_settings)
            return f"Setting '{setting}' updated to '{value}'"
        except Exception as e:
            self.logger.error(f"Error updating setting: {str(e)}")
            return f"Failed to update setting. Error: {str(e)}"
    
    def get_module_info(self, module_name=None):
        """
        Get information about installed modules.
        
        Args:
            module_name: Name of the module to get info for, or None for all modules
            
        Returns:
            Module information dictionary or list of dictionaries
        """
        try:
            modules_dir = os.path.join(os.getcwd(), "modules")
            if not os.path.exists(modules_dir):
                return []
                
            if module_name:
                module_path = os.path.join(modules_dir, f"{module_name}.py")
                if not os.path.exists(module_path):
                    return None
                    
                return self._get_module_info(module_name, module_path)
            else:
                modules = []
                for file in os.listdir(modules_dir):
                    if file.endswith(".py"):
                        module_name = file[:-3]
                        module_path = os.path.join(modules_dir, file)
                        modules.append(self._get_module_info(module_name, module_path))
                return modules
        except Exception as e:
            self.logger.error(f"Error getting module info: {str(e)}")
            return []
    
    def _get_module_info(self, module_name, module_path):
        """Get information about a module"""
        try:
            # Get file stats
            stats = os.stat(module_path)
            modified_time = datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            size = stats.st_size
            
            # Read first few lines to extract docstring
            description = ""
            with open(module_path, "r") as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if '"""' in line or "'''" in line:
                        # Found start of docstring
                        start_line = i
                        # Find end of docstring
                        for j in range(i + 1, min(i + 20, len(lines))):
                            if '"""' in lines[j] or "'''" in lines[j]:
                                # Extract docstring
                                docstring_lines = lines[start_line:j+1]
                                description = "".join(docstring_lines).strip()
                                description = description.replace('"""', "").replace("'''", "").strip()
                                break
                        break
            
            return {
                "name": module_name,
                "path": module_path,
                "modified": modified_time,
                "size": size,
                "description": description
            }
        except Exception as e:
            self.logger.error(f"Error getting module info: {str(e)}")
            return {
                "name": module_name,
                "path": module_path,
                "error": str(e)
            }
