import os
import json
import logging
import hashlib
import getpass
import time
import random
import string
from datetime import datetime

class SecurityModule:
    """
    Module for handling user authentication, personalization, and privacy controls.
    Provides user authentication via voice or password, personalized responses,
    and privacy control for stored data.
    """
    
    def __init__(self, memory_manager):
        """Initialize the Security & Personalization Module."""
        self.logger = logging.getLogger("jarvis.security")
        self.memory_manager = memory_manager
        self.user_authenticated = False
        self.auth_timestamp = None
        self.auth_timeout = 3600  # 1 hour timeout by default
        self.security_settings = self._load_security_settings()
        self.personalization = self._load_personalization()
        
    def _load_security_settings(self):
        """Load security settings from memory manager"""
        try:
            settings = self.memory_manager.get_preference("security_settings")
            if not settings:
                # Default security settings
                settings = {
                    "auth_required": True,
                    "auth_timeout": 3600,  # 1 hour
                    "voice_auth_enabled": False,
                    "password_hash": "",
                    "voice_print": "",
                    "privacy_level": "standard"  # standard, high, paranoid
                }
                self.memory_manager.store_preference("security_settings", settings)
            
            # Update instance variable with settings
            self.auth_timeout = settings.get("auth_timeout", 3600)
            return settings
        except Exception as e:
            self.logger.error(f"Error loading security settings: {str(e)}")
            return {}
    
    def _load_personalization(self):
        """Load personalization settings from memory manager"""
        try:
            personalization = self.memory_manager.get_preference("personalization")
            if not personalization:
                # Default personalization settings
                personalization = {
                    "user_name": "User",
                    "assistant_name": "Jarvis",
                    "formality_level": "casual",  # formal, casual, friendly
                    "response_style": "concise",  # concise, detailed, technical
                    "favorite_topics": [],
                    "interests": [],
                    "greeting_style": "standard"  # standard, enthusiastic, professional
                }
                self.memory_manager.store_preference("personalization", personalization)
            return personalization
        except Exception as e:
            self.logger.error(f"Error loading personalization: {str(e)}")
            return {}
    
    def authenticate_user(self, password=None, voice_print=None):
        """
        Authenticate user with password or voice print.
        
        Args:
            password: User password (optional)
            voice_print: Voice print data (optional)
            
        Returns:
            Boolean indicating authentication success
        """
        # Check if authentication is required
        if not self.security_settings.get("auth_required", True):
            self.user_authenticated = True
            self.auth_timestamp = time.time()
            return True
            
        # Check if already authenticated within timeout period
        if self.user_authenticated and self.auth_timestamp:
            if time.time() - self.auth_timestamp < self.auth_timeout:
                # Refresh the authentication timestamp
                self.auth_timestamp = time.time()
                return True
        
        # Try password authentication
        if password:
            stored_hash = self.security_settings.get("password_hash", "")
            if stored_hash and self._verify_password(password, stored_hash):
                self.user_authenticated = True
                self.auth_timestamp = time.time()
                return True
        
        # Try voice authentication if enabled
        if voice_print and self.security_settings.get("voice_auth_enabled", False):
            stored_voice_print = self.security_settings.get("voice_print", "")
            if stored_voice_print and self._verify_voice_print(voice_print, stored_voice_print):
                self.user_authenticated = True
                self.auth_timestamp = time.time()
                return True
        
        # Authentication failed
        self.user_authenticated = False
        return False
    
    def _verify_password(self, password, stored_hash):
        """Verify password against stored hash"""
        try:
            # In a real implementation, use a proper password hashing library
            # This is a simplified example using hashlib
            salt = stored_hash.split("$")[0]
            hash_value = hashlib.sha256((salt + password).encode()).hexdigest()
            full_hash = f"{salt}${hash_value}"
            return full_hash == stored_hash
        except Exception as e:
            self.logger.error(f"Error verifying password: {str(e)}")
            return False
    
    def _verify_voice_print(self, voice_print, stored_voice_print):
        """Verify voice print against stored voice print"""
        # This is a placeholder - actual implementation would require
        # voice recognition and comparison algorithms
        return False
    
    def set_password(self, password):
        """
        Set a new password for authentication.
        
        Args:
            password: New password to set
            
        Returns:
            Success message
        """
        try:
            # Generate a random salt
            salt = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
            
            # Hash the password with the salt
            hash_value = hashlib.sha256((salt + password).encode()).hexdigest()
            full_hash = f"{salt}${hash_value}"
            
            # Update security settings
            settings = self.security_settings
            settings["password_hash"] = full_hash
            self.memory_manager.store_preference("security_settings", settings)
            self.security_settings = settings
            
            return "Password set successfully"
        except Exception as e:
            self.logger.error(f"Error setting password: {str(e)}")
            return f"Failed to set password. Error: {str(e)}"
    
    def set_voice_print(self, voice_print):
        """
        Set a new voice print for authentication.
        
        Args:
            voice_print: Voice print data
            
        Returns:
            Success message
        """
        try:
            # Update security settings
            settings = self.security_settings
            settings["voice_print"] = voice_print
            settings["voice_auth_enabled"] = True
            self.memory_manager.store_preference("security_settings", settings)
            self.security_settings = settings
            
            return "Voice authentication enabled"
        except Exception as e:
            self.logger.error(f"Error setting voice print: {str(e)}")
            return f"Failed to set voice print. Error: {str(e)}"
    
    def update_security_setting(self, setting, value):
        """
        Update a security setting.
        
        Args:
            setting: Setting name
            value: New setting value
            
        Returns:
            Success message
        """
        try:
            settings = self.security_settings
            settings[setting] = value
            
            # Update instance variable if auth_timeout is changed
            if setting == "auth_timeout":
                self.auth_timeout = value
                
            self.memory_manager.store_preference("security_settings", settings)
            self.security_settings = settings
            
            return f"Security setting '{setting}' updated to '{value}'"
        except Exception as e:
            self.logger.error(f"Error updating security setting: {str(e)}")
            return f"Failed to update security setting. Error: {str(e)}"
    
    def update_personalization(self, setting, value):
        """
        Update a personalization setting.
        
        Args:
            setting: Setting name
            value: New setting value
            
        Returns:
            Success message
        """
        try:
            personalization = self.personalization
            personalization[setting] = value
            self.memory_manager.store_preference("personalization", personalization)
            self.personalization = personalization
            
            return f"Personalization setting '{setting}' updated to '{value}'"
        except Exception as e:
            self.logger.error(f"Error updating personalization: {str(e)}")
            return f"Failed to update personalization. Error: {str(e)}"
    
    def get_personalized_response(self, response_type, context=None):
        """
        Get a personalized response based on user preferences.
        
        Args:
            response_type: Type of response (greeting, confirmation, etc.)
            context: Additional context for the response
            
        Returns:
            Personalized response string
        """
        user_name = self.personalization.get("user_name", "User")
        formality = self.personalization.get("formality_level", "casual")
        
        responses = {
            "greeting": {
                "standard": f"Hello {user_name}, how can I help you today?",
                "enthusiastic": f"Hi {user_name}! Great to see you! How can I assist you?",
                "professional": f"Good day, {user_name}. How may I be of assistance?"
            },
            "confirmation": {
                "standard": "I've completed that task.",
                "enthusiastic": "All done! That was successful!",
                "professional": "The requested task has been completed successfully."
            },
            "farewell": {
                "standard": f"Goodbye {user_name}, have a nice day.",
                "enthusiastic": f"Bye {user_name}! It was great helping you today!",
                "professional": f"Farewell, {user_name}. Please don't hesitate to call upon my services again."
            }
        }
        
        greeting_style = self.personalization.get("greeting_style", "standard")
        
        if response_type in responses:
            return responses[response_type].get(greeting_style, responses[response_type]["standard"])
        else:
            return f"I'm here to help you, {user_name}."
    
    def is_authenticated(self):
        """
        Check if the user is currently authenticated.
        
        Returns:
            Boolean indicating authentication status
        """
        # If authentication is not required, always return True
        if not self.security_settings.get("auth_required", True):
            return True
            
        # Check if authenticated within timeout period
        if self.user_authenticated and self.auth_timestamp:
            if time.time() - self.auth_timestamp < self.auth_timeout:
                return True
        
        # Authentication expired or not authenticated
        self.user_authenticated = False
        return False
    
    def logout(self):
        """
        Log out the current user.
        
        Returns:
            Success message
        """
        self.user_authenticated = False
        self.auth_timestamp = None
        return "You have been logged out"
    
    def get_privacy_data(self):
        """
        Get information about stored data and privacy settings.
        
        Returns:
            Dictionary with privacy information
        """
        privacy_level = self.security_settings.get("privacy_level", "standard")
        
        # Get data storage information
        data_info = {
            "conversations": self.memory_manager.get_conversation_count(),
            "preferences": len(self.memory_manager.get_all_preferences()),
            "privacy_level": privacy_level,
            "data_retention": self._get_retention_policy(privacy_level)
        }
        
        return data_info
    
    def _get_retention_policy(self, privacy_level):
        """Get data retention policy based on privacy level"""
        policies = {
            "standard": "Conversations stored for 30 days",
            "high": "Conversations stored for 7 days",
            "paranoid": "Conversations deleted after each session"
        }
        return policies.get(privacy_level, policies["standard"])
    
    def clear_user_data(self, data_type=None):
        """
        Clear user data of specified type.
        
        Args:
            data_type: Type of data to clear (conversations, preferences, all)
            
        Returns:
            Success message
        """
        try:
            if data_type == "conversations" or data_type == "all":
                self.memory_manager.clear_conversations()
                
            if data_type == "preferences" or data_type == "all":
                # Keep security settings but clear other preferences
                security_settings = self.security_settings
                personalization = self.personalization
                self.memory_manager.clear_preferences()
                self.memory_manager.store_preference("security_settings", security_settings)
                self.memory_manager.store_preference("personalization", personalization)
                
            return f"User data ({data_type if data_type else 'all'}) cleared successfully"
        except Exception as e:
            self.logger.error(f"Error clearing user data: {str(e)}")
            return f"Failed to clear user data. Error: {str(e)}"