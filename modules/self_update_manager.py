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
    Enhanced Self-Update Manager for Jarvis AI.
    Can fulfill smart code update requests, fetch modules, backup and restore safely.
    """

    def __init__(self, memory_manager):
        self.logger = logging.getLogger("jarvis.self_update")
        self.memory_manager = memory_manager
        self.update_settings = self._load_update_settings()
        self.current_version = "1.0.0"
        self.update_thread = None
        self.update_in_progress = False

    def _load_update_settings(self):
        try:
            settings = self.memory_manager.get_preference("update_settings")
            if not settings:
                settings = {
                    "auto_check_updates": True,
                    "check_interval": 86400,
                    "last_check": None,
                    "update_channel": "stable",
                    "backup_before_update": True,
                    "update_repository": "https://api.github.com/repos/user/jarvis/releases/latest"
                }
                self.memory_manager.store_preference("update_settings", settings)
            return settings
        except Exception as e:
            self.logger.error(f"Error loading update settings: {str(e)}")
            return {}

    #... [include all previous version/backup/download/restore methods here, unchanged] ...

    def fulfill_update_request(self, command: str) -> str:
        """
        Accepts a natural language update request, parses it, and takes action.
        Example: "Update weather module", "Install voice recognition", "Add system control"
        """
        try:
            self.logger.info(f"Received update request: {command}")

            # Simple intent parsing
            intent_words = command.lower().split()
            actions = ["update", "install", "add", "remove", "upgrade"]
            modules = [file[:-3] for file in os.listdir("modules") if file.endswith('.py')]

            action = next((word for word in intent_words if word in actions), None)
            target_module = next((mod for mod in modules if mod in intent_words), None)

            # If user wants to add a capability not present
            if action in ["add", "install"] and not target_module:
                return f"Sorry, I cannot add new capabilities yet unless you specify the module name available in the repo."

            # If updating existing module
            if action in ["update", "upgrade"] and target_module:
                self.logger.info(f"Preparing to update module: {target_module}")
                update_info = self.check_for_updates(force=True)
                if update_info:
                    path = self.download_update(update_info)
                    result = self.install_update(path)
                    return result
                else:
                    return "No updates available for your request."
            # If installing a new module from a repo (future: allow LLM code-gen)
            elif action in ["add", "install"] and target_module:
                return f"Module {target_module} appears installed. Try update or specify another feature."
            # If removing/disabling
            elif action == "remove" and target_module:
                try:
                    os.remove(os.path.join("modules", f"{target_module}.py"))
                    return f"Removed {target_module} module as you requested."
                except Exception as e:
                    return f"Could not remove {target_module}: {str(e)}"
            else:
                # Pass-through to upgrade system or ask for clarification
                if "jarvis" in intent_words or ("system" in intent_words and action):
                    update_info = self.check_for_updates(force=True)
                    if update_info:
                        path = self.download_update(update_info)
                        result = self.install_update(path)
                        return result
                    else:
                        return "No core system updates available now."
                return "Could not interpret your update request. Please rephrase or specify which module/feature to change."

        except Exception as e:
            self.logger.error(f"Error fulfilling update request: {str(e)}")
            return f"Error while trying to fulfill update: {str(e)}"

    #... [rest of class: keep all prior check_for_updates, download_update, install_update, backup, restore, list_backups, etc.] ...
