import requests
import logging
import webbrowser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from typing import Dict, Any, Optional, List

class InternetAPIModule:
    """
    Enhanced Internet API Module for Jarvis.
    Provides web search, weather, news, email, and external API functions.
    """

    def __init__(self, memory_manager):
        self.logger = logging.getLogger("jarvis.internet_api")
        self.memory = memory_manager
        self.api_keys = self._load_api_keys()
        self.prefs = self._load_user_prefs()
        self.logger.info("Internet API Module initialized")

    def _load_api_keys(self):
        try:
            keys = self.memory.get_preference("api_keys") or {}
            defaults = {"weather": "", "news": "", "email": {"username": "", "password": ""}}
            for k, v in defaults.items():
                keys.setdefault(k, v)
            self.memory.store_preference("api_keys", keys)
            return keys
        except Exception as e:
            self.logger.error(f"API key load error: {e}")
            return {}

    def _load_user_prefs(self):
        try:
            prefs = self.memory.get_preference("internet_preferences") or {}
            defaults = {
                "default_search_engine": "google",
                "weather_location": "auto",
                "news_topics": ["technology", "world"],
                "preferred_units": "metric"
            }
            for k, v in defaults.items():
                prefs.setdefault(k, v)
            self.memory.store_preference("internet_preferences", prefs)
            return prefs
        except Exception as e:
            self.logger.error(f"Preference load error: {e}")
            return {}

    # ------------------- SEARCH -------------------
    def web_search(self, query: str, open_browser: bool = False) -> str:
        try:
            search_engine = self.prefs.get("default_search_engine", "google").lower()
            search_map = {
                "google": f"https://www.google.com/search?q={query.replace(' ', '+')}",
                "bing": f"https://www.bing.com/search?q={query.replace(' ', '+')}",
                "duckduckgo": f"https://duckduckgo.com/?q={query.replace(' ', '+')}"
            }
            url = search_map.get(search_engine, search_map["google"])
            if open_browser:
                webbrowser.open(url)
                return f"Opening {search_engine} search for '{query}'..."
            return f"Search URL: {url}"
        except Exception as e:
            self.logger.error(f"Search error: {e}")
            return f"Search failed: {e}"

    # ------------------- WEATHER -------------------
    def get_weather(self, location: Optional[str] = None) -> str:
        location = location or self.prefs.get('weather_location', 'auto')
        api_key = self.api_keys.get("weather", "")
        if not api_key:
            return "Weather API key missing. Please configure it first."
        try:
            units = self.prefs.get("preferred_units", "metric")
            url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={api_key}&units={units}"
            r = requests.get(url, timeout=5)
            if r.status_code != 200:
                return f"Weather request failed ({r.status_code})."
            data = r.json()
            return (
                f"Weather in {data['name']}: {data['main']['temp']}°"
                f"{'C' if units == 'metric' else 'F'}, "
                f"{data['weather'][0]['description'].capitalize()}, "
                f"Humidity {data['main']['humidity']}%"
            )
        except Exception as e:
            self.logger.error(f"Weather error: {e}")
            return f"Could not fetch weather: {e}"

    # ------------------- NEWS -------------------
    def get_news(self, topic: Optional[str] = None, count: int = 5) -> str:
        api_key = self.api_keys.get("news", "")
        if not api_key:
            return "News API key missing. Please configure it first."
        topic = topic or self.prefs.get("news_topics", ["general"])[0]
        try:
            url = f"https://newsapi.org/v2/top-headlines?category={topic}&apiKey={api_key}&pageSize={count}"
            r = requests.get(url, timeout=5)
            if r.status_code != 200:
                return f"Failed to get news ({r.status_code})."
            articles = r.json().get("articles", [])
            if not articles:
                return f"No news found for topic: {topic}."
            summary = [f"{i+1}. {a['title']} - {a['source']['name']}" for i, a in enumerate(articles[:count])]
            return f"Top {len(summary)} news in {topic}:\n" + "\n".join(summary)
        except Exception as e:
            self.logger.error(f"News error: {e}")
            return f"Error getting news: {e}"

    # ------------------- EMAIL -------------------
    def send_email(self, to: str, subject: str, body: str) -> str:
        mail_cfg = self.api_keys.get("email", {})
        user, pwd = mail_cfg.get("username", ""), mail_cfg.get("password", "")
        if not user or not pwd:
            return "Email credentials not set."
        try:
            msg = MIMEMultipart()
            msg["From"], msg["To"], msg["Subject"] = user, to, subject
            msg.attach(MIMEText(body, "plain"))

            smtp_server = ("smtp.gmail.com" if "gmail" in user else 
                           "smtp.office365.com" if "outlook" in user else None)
            if not smtp_server:
                return "Unsupported email provider (use Gmail or Outlook)."
            server = smtplib.SMTP(smtp_server, 587)
            server.starttls()
            server.login(user, pwd)
            server.send_message(msg)
            server.quit()
            return f"Email sent successfully to {to}."
        except Exception as e:
            self.logger.error(f"Email error: {e}")
            return f"Failed to send email: {e}"

    # ------------------- UTILS -------------------
    def store_api_key(self, service: str, key: str, username: str = "", password: str = "") -> str:
        try:
            if service == "email":
                self.api_keys["email"].update({"username": username, "password": password})
            else:
                self.api_keys[service] = key
            self.memory.store_preference("api_keys", self.api_keys)
            return f"API key for {service} saved."
        except Exception as e:
            self.logger.error(f"API key store error: {e}")
            return f"Failed to store API key: {e}"
