from google.adk.agents import Agent
from typing import Dict, Any
from datetime import datetime
from zoneinfo import ZoneInfo
import requests
import logging

logging.basicConfig(level=logging.INFO)

# ---------------------------------------------------------
# Geocoding Helper (Supports Any City)
# ---------------------------------------------------------
def get_city_coordinates(city: str) -> Dict[str, Any]:
    """
    Uses Open-Meteo Geocoding API to get any city name
    into latitude, longitude, and timezone.
    """
    try:
        response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1},
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()

        results = data.get("results")
        if not results:
            return {"status": "error", "error_message": "City not found."}

        city_data = results[0]

        return {
            "status": "success",
            "latitude": city_data["latitude"],
            "longitude": city_data["longitude"],
            "timezone": city_data["timezone"],
            "name": city_data["name"],
            "country": city_data.get("country", "")
        }

    except requests.exceptions.RequestException:
        return {"status": "error", "error_message": "Failed to resolve city name."}


# ---------------------------------------------------------
# Weather Function
# ---------------------------------------------------------
def get_weather(city: str) -> Dict[str, Any]:
    """
    Fetch current weather data for a supported city
    using the Open-Meteo public API.
    """
    city = city.strip().lower()
    logging.info(f"Weather tool called for city: {city}")

    location = get_city_coordinates(city)

    if location["status"] == "error":
        return {
            "status": "error",
            "report": None,
            "error_message": location["error_message"]
        }

    try: #api call
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current_weather": True
            },
            timeout=5
        )

        response.raise_for_status()
        data = response.json()
        weather = data.get("current_weather")

        if not weather:
            return {
                "status": "error",
                "report": None,
                "error_message": "Weather API returned no data."
            }

        return {
            "status": "success",
            "report": {
                "temperature_c": weather["temperature"],
                "wind_speed_kmh": weather["windspeed"],
                "weather_code": weather["weathercode"]
            },
            "error_message": None
        }

    except requests.exceptions.RequestException as e:
        logging.error(f"Weather API request failed: {e}")
        return {
            "status": "error",
            "report": None,
            "error_message": "Failed to fetch weather data."
        }


# ---------------------------------------------------------
# Time Function
# ---------------------------------------------------------
def get_current_time(city: str) -> Dict[str, Any]:
    """
    Fetch current local time for a supported city.
    """
    city = city.strip().lower()
    logging.info(f"Time tool called for city: {city}")

    try:
        location = get_city_coordinates(city)

        if location["status"] == "error":
            return {
                "status": "error",
                "report": None,
                "error_message": location["error_message"]
            }

        tz = ZoneInfo(location["timezone"])
        now = datetime.now(tz)

        return {
            "status": "success",
            "report": {
                "local_time": now.strftime("%Y-%m-%d %H:%M:%S"),
                "timezone": location["timezone"]
            },
            "error_message": None
        }

    except Exception as e:
        logging.error(f"Time tool failed: {e}")
        return {
            "status": "error",
            "report": None,
            "error_message": "Failed to fetch time data."
        }


# ---------------------------------------------------------
# Agent Instructions and Definition VERY IMPORTANT
# ---------------------------------------------------------
INSTRUCTION = """
You are a weather and time assistant.

Rules:
- If the user asks about weather, call get_weather.
- If the user asks about current time, call get_current_time.
- Always use tools instead of guessing.
- Don't use the metric sytem and if you need to convert do so.
- If a tool returns an error, explain it clearly to the user.
"""

root_agent = Agent(
    name="weather_time_agent",
    model="gemini-3-flash-preview",
    description="Provides real-time weather and time information for supported cities.",
    instruction=INSTRUCTION,
    tools=[get_weather, get_current_time],
)