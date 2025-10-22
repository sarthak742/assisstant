import requests
import logging
import webbrowser
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
from typing import Dict, Any, Optional, List
import openai  # pip install openai


class InternetAPIModule:
    """
    Enhanced Internet API Module for Jarvis AI Assistant
    Handles search, weather, news, email, and reasoning-based summarization.
    """

    def __init__(self, memory_manager):
        self.logger = logging.getLogger("jarvis.internet_api")
        self.memory = memory_manager
        self.api_keys = self._load_api_keys()
        self.prefs = self._load_user_prefs()
        self.logger.info("Internet API Module initialized")

    # ------------------- CONFIG AND INIT -------------------
    def _load_api_keys(self):
        try:
            keys = self.memory.get_preference("api_keys") or {}
            defaults = {
                "weather": "",
                "news": "",
                "openai": "",
                "email": {"username": "", "password": ""}
            }
            for k, v in defaults.items():
                keys.setdefault(k, v)
            self.memory.store_preference("api_keys", keys)
            return keys
        except Exception as e:
            self.logger.error(f"Error loading API keys: {e}")
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
            self.logger.error(f"Error loading internet prefs: {e}")
            return {}

    # ------------------- SEARCH -------------------
    def web_search(self, query: str, open_browser: bool = False) -> str:
        try:
            engine = self.prefs.get("default_search_engine", "google").lower()
            search_map = {
                "google": f"https://www.google.com/search?q={query.replace(' ', '+')}",
                "bing": f"https://www.bing.com/search?q={query.replace(' ', '+')}",
                "duckduckgo": f"https://duckduckgo.com/?q={query.replace(' ', '+')}"
            }
            url = search_map.get(engine, search_map["google"])
            if open_browser:
                webbrowser.open(url)
                return f"Opening {engine} search for '{query}'..."
            return f"Search URL: {url}"
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return f"Error performing search: {e}"

    # ------------------- WEATHER -------------------
    def get_weather(self, location: Optional[str] = None) -> str:
        location = location or self.prefs.get("weather_location", "auto")
        api_key = self.api_keys.get("weather", "")
        if not api_key:
            return "Weather API key not configured."
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
            return f"Failed to retrieve weather: {e}"

    # ------------------- NEWS -------------------
    def get_news(self, topic: Optional[str] = None, count: int = 5) -> str:
        api_key = self.api_keys.get("news", "")
        if not api_key:
            return "News API key missing."
        topic = topic or self.prefs.get("news_topics", ["general"])[0]
        try:
            url = f"https://newsapi.org/v2/top-headlines?category={topic}&apiKey={api_key}&pageSize={count}"
            r = requests.get(url, timeout=5)
            if r.status_code != 200:
                return f"News fetch failed ({r.status_code})."
            articles = r.json().get("articles", [])
            if not articles:
                return f"No recent news found for {topic}."
            summary = [f"{i+1}. {a['title']} - {a['source']['name']}" for i, a in enumerate(articles[:count])]
            return f"Top {len(summary)} {topic} headlines:\n" + "\n".join(summary)
        except Exception as e:
            self.logger.error(f"News retrieval error: {e}")
            return f"Could not fetch news: {e}"

    # ------------------- LLM REASONING: SUMMARIZATION -------------------
    def summarize_news(self, topic: str = "technology", count: int = 5) -> str:
        """
        Fetch latest news and summarize key insights using LLM reasoning.
        Requires: NewsAPI + OpenAI keys.
        """
        news_key = self.api_keys.get("news", "")
        llm_key = self.api_keys.get("openai", "")
        if not news_key or not llm_key:
            return "Missing News or OpenAI API keys."

        try:
            # Step 1: Fetch news articles
            url = f"https://newsapi.org/v2/top-headlines?q={topic}&apiKey={news_key}&pageSize={count}"
            r = requests.get(url, timeout=5)
            if r.status_code != 200:
                return f"News fetch failed ({r.status_code})."
            articles = r.json().get("articles", [])
            if not articles:
                return f"No news found for {topic}."

            content = "\n".join(
                [f"{i+1}. {a['title']} - {a.get('description', '')}" for i, a in enumerate(articles)]
            )

            # Step 2: LLM summarization
            openai.api_key = llm_key
            prompt = (
                f"Summarize the following {count} news items about '{topic}' "
                "into 3-4 concise bullet points with neutral tone.\n\n"
                f"{content}"
            )
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an intelligent Jarvis assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=300
            )
            summary = response.choices[0].message["content"].strip()
            return f"Summary of {topic} news:\n{summary}"

        except Exception as e:
            self.logger.error(f"Summarization error: {e}")
            return f"Failed to summarize news: {e}"

    # ------------------- EMAIL -------------------
    def send_email(self, to: str, subject: str, body: str) -> str:
        email_data = self.api_keys.get("email", {})
        user, pwd = email_data.get("username", ""), email_data.get("password", "")
        if not user or not pwd:
            return "Email not configured. Please set your credentials."
        try:
            msg = MIMEMultipart()
            msg["From"], msg["To"], msg["Subject"] = user, to, subject
            msg.attach(MIMEText(body, "plain"))
            smtp = "smtp.gmail.com" if "gmail" in user else "smtp.office365.com"
            s = smtplib.SMTP(smtp, 587)
            s.starttls()
            s.login(user, pwd)
            s.send_message(msg)
            s.quit()
            return f"Email sent successfully to {to}."
        except Exception as e:
            self.logger.error(f"Email send error: {e}")
            return f"Failed to send email: {e}"

    # ------------------- UTILS -------------------
    def store_api_key(self, service: str, key: str, username: str = "", password: str = "") -> str:
        try:
            if service == "email":
                self.api_keys["email"].update({"username": username, "password": password})
            else:
                self.api_keys[service] = key
            self.memory.store_preference("api_keys", self.api_keys)
            return f"{service} API key stored."
        except Exception as e:
            self.logger.error(f"API storage error: {e}")
            return f"Could not store API key: {e}"
