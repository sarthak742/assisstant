import requests
import logging
import webbrowser
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

class InternetAPIModule:
    """
    Module for handling internet-based functionalities and API integrations.
    Provides web search, weather updates, news, email functionality, and integration with external APIs.
    """
    
    def __init__(self, memory_manager):
        """Initialize the Internet & API Integration Module."""
        self.logger = logging.getLogger("jarvis.internet_api")
        self.memory_manager = memory_manager
        self.api_keys = self._load_api_keys()
        self.user_preferences = self._load_user_preferences()
        
    def _load_api_keys(self):
        """Load API keys from memory manager"""
        try:
            api_keys = self.memory_manager.get_preference("api_keys") or {}
            if not api_keys:
                api_keys = {"weather": "", "news": "", "email": {"username": "", "password": ""}}
                self.memory_manager.store_preference("api_keys", api_keys)
            return api_keys
        except Exception as e:
            self.logger.error(f"Error loading API keys: {str(e)}")
            return {}
            
    def _load_user_preferences(self):
        """Load user preferences for internet services"""
        try:
            preferences = self.memory_manager.get_preference("internet_preferences") or {}
            if not preferences:
                preferences = {
                    "default_search_engine": "google",
                    "weather_location": "auto",
                    "news_topics": ["technology", "world"],
                    "preferred_units": "metric"
                }
                self.memory_manager.store_preference("internet_preferences", preferences)
            return preferences
        except Exception as e:
            self.logger.error(f"Error loading internet preferences: {str(e)}")
            return {}
    
    def web_search(self, query, open_browser=False):
        """Perform a web search using the default search engine."""
        search_engine = self.user_preferences.get("default_search_engine", "google")
        search_urls = {
            "google": f"https://www.google.com/search?q={query.replace(" ", "+")}",
            "bing": f"https://www.bing.com/search?q={query.replace(" ", "+")}",
            "duckduckgo": f"https://duckduckgo.com/?q={query.replace(" ", "+")}"
        }
        
        url = search_urls.get(search_engine, search_urls["google"])
        
        if open_browser:
            try:
                webbrowser.open(url)
                return f"Opening {search_engine} search for \"{query}\""
            except Exception as e:
                self.logger.error(f"Error opening browser: {str(e)}")
                return f"Failed to open browser. Error: {str(e)}"
        else:
            return f"Search URL for \"{query}\": {url}"
    
    def get_weather(self, location=None):
        """Get current weather information for a location."""
        if not location:
            location = self.user_preferences.get("weather_location", "auto")
            
        api_key = self.api_keys.get("weather", "")
        if not api_key:
            return "Weather API key not configured. Please set up your API key."
        
        try:
            units = self.user_preferences.get("preferred_units", "metric")
            url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units={units}"
            
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                temp = data["main"]["temp"]
                condition = data["weather"][0]["description"]
                humidity = data["main"]["humidity"]
                
                unit_symbol = "C" if units == "metric" else "F"
                
                return f"Weather in {data["name"]}: {temp}{unit_symbol}, {condition}, Humidity: {humidity}%"
            else:
                return f"Failed to get weather. Error: {response.status_code}"
        except Exception as e:
            self.logger.error(f"Error getting weather: {str(e)}")
            return f"Failed to get weather information. Error: {str(e)}"
    
    def get_news(self, topic=None, count=5):
        """Get latest news articles."""
        api_key = self.api_keys.get("news", "")
        if not api_key:
            return "News API key not configured. Please set up your API key."
        
        if not topic:
            topics = self.user_preferences.get("news_topics", ["general"])
            topic = topics[0] if topics else "general"
        
        try:
            url = f"https://newsapi.org/v2/top-headlines?category={topic}&apiKey={api_key}&pageSize={count}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get("articles", [])
                
                if not articles:
                    return f"No news articles found for topic: {topic}"
                
                news_summary = f"Top {len(articles)} news for {topic}:\n\n"
                for i, article in enumerate(articles, 1):
                    news_summary += f"{i}. {article["title"]} - {article["source"]["name"]}\n"
                
                return news_summary
            else:
                return f"Failed to get news. Error: {response.status_code}"
        except Exception as e:
            self.logger.error(f"Error getting news: {str(e)}")
            return f"Failed to get news. Error: {str(e)}"
    
    def send_email(self, to_address, subject, body):
        """Send an email using configured email account."""
        email_config = self.api_keys.get("email", {})
        username = email_config.get("username", "")
        password = email_config.get("password", "")
        
        if not username or not password:
            return "Email not configured. Please set up your email credentials."
        
        try:
            msg = MIMEMultipart()
            msg["From"] = username
            msg["To"] = to_address
            msg["Subject"] = subject
            
            msg.attach(MIMEText(body, "plain"))
            
            # Determine SMTP server based on email domain
            if "@gmail.com" in username.lower():
                server = smtplib.SMTP("smtp.gmail.com", 587)
            elif "@outlook.com" in username.lower():
                server = smtplib.SMTP("smtp.office365.com", 587)
            else:
                return "Unsupported email provider. Please use Gmail or Outlook."
            
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
            server.quit()
            
            return f"Email sent successfully to {to_address}"
        except Exception as e:
            self.logger.error(f"Error sending email: {str(e)}")
            return f"Failed to send email. Error: {str(e)}"
    
    def store_api_key(self, service, key, username=None, password=None):
        """Store API key for a service."""
        try:
            api_keys = self.api_keys
            
            if service == "email":
                if not api_keys.get("email"):
                    api_keys["email"] = {}
                api_keys["email"]["username"] = username
                api_keys["email"]["password"] = password
            else:
                api_keys[service] = key
                
            self.memory_manager.store_preference("api_keys", api_keys)
            self.api_keys = api_keys
            
            return f"API key for {service} stored successfully"
        except Exception as e:
            self.logger.error(f"Error storing API key: {str(e)}")
            return f"Failed to store API key. Error: {str(e)}"
